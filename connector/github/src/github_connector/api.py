"""Fixed API origin, bounded read redirects, safe failures and Link pagination."""

import asyncio
import json
import math
import re
import time
from contextvars import ContextVar
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from urllib.parse import parse_qsl, urlsplit

from connector_sdk import HttpError, OperationRejected

from .models import Result

ORIGIN = "https://api.github.com/"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2026-03-10",
    "User-Agent": "actus-github/0.1.0",
}
_schedule = ContextVar("github_schedule", default=None)


class Scheduler:
    def __init__(self):
        self.gate = asyncio.Lock()
        self.cooldowns = {}
        self.writes = {}


async def execute(scheduler, ctx, callback, params):
    key = ctx.connection.connection_id
    async with asyncio.timeout_at(ctx.deadline), scheduler.gate:
        now = time.monotonic()
        scheduler.cooldowns = {k: v for k, v in scheduler.cooldowns.items() if v > now}
        scheduler.writes = {k: v for k, v in scheduler.writes.items() if v + 1 > now}
        if key in scheduler.cooldowns:
            # No business request has been sent by this invocation.
            if ctx.operation_name in {"create_issue", "update_issue", "create_issue_comment"}:
                raise OperationRejected()
            raise HttpError("github_rate_limited")
        bound = _schedule.set((scheduler, key))
        try:
            return await callback(ctx, params)
        finally:
            _schedule.reset(bound)


def cooldown(headers, limited):
    bound = _schedule.get()
    if bound is None:
        return
    seconds = 60.0 if limited else 0.0
    raw = headers.get("retry-after")
    if raw is not None:
        try:
            seconds = float(raw)
        except ValueError:
            try:
                seconds = parsedate_to_datetime(raw).timestamp() - time.time()
            except (ValueError, TypeError, OverflowError):
                seconds = 60.0
    if headers.get("x-ratelimit-remaining") == "0":
        try:
            seconds = max(seconds, float(headers["x-ratelimit-reset"]) - time.time())
        except (KeyError, ValueError, OverflowError):
            seconds = max(seconds, 60.0)
    if not math.isfinite(seconds) or seconds < 0:
        seconds = 60.0
    if seconds:
        scheduler, key = bound
        scheduler.cooldowns[key] = max(scheduler.cooldowns.get(key, 0), time.monotonic() + seconds)


def decode(content):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError
            result[key] = value
        return result

    def invalid(_):
        raise ValueError

    try:
        if len(content) > 1024 * 1024:
            raise ValueError
        return json.loads(content, object_pairs_hook=pairs, parse_constant=invalid)
    except (ValueError, UnicodeError, RecursionError):
        raise HttpError("github_invalid_response") from None


@dataclass
class Reply:
    data: object
    headers: dict
    route: str


def url(value):
    try:
        if type(value) is not str or len(value) > 16384 or any(ord(c) <= 32 for c in value):
            raise ValueError
        parts = urlsplit(value)
        if (
            parts.scheme != "https"
            or parts.netloc != "api.github.com"
            or parts.fragment
            or parts.username is not None
            or "\\" in value
            or "%" in parts.path
            or "//" in parts.path
            or any(s in (".", "..") for s in parts.path.split("/"))
        ):
            raise ValueError
        return parts
    except ValueError:
        raise HttpError("github_invalid_link") from None


def related(before, after):
    if before == after:
        return True
    # GitHub canonicalizes repository routes to /repositories/{id}, including page links.
    pattern = r"^(?:repos/[^/]+/[^/]+|repositories/[1-9][0-9]*)(.*)$"
    first, second = re.fullmatch(pattern, before), re.fullmatch(pattern, after)
    return first is not None and second is not None and first[1] == second[1]


async def request(ctx, method, route, *, params=None, body=None, expected=200):
    query = {k: str(v) for k, v in (params or {}).items()}
    bound = _schedule.get()
    if bound is not None:
        scheduler, key = bound
        if scheduler.cooldowns.get(key, 0) > time.monotonic():
            raise HttpError("github_rate_limited")
        if method != "GET":
            delay = scheduler.writes.get(key, 0) + 1 - time.monotonic()
            if delay > 0:
                async with asyncio.timeout_at(ctx.deadline):
                    await asyncio.sleep(delay)
            scheduler.writes[key] = time.monotonic()

    async def consume(response):
        headers = dict(response.headers)
        status = response.status_code
        if status != expected:
            limited = status == 429 or (
                status == 403
                and (headers.get("x-ratelimit-remaining") == "0" or "retry-after" in headers)
            )
            if status == 403 and not limited:
                # Some secondary limits carry only a documented message, not rate headers.
                try:
                    data = decode(await response.read())
                    message = data.get("message", "") if type(data) is dict else ""
                    limited = type(message) is str and any(
                        text in message.lower()
                        for text in ("secondary rate limit", "api rate limit exceeded")
                    )
                except HttpError:
                    pass
            if limited:
                cooldown(headers, True)
                raise HttpError("github_rate_limited")
            codes = {
                401: "github_credentials_rejected",
                403: "github_access_denied",
                404: "github_resource_unavailable",
                422: "github_request_rejected",
            }
            raise HttpError(codes.get(status, "github_http_failed"))
        cooldown(headers, False)
        return status, decode(await response.read()), headers

    try:
        try:
            _, data, headers = await ctx.http("api").request(
                method, route, params=query, json=body, headers=HEADERS, consume=consume
            )
        except HttpError as error:
            if error.code != "http_redirect_rejected":
                raise
            if method != "GET":
                raise HttpError("github_resource_moved") from None
            # SDK b9 forbids 3xx before exposing headers. Repeat only this safe GET
            # through a bounded application-owned redirect adapter using public resources.
            from .network import redirected_get

            _, data, headers, route = await redirected_get(ctx, route, query, consume)
        return Reply(data, headers, route)
    except HttpError as error:
        ctx.logger.warning(error.code if error.code.startswith("github_") else "github_http_failed")
        raise


def next_page(reply, current, per_page):
    link = reply.headers.get("link")
    if link is None:
        return None
    if len(link) > 16384:
        raise HttpError("github_invalid_pagination")
    next_value = None
    for entry in link.split(","):
        match = re.fullmatch(r'\s*<([^<>]+)>\s*;\s*rel="(next|prev|first|last)"\s*', entry)
        if match is None:
            raise HttpError("github_invalid_pagination")
        if match[2] != "next":
            continue
        if next_value is not None:
            raise HttpError("github_invalid_pagination")
        parts = url(match[1])
        if not related(reply.route, parts.path.removeprefix("/")):
            raise HttpError("github_invalid_pagination")
        pairs = parse_qsl(parts.query, keep_blank_values=True)
        values = dict(pairs)
        raw = values.get("page", "")
        if (
            len(values) != len(pairs)
            or not raw.isascii()
            or not raw.isdigit()
            or not int(raw) == current + 1 <= 1000000
            or values.get("per_page", str(per_page)) != str(per_page)
        ):
            raise HttpError("github_invalid_pagination")
        next_value = int(raw)
    return next_value


def object_data(reply):
    if type(reply.data) is not dict:
        raise HttpError("github_invalid_response")
    return reply.data


def items(reply, params, key=None):
    data = object_data(reply).get(key) if key is not None else reply.data
    if (
        type(data) is not list
        or len(data) > params.per_page
        or any(type(item) is not dict for item in data)
    ):
        raise HttpError("github_invalid_page")
    if not reply.route.endswith("/files") and any(not positive(item.get("id")) for item in data):
        raise HttpError("github_invalid_page")
    following = next_page(reply, params.page, params.per_page)
    page_data = {
        "items": data,
        "page": params.page,
        "per_page": params.per_page,
        "has_more": following is not None,
        "next_page": following,
    }
    if key is not None and "total_count" in reply.data:
        total = reply.data["total_count"]
        if type(total) is not int or total < 0:
            raise HttpError("github_invalid_page")
        page_data["total_count"] = total
    return page_data


def paging(params):
    return {"page": params.page, "per_page": params.per_page}


def result(data):
    return Result(data=data)


def positive(value):
    return type(value) is int and 0 < value < 2**53
