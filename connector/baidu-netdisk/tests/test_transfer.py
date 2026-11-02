import asyncio
import hashlib
import json
import logging
import tempfile
import threading
from types import SimpleNamespace

import httpx
import pytest
from connector_sdk import CallResources, FileInput, OAuthAccessCredential
from connector_sdk.client import ClientError
from vendor import Stream

from baidu_netdisk import models as m
from baidu_netdisk import upload as upload_module
from baidu_netdisk.download import download, initial_url, validate_url
from baidu_netdisk.network import thread_call


async def chunks(content):
    for offset in range(0, len(content), 65536):
        yield content[offset:offset + 65536]


async def upload(case, connection, content, *, size=None, **params):
    return await case.sdk.invoke_file_input(
        "upload_file", params, FileInput(file_name="上传.txt", content=chunks(content),
                                         size_bytes=size), max_file_bytes=m.MAX_FILE_BYTES,
        **case.invocation(connection, "upload_file"))


@pytest.mark.parametrize("missing", [[1], [2, 0], [], [0, 1, 2]])
async def test_partial_reuse_upload_and_full_ordered_merge(case, missing):
    connection = await case.connect()
    case.vendor.missing = missing
    content = b"a" * m.PART_BYTES + b"b" * m.PART_BYTES + b"c"
    reply = await upload(case, connection, content, size=len(content), destination_path="/目标")
    assert reply.status == "succeeded", reply
    assert [i for i, _ in case.vendor.parts] == missing
    hashes = [hashlib.md5(content[i:i + m.PART_BYTES]).hexdigest()
              for i in range(0, len(content), m.PART_BYTES)]
    assert json.loads(case.vendor.creates[-1]["block_list"]) == hashes
    assert reply.data == {"external_resource_id": "125", "file_name": "上传.txt",
                          "size_bytes": len(content), "provider_path": "/目标/上传.txt"}


async def test_rapid_upload_never_fabricates_id(case):
    connection = await case.connect()
    case.vendor.rapid = True
    reply = await upload(case, connection, b"abc")
    assert reply.status == "succeeded" and reply.data["external_resource_id"] is None
    assert not case.vendor.parts and not case.vendor.creates


@pytest.mark.parametrize("missing", [[-1], [True], [1], [0, 0], "0"])
async def test_bad_missing_list_never_uploads_or_merges(case, missing):
    connection = await case.connect()
    case.vendor.missing = missing
    reply = await upload(case, connection, b"abc")
    assert reply.status == "uncertain" and not case.vendor.parts and not case.vendor.creates


@pytest.mark.parametrize("content,size", [(b"", 0), (b"abc", 4), (b"abcd", 3)])
async def test_bad_input_never_starts_remote_upload(case, content, size):
    connection = await case.connect()
    before = len(case.vendor.calls)
    reply = await upload(case, connection, content, size=size)
    assert reply.status != "succeeded" and len(case.vendor.calls) == before


async def test_application_counts_unknown_size_and_rejects_limit_before_precreate(
    case, monkeypatch,
):
    connection = await case.connect()
    monkeypatch.setattr(m, "MAX_FILE_BYTES", 2)
    before = len(case.vendor.calls)
    reply = await upload(case, connection, b"abc")
    assert reply.status == "failed" and len(case.vendor.calls) == before


@pytest.mark.parametrize("phase", ["part", "merge"])
async def test_upload_response_loss_never_retries(case, phase):
    connection = await case.connect()

    async def inject(request):
        is_part = request.url.path.endswith("superfile2")
        is_merge = request.url.params.get("method") == "create"
        if (phase == "part" and is_part) or (phase == "merge" and is_merge):
            raise httpx.ReadError("private-upload-secret")

    case.vendor.inject = inject
    reply = await upload(case, connection, b"abc")
    assert reply.status == "uncertain" and "private-upload-secret" not in repr(reply)
    targets = [r for r in case.vendor.calls if (r.url.path.endswith("superfile2") if phase == "part"
               else r.url.params.get("method") == "create")]
    assert len(targets) == 1


async def test_checksum_failure_stops_merge(case):
    connection = await case.connect()

    async def inject(request):
        if request.url.path.endswith("superfile2"):
            return httpx.Response(200, json={"md5": "0" * 32})

    case.vendor.inject = inject
    reply = await upload(case, connection, b"abc")
    assert reply.status == "uncertain" and not case.vendor.creates


async def test_download_actual_bytes_metadata_and_close(case):
    connection = await case.connect()

    async def consume(response):
        assert response.external_resource_id == "123"
        assert response.file.file_name == "测试.txt" and response.file.size_bytes == 3
        return b"".join([part async for part in response.file.content])

    reply = await case.sdk.invoke_file_output(
        "download_file", {"fs_id": "123"}, consume=consume, max_file_bytes=m.MAX_FILE_BYTES,
        **case.invocation(connection, "download_file"))
    assert reply.status == "succeeded" and reply.data == b"abc"
    assert all(stream.closed == 1 for stream in case.vendor.streams)


@pytest.mark.parametrize("target", [
    "http://pan.baidu.com/f", "https://127.0.0.1/f", "https://pan.baidu.com.evil.test/f",
    "https://pan.baidu.com:444/f", "https://u@pan.baidu.com/f",
    "https://pan.baidu.com/f#fragment", "https://pan.baidu.com\\@evil.test/f",
])
def test_untrusted_download_target_rejected(target):
    with pytest.raises(ValueError, match="baidu_download_target_invalid"):
        validate_url(target)


def test_official_pcs_initial_link_receives_token():
    target = initial_url("https://d.pcs.baidu.com/file/a?access_token=stale&sign=s", "access-1")
    assert dict(httpx.URL(target).params) == {"access_token": "access-1", "sign": "s"}


async def test_cleanup_failure_preserves_primary_staging_rejection(case, monkeypatch, caplog):
    await case.connect()

    class BrokenClose:
        closed = False

        def close(self):
            raise OSError("private-close-message")

    monkeypatch.setattr(upload_module.tempfile, "TemporaryFile", lambda **_: BrokenClose())
    resources = CallResources(asyncio.get_running_loop().time() + 2)
    ctx = SimpleNamespace(resources=resources, deadline=resources.deadline)
    from connector_sdk import OperationRejected

    with pytest.raises(OperationRejected):
        await upload_module.upload(ctx, m.Upload(), FileInput(file_name="a", content=chunks(b"")),
                                   asyncio.Semaphore(1))
    assert "baidu_staging_cleanup_failed" in caplog.text
    assert "private-close-message" not in caplog.text
    with pytest.raises(OSError):
        await resources.close()


@pytest.mark.parametrize("mode", ["redirect", "too_many", "short", "long", "length", "encoding"])
async def test_download_rejects_unsafe_or_incomplete_response(case, mode):
    connection = await case.connect()
    stream = Stream([b"ab" if mode == "short" else b"abcd"])

    async def inject(request):
        if request.url.host != "cdn.baidupcs.com":
            return None
        if mode == "redirect":
            return httpx.Response(302, headers={"location": "https://evil.test/private"})
        if mode == "too_many":
            return httpx.Response(302, headers={"location": "/loop"})
        if mode == "length":
            return httpx.Response(200, stream=stream, headers={"content-length": "4"})
        if mode == "encoding":
            return httpx.Response(200, headers={"content-encoding": "gzip"}, content=b"bad-gzip")
        return httpx.Response(200, stream=stream)

    async def consume(response):
        return b"".join([part async for part in response.file.content])

    case.vendor.inject = inject
    try:
        reply = await case.sdk.invoke_file_output(
            "download_file", {"fs_id": "123"}, consume=consume, max_file_bytes=m.MAX_FILE_BYTES,
            **case.invocation(connection, "download_file"))
        assert reply.status == "failed"
    except ClientError as error:
        # Once output bytes have started, incomplete framing is rejected by the client.
        assert mode in ("short", "long") and error.code == "client_response_invalid"
    assert not any(r.url.host == "evil.test" for r in case.vendor.calls)
    if mode in ("short", "long", "length"):
        assert stream.closed == 1


async def direct_download(case):
    await case.connect()
    resources = CallResources(asyncio.get_running_loop().time() + 3,
                              OAuthAccessCredential(access_token="access-1"))

    class Service:
        async def request(self, *args, consume, **kwargs):
            # Public response adapter for direct application lifecycle verification.
            request = httpx.Request(args[0], "https://pan.baidu.com/" + args[1],
                                    params=kwargs["params"] | {"access_token": "access-1"})
            response = await case.vendor(request)

            class Response:
                status_code = response.status_code

                async def read(self):
                    return response.content

            return await consume(Response())

    ctx = SimpleNamespace(deadline=resources.deadline, resources=resources,
                           credential=resources.credential, http=lambda _: Service())
    return await download(ctx, "123"), resources


async def test_unconsumed_download_is_owned_by_public_resources(case):
    output, resources = await direct_download(case)
    assert output.size_bytes == 3 and case.vendor.streams[-1].closed == 0
    await resources.close()
    assert case.vendor.streams[-1].closed == 1


async def test_started_download_can_close_from_cleanup_task(case):
    output, resources = await direct_download(case)
    try:
        assert await anext(output.content) == b"a"
        await asyncio.create_task(output.content.aclose())
    finally:
        await resources.close()
    assert case.vendor.streams[-1].closed == 1


async def test_thread_cancel_waits_before_file_can_close():
    entered, release, completed = threading.Event(), threading.Event(), threading.Event()

    def write():
        entered.set()
        release.wait(timeout=3)
        completed.set()

    task = asyncio.create_task(thread_call(write))
    try:
        async with asyncio.timeout(2):
            while not entered.is_set():
                await asyncio.sleep(0.001)
        task.cancel()
        await asyncio.sleep(0)
        task.cancel()
        await asyncio.sleep(0)
        assert not task.done() and not completed.is_set()
    finally:
        release.set()
        with pytest.raises(asyncio.CancelledError):
            await task
    assert completed.is_set()


async def test_staging_cancel_cleans_file_and_releases_upload_slot(case, monkeypatch):
    connection = await case.connect()
    staged_files = []
    original = tempfile.TemporaryFile

    def temporary(*args, **kwargs):
        staged = original(*args, **kwargs)
        staged_files.append(staged)
        return staged

    monkeypatch.setattr(upload_module.tempfile, "TemporaryFile", temporary)
    entered = asyncio.Event()

    async def blocked():
        yield b"abc"
        entered.set()
        await asyncio.Event().wait()

    file = FileInput(file_name="cancel.txt", content=blocked())
    resources = CallResources(asyncio.get_running_loop().time() + 3,
                              OAuthAccessCredential(access_token="access-1"))
    ctx = SimpleNamespace(resources=resources, deadline=resources.deadline)
    gate = asyncio.Semaphore(1)
    task = asyncio.create_task(upload_module.upload(ctx, m.Upload(), file, gate))
    try:
        await asyncio.wait_for(entered.wait(), 2)
        task.cancel()
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        await resources.close()
    assert staged_files and all(f.closed for f in staged_files)
    assert not case.vendor.pending
    await asyncio.wait_for(gate.acquire(), 0.5)
    gate.release()
    assert (await upload(case, connection, b"next")).status == "succeeded"


async def test_custom_transport_debug_logs_redact_query_secrets(case, caplog):
    caplog.set_level(logging.DEBUG)
    connection = await case.connect()
    assert (await upload(case, connection, b"abc")).status == "succeeded"
    for secret in ("access-1", "refresh-1", "test-secret", "test-code"):
        assert secret not in caplog.text


async def test_upload_queue_uses_original_deadline_before_staging(case, monkeypatch):
    await case.connect()
    staged_files = []
    original = tempfile.TemporaryFile

    def temporary(**kwargs):
        staged = original(**kwargs)
        staged_files.append(staged)
        return staged

    monkeypatch.setattr(upload_module.tempfile, "TemporaryFile", temporary)
    gate, entered, second_read = asyncio.Semaphore(1), asyncio.Event(), asyncio.Event()
    first_resources = CallResources(asyncio.get_running_loop().time() + 3)
    second_resources = CallResources(asyncio.get_running_loop().time() + 0.04)

    async def first():
        entered.set()
        await asyncio.Event().wait()
        yield b"first"

    async def second():
        second_read.set()
        yield b"second"

    ctx = SimpleNamespace(resources=first_resources, deadline=first_resources.deadline)
    task = asyncio.create_task(upload_module.upload(
        ctx, m.Upload(), FileInput(file_name="a", content=first()), gate))
    try:
        await asyncio.wait_for(entered.wait(), 1)
        ctx = SimpleNamespace(resources=second_resources, deadline=second_resources.deadline)
        with pytest.raises(TimeoutError):
            await upload_module.upload(ctx, m.Upload(), FileInput(file_name="b", content=second()),
                                       gate)
        assert len(staged_files) == 1 and not second_read.is_set()
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        await first_resources.close()
        await second_resources.close()
    assert all(file.closed for file in staged_files)
