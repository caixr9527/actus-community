import asyncio
import json

import httpx
import pytest
from connector_sdk import OperationRejected
from test_runtime import connect

from notion_connector.mcp import payload
from notion_connector.schema import arguments, validate


class Stream(httpx.AsyncByteStream):
    def __init__(self, content, *, pause=False):
        self.content, self.pause = content, pause
        self.closed = False
        self.entered = asyncio.Event()

    async def __aiter__(self):
        for byte in self.content:
            yield bytes([byte])
        self.entered.set()
        if self.pause:
            await asyncio.Event().wait()

    async def aclose(self):
        self.closed = True


@pytest.mark.parametrize("separator", ["\n", "\r\n", "\r"])
async def test_incremental_sse_utf8_multiline_notifications_and_close(case, separator):
    connection = await connect(case)
    streams = []

    async def inject(body, request):
        if body.get("params", {}).get("name") != "notion-search":
            return
        message = {"jsonrpc": "2.0", "id": body["id"],
                   "result": {"structuredContent": {"name": "中文"}}}
        data = json.dumps(message, ensure_ascii=False).replace(', "result":', ',\n"result":')
        notification = 'data: {"jsonrpc":"2.0","method":"notifications/progress"}'
        text = ("\ufeff:keepalive" + separator + notification + separator * 2
                + separator.join("data: " + part for part in data.split("\n")) + separator * 2)
        stream = Stream(text.encode(), pause=True)
        streams.append(stream)
        return httpx.Response(200, headers={"content-type": "text/event-stream"}, stream=stream)

    case.vendor.inject = inject
    result = await case.invoke(connection, "search", {"query": "Q"})
    assert result.status == "succeeded" and result.data["data"]["name"] == "中文"
    assert streams[0].closed


@pytest.mark.parametrize("variant", ["partial", "wrong_id", "error", "invalid_utf8"])
async def test_sse_failure_after_write_is_failed_and_never_retried(case, variant):
    connection = await connect(case)
    streams = []

    async def inject(body, request):
        if body.get("params", {}).get("name") != "notion-create-pages":
            return
        message = {"jsonrpc": "2.0", "id": body["id"],
                   "result": {"structuredContent": {"task_id": "original-task"}}}
        if variant == "wrong_id":
            message["id"] += 1
        if variant == "error":
            message["result"] = {"isError": True}
        content = b"data: " + json.dumps(message).encode()
        content += b"\n" if variant == "partial" else b"\n\n"
        if variant == "invalid_utf8":
            content = b"data: \xff\n\n"
        stream = Stream(content)
        streams.append(stream)
        return httpx.Response(200, headers={"content-type": "text/event-stream"}, stream=stream)

    case.vendor.inject = inject
    result = await case.invoke(connection, "create_page", {"parent_id": "p", "title": "T"})
    assert result.status == "uncertain"
    assert streams[0].closed and len(streams) == 1


async def test_cancelled_write_releases_stream_without_retry(case):
    connection = await connect(case)
    stream = Stream(b":waiting\n\n", pause=True)

    async def inject(body, request):
        if body.get("params", {}).get("name") == "notion-create-pages":
            return httpx.Response(200, headers={"content-type": "text/event-stream"}, stream=stream)

    case.vendor.inject = inject
    task = asyncio.create_task(
        case.invoke(connection, "create_page", {"parent_id": "p", "title": "T"}))
    await asyncio.wait_for(stream.entered.wait(), 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert stream.closed
    assert sum(c.get("params", {}).get("name") == "notion-create-pages"
               for c in case.vendor.calls) == 1


@pytest.mark.parametrize("schema,value", [
    ({"type": "integer"}, True), ({"type": "string", "minLength": 3}, "a"),
    ({"type": "object", "additionalProperties": False}, {"extra": 1}),
    ({"type": "string", "pattern": ".*"}, "x"), ({"$ref": "https://other.test"}, {}),
    ({"oneOf": [{"type": "string"}, {"type": "string"}]}, "ambiguous"),
    ({"oneOf": [{"type": "string"}, {"type": "string", "pattern": ".*"}]}, "ambiguous"),
    ({"enum": [1]}, True),
])
def test_remote_schema_validation_fails_closed(schema, value):
    with pytest.raises(OperationRejected):
        validate(value, schema)


def test_both_view_shapes_and_local_ref():
    item = {"type": "object", "required": ["mode", "view_url"],
            "properties": {"mode": {"const": "view"}, "view_url": {"type": "string"}},
            "additionalProperties": False}
    schema = {"type": "object", "$defs": {"view": item}, "required": ["data"],
              "properties": {"data": {"$ref": "#/$defs/view"}}}
    assert arguments("query_database_view", {"view_url": "v"}, schema) == {
        "data": {"mode": "view", "view_url": "v"}}
    assert arguments("query_database_view", {"view_url": "v"}, item)["mode"] == "view"


def test_structured_json_markdown_and_async_status_preserved():
    assert payload({"structuredContent": {"task_id": "original", "status": "pending"}}).data == {
        "task_id": "original", "status": "pending"}
    assert payload({"content": [{"type": "text", "text": "[1,2]"}]}).data == {"value": [1, 2]}
    assert payload({"content": [{"type": "text", "text": "# Markdown"}]}).data == {
        "text": "# Markdown"}


@pytest.mark.parametrize("stage", ["initialize", "tools/list", "tools/call"])
async def test_confirmed_dispatch_rejection_and_preflight_failure_are_not_uncertain(case, stage):
    connection = await connect(case)

    async def inject(body, request):
        if body["method"] != stage:
            return
        if stage == "tools/call":
            return httpx.Response(200, json={"jsonrpc": "2.0", "id": body["id"],
                                             "error": {"code": -32602, "message": "private"}})
        return httpx.Response(503)

    case.vendor.inject = inject
    reply = await case.invoke(connection, "create_page", {"parent_id": "p", "title": "T"})
    assert reply.status == "failed" and reply.error.code == "operation_failed"


async def test_schema_and_access_not_cached_across_calls(case):
    connection = await connect(case)
    assert (await case.invoke(connection, "search", {"query": "Q"})).status == "succeeded"
    case.vendor.tools["notion-search"] = {
        "type": "object", "properties": {"query": {"type": "integer"}}, "required": ["query"]}
    before = len(case.vendor.calls)
    assert (await case.invoke(connection, "search", {"query": "Q"})).status == "failed"
    assert not any(c.get("params", {}).get("name") == "notion-search"
                   for c in case.vendor.calls[before:])


@pytest.mark.parametrize("name,params", [
    ("duplicate_page", {"page_id": "p"}),
    ("create_page", {"parent_id": "p", "title": "T", "allow_async": True}),
    ("update_page", {"page_id": "p", "content": "T", "allow_async": True}),
])
async def test_incompatible_polling_contract_blocks_async_writes(case, name, params):
    connection = await connect(case)
    case.vendor.tools["notion-get-async-task"] = {
        "type": "object", "required": ["sql"], "properties": {"sql": {"type": "string"}}}
    before = len(case.vendor.calls)
    result = await case.invoke(connection, name, params)
    assert result.status == "failed" and result.error.code == "operation_failed"
    assert not any(c["method"] == "tools/call" for c in case.vendor.calls[before:])


async def test_malformed_schema_cannot_make_an_unsent_write_uncertain(case):
    connection = await connect(case)
    case.vendor.tools["notion-create-pages"] = {"type": [["object"]]}
    before = len(case.vendor.calls)
    result = await case.invoke(connection, "create_page", {"parent_id": "p", "title": "T"})
    assert result.status == "failed" and result.error.code == "operation_failed"
    assert not any(c["method"] == "tools/call" for c in case.vendor.calls[before:])
