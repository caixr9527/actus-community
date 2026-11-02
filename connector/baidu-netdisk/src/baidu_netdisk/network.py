"""Optional HTTPX path for multipart/CDN traffic, owned by this application."""

import asyncio
import logging
from contextlib import contextmanager
from contextvars import ContextVar

import httpx

from .api import decode

USER_AGENT = "pan.baidu.com actus-baidu-netdisk/0.1.0"
_active = ContextVar("baidu_netdisk_network", default=False)


class _Quiet(logging.Filter):
    def filter(self, record):
        return not _active.get()


_filter = _Quiet()


@contextmanager
def quiet():
    # HTTPX emits full query URLs; suppress only this app's transport context.
    for logger in ("httpx", "httpcore.connection", "httpcore.http11", "httpcore.http2",
                   "httpcore.proxy", "httpcore.socks"):
        logging.getLogger(logger).addFilter(_filter)
    token = _active.set(True)
    try:
        yield
    finally:
        _active.reset(token)


async def client(ctx):
    remaining = ctx.deadline - asyncio.get_running_loop().time()
    if remaining <= 0:
        raise TimeoutError("baidu_deadline_exceeded")
    with quiet():
        return await ctx.resources.enter_async_context(httpx.AsyncClient(
            timeout=min(20, remaining), follow_redirects=False, trust_env=False,
            transport=httpx.AsyncHTTPTransport(retries=0, trust_env=False),
            headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity"}))


async def multipart(ctx, session, params, filename, part):
    token = ctx.credential().access_token.get_secret_value()
    try:
        with quiet():
            async with asyncio.timeout_at(ctx.deadline), session.stream(
                "POST", "https://d.pcs.baidu.com/rest/2.0/pcs/superfile2",
                params=params | {"access_token": token},
                files={"file": (filename, part, "application/octet-stream")},
            ) as response:
                content = bytearray()
                async for chunk in response.aiter_bytes():
                    content.extend(chunk)
                    if len(content) > 1024 * 1024:
                        raise ValueError("baidu_response_too_large")
                return decode(bytes(content), response.status_code, require_errno=False)
    except httpx.HTTPError:
        raise ValueError("baidu_upload_transport_failed") from None


async def thread_call(fn, *args):
    """Wait for our thread before propagating cancellation and closing its file."""
    task = asyncio.create_task(asyncio.to_thread(fn, *args))
    cancelled = False
    while not task.done():
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            cancelled = True
        except Exception:
            break
    if cancelled:
        # Preserve cancellation; surface a cleanup failure without exposing file data.
        if not task.cancelled() and task.exception() is not None:
            logging.getLogger(__name__).error("baidu_staging_io_failed_during_cancel")
        raise asyncio.CancelledError
    return task.result()
