"""Application-owned staging and Baidu multipart protocol; no automatic write retry."""

import asyncio
import hashlib
import json
import logging
import sys
import tempfile

from connector_sdk import OperationRejected

from . import models as m
from .api import integer, request
from .network import client, multipart, thread_call


async def stage(staged, file):
    total, part_size = 0, 0
    digest = hashlib.md5(usedforsecurity=False)
    hashes = []
    async for chunk in file.content:
        if type(chunk) is not bytes:
            raise OperationRejected()
        total += len(chunk)
        if total > m.MAX_FILE_BYTES or (file.size_bytes is not None and total > file.size_bytes):
            raise OperationRejected()
        await thread_call(staged.write, chunk)
        view = memoryview(chunk)
        offset = 0
        while offset < len(view):
            count = min(m.PART_BYTES - part_size, len(view) - offset)
            digest.update(view[offset:offset + count])
            offset += count
            part_size += count
            if part_size == m.PART_BYTES:
                hashes.append(digest.hexdigest())
                digest, part_size = hashlib.md5(usedforsecurity=False), 0
    if not total or (file.size_bytes is not None and total != file.size_bytes):
        raise OperationRejected()
    if part_size:
        hashes.append(digest.hexdigest())
    await thread_call(staged.flush)
    return total, hashes


def read_part(staged, index):
    staged.seek(index * m.PART_BYTES)
    return staged.read(m.PART_BYTES)


def result(data, remote_path, size, *, rapid=False):
    # A rapid response may omit fs_id. Never invent one from the requested path.
    identifier = data.get("fs_id")
    if identifier is None and not rapid:
        raise ValueError("baidu_upload_response_invalid")
    if identifier is not None:
        identifier = m.FileID(fs_id=str(integer(identifier, positive=True))).fs_id
    returned_path = data.get("path", remote_path if rapid else None)
    returned_size = data.get("size", size if rapid else None)
    if returned_path != remote_path or type(returned_size) is not int or returned_size != size:
        raise ValueError("baidu_upload_response_invalid")
    return m.Uploaded(external_resource_id=identifier,
                      file_name=remote_path.rsplit("/", 1)[1],
                      size_bytes=size, provider_path=remote_path)


async def upload(ctx, params, file, gate):
    try:
        filename = m.name(file.file_name)
    except ValueError:
        raise OperationRejected() from None
    if file.size_bytes is not None and not 0 < file.size_bytes <= m.MAX_FILE_BYTES:
        raise OperationRejected()
    remote_path = params.destination_path.rstrip("/") + "/" + filename
    if len(remote_path) > 2048:
        raise OperationRejected()
    async with asyncio.timeout_at(ctx.deadline), gate:
        staged = tempfile.TemporaryFile(mode="w+b")

        async def close():
            if not staged.closed:
                await thread_call(staged.close)

        ctx.resources.callback(close)
        try:
            size, hashes = await stage(staged, file)
            fields = {"path": remote_path, "size": str(size), "isdir": "0", "rtype": "0",
                      "block_list": json.dumps(hashes, separators=(",", ":"))}
            precreated = await request(ctx, "POST", "rest/2.0/xpan/file", {"method": "precreate"},
                                       data=fields | {"autoinit": "1"})
            kind = integer(precreated.get("return_type"))
            if kind == 2:
                return result(precreated, remote_path, size, rapid=True)
            upload_id, missing = precreated.get("uploadid"), precreated.get("block_list")
            if (kind != 1 or type(upload_id) is not str or not upload_id or len(upload_id) > 1024
                    or type(missing) is not list or len(missing) > len(hashes)):
                raise ValueError("baidu_precreate_response_invalid")
            m.text(upload_id)
            seen = set()
            for index in missing:
                if type(index) is not int or not 0 <= index < len(hashes) or index in seen:
                    raise ValueError("baidu_precreate_response_invalid")
                seen.add(index)
            if missing:
                session = await client(ctx)
                for index in missing:
                    part = await thread_call(read_part, staged, index)
                    if not part:
                        raise ValueError("baidu_staged_part_missing")
                    response = await multipart(ctx, session, {
                        "method": "upload", "type": "tmpfile", "path": remote_path,
                        "uploadid": upload_id, "partseq": str(index)}, filename, part)
                    if (type(response.get("md5")) is not str
                            or response["md5"].lower() != hashes[index]):
                        raise ValueError("baidu_part_checksum_mismatch")
            created = await request(ctx, "POST", "rest/2.0/xpan/file", {"method": "create"},
                                    data=fields | {"uploadid": upload_id})
            return result(created, remote_path, size)
        finally:
            primary = sys.exception()
            try:
                await close()
            except Exception:
                logging.getLogger(__name__).error("baidu_staging_cleanup_failed")
                if primary is None:
                    raise ValueError("baidu_staging_cleanup_failed") from None
                primary.add_note("baidu_staging_cleanup_failed")
