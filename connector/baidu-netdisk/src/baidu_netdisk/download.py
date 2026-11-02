"""Baidu download policy and stream ownership, independent of SDK HTTP helpers."""

import asyncio
import mimetypes
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

import httpx
from connector_sdk import FileOutput

from . import models as m
from .api import metadata
from .network import client, quiet


def validate_url(url):
    try:
        if type(url) is not str or len(url) > 16384 or any(ord(c) <= 32 for c in url):
            raise ValueError
        parsed = urlsplit(url)
        host = (parsed.hostname or "").lower()
        allowed = (host in {"pan.baidu.com", "d.pcs.baidu.com", "pcs.baidu.com"}
                   or host.endswith(".baidupcs.com"))
        if (parsed.scheme != "https" or not allowed or parsed.username is not None
                or parsed.password is not None or parsed.port not in (None, 443)
                or parsed.fragment or "\\" in url):
            raise ValueError
        return url
    except ValueError:
        raise ValueError("baidu_download_target_invalid") from None


def initial_url(url, token):
    validate_url(url)
    parsed = urlsplit(url)
    values = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True)
              if k != "access_token"]
    # Official metadata may return a PCS link requiring a token on the first request.
    # The target has already passed the Baidu-only policy; redirects never re-inject it.
    values.append(("access_token", token))
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(values), ""))


def redirect_url(current, location):
    target = validate_url(urljoin(current, location))
    before, after = urlsplit(current), urlsplit(target)
    if before.hostname != after.hostname:
        query = [(k, v) for k, v in parse_qsl(after.query, keep_blank_values=True)
                 if k != "access_token"]
        target = urlunsplit((after.scheme, after.netloc, after.path, urlencode(query), ""))
    return target


async def download(ctx, fs_id):
    record, link = await metadata(ctx, fs_id, download=True)
    if (record.is_directory is not False or record.size_bytes is None
            or record.size_bytes > m.MAX_FILE_BYTES):
        raise ValueError("baidu_download_metadata_invalid")
    target = initial_url(link, ctx.credential().access_token.get_secret_value())
    session = await client(ctx)
    try:
        for redirects in range(6):
            with quiet():
                async with asyncio.timeout_at(ctx.deadline):
                    response = await ctx.resources.enter_async_context(session.stream(
                        "GET", validate_url(target),
                        headers={"Accept": "application/octet-stream"}))
            if response.status_code in (301, 302, 303, 307, 308):
                location = response.headers.get("location")
                with quiet():
                    await response.aclose()
                if not location or redirects == 5:
                    raise ValueError("baidu_download_redirect_invalid")
                target = redirect_url(target, location)
                continue
            if response.status_code != 200 or response.headers.get("content-encoding", "identity") \
                    not in ("identity", ""):
                raise ValueError("baidu_download_response_invalid")
            length = response.headers.get("content-length")
            if length is not None and (not length.isascii() or not length.isdigit()
                                       or int(length) != record.size_bytes):
                raise ValueError("baidu_download_size_mismatch")
            break
        else:
            raise ValueError("baidu_download_redirect_invalid")
    except httpx.HTTPError:
        raise ValueError("baidu_download_transport_failed") from None

    async def content():
        total = 0
        iterator = response.aiter_bytes()
        try:
            while True:
                # Do not carry task-local contexts or timeout managers across yield:
                # the SDK may close this generator from a different cleanup task.
                with quiet():
                    async with asyncio.timeout_at(ctx.deadline):
                        chunk = await anext(iterator, None)
                if asyncio.get_running_loop().time() >= ctx.deadline:
                    raise TimeoutError("baidu_deadline_exceeded")
                if chunk is None:
                    if total != record.size_bytes:
                        raise ValueError("baidu_download_size_mismatch")
                    return
                total += len(chunk)
                if total > record.size_bytes or total > m.MAX_FILE_BYTES:
                    raise ValueError("baidu_download_size_mismatch")
                yield chunk
        except httpx.HTTPError:
            raise ValueError("baidu_download_transport_failed") from None
        finally:
            with quiet():
                await iterator.aclose()

    # The response/client are already in ctx.resources even if content is never iterated.
    return FileOutput(file_name=record.name, size_bytes=record.size_bytes,
                      mime_type=mimetypes.guess_type(record.name)[0],
                      external_resource_id=record.fs_id, content=content())
