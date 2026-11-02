"""Read-only redirect adapter; uses public credentials/resources, never SDK internals."""

import asyncio
import logging
from contextlib import contextmanager
from contextvars import ContextVar

import httpx
from connector_sdk import HttpError

from .api import HEADERS, ORIGIN, related, url

_active = ContextVar("github_redirect_transport", default=False)


class Quiet(logging.Filter):
    def filter(self, record):
        return not _active.get()


_filter = Quiet()


@contextmanager
def quiet():
    for name in (
        "httpx",
        "httpcore.connection",
        "httpcore.http11",
        "httpcore.http2",
        "httpcore.proxy",
        "httpcore.socks",
    ):
        logging.getLogger(name).addFilter(_filter)
    token = _active.set(True)
    try:
        yield
    finally:
        _active.reset(token)


class Response:
    def __init__(self, response):
        self.response = response
        self.headers, self.status_code = response.headers, response.status_code

    async def read(self):
        length = self.headers.get("content-length")
        if length is not None and (
            not length.isascii() or not length.isdigit() or int(length) > 1024 * 1024
        ):
            raise HttpError("github_invalid_length")
        data = bytearray()
        async for chunk in self.response.aiter_bytes():
            data.extend(chunk)
            if len(data) > 1024 * 1024:
                raise HttpError("github_response_too_large")
        if length is not None and len(data) != int(length):
            raise HttpError("github_invalid_length")
        return bytes(data)


async def redirected_get(ctx, route, query, consume):
    remaining = ctx.deadline - asyncio.get_running_loop().time()
    if remaining <= 0:
        raise HttpError("github_deadline_exceeded")
    credential = ctx.credential().access_token.get_secret_value()
    try:
        with quiet():
            session = await ctx.resources.enter_async_context(
                httpx.AsyncClient(
                    timeout=min(20, remaining),
                    follow_redirects=False,
                    trust_env=False,
                    transport=httpx.AsyncHTTPTransport(retries=0, trust_env=False),
                    headers=HEADERS
                    | {"Authorization": "Bearer " + credential, "Accept-Encoding": "identity"},
                )
            )
            async with asyncio.timeout_at(ctx.deadline):
                for index in range(4):
                    async with session.stream("GET", ORIGIN + route, params=query) as response:
                        if response.status_code in (301, 302, 303, 307, 308):
                            if index == 3:
                                raise HttpError("github_redirect_limit")
                            target = url(response.headers.get("location"))
                            next_route = target.path.removeprefix("/")
                            if not related(route, next_route) or target.query:
                                raise HttpError("github_invalid_redirect")
                            route = next_route
                            continue
                        if response.headers.get("content-encoding", "identity") != "identity":
                            raise HttpError("github_invalid_encoding")
                        status, data, headers = await consume(Response(response))
                        return status, data, headers, route
    except httpx.HTTPError:
        raise HttpError("github_redirect_transport_failed") from None
    raise HttpError("github_redirect_limit")
