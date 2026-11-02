"""Fixed HTTPS service, bounded JSON and projected current-user identity."""

import json

from connector_sdk import HttpError

from .models import Profile

ORIGIN = "https://api.dingtalk.com/"
SCOPES = ("openid", "Contact.User.Read", "Todo.PersonalTodo.Write")


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
        value = json.loads(content, object_pairs_hook=pairs, parse_constant=invalid)
        if type(value) is not dict:
            raise ValueError
        return value
    except (ValueError, UnicodeError, RecursionError):
        raise HttpError("dingtalk_invalid_response") from None


def material(value, *, maximum=16384):
    return (
        type(value) is str
        and 0 < len(value) <= maximum
        and value.isascii()
        and all(32 < ord(c) < 127 for c in value)
    )


async def request(ctx, method, route, *, params=None, body=None):
    async def consume(response):
        if response.status_code != 200:
            codes = {
                400: "dingtalk_request_rejected",
                401: "dingtalk_credentials_rejected",
                403: "dingtalk_access_denied",
                404: "dingtalk_resource_unavailable",
                429: "dingtalk_rate_limited",
            }
            raise HttpError(codes.get(response.status_code, "dingtalk_http_failed"))
        data = decode(await response.read())
        # New APIs return direct bodies, not a legacy errcode/result envelope.
        if any(key in data for key in ("code", "errcode", "error")):
            raise HttpError("dingtalk_api_rejected")
        return data

    try:
        return await ctx.http("api").request(
            method,
            route,
            params=params,
            json=body,
            headers={"Accept": "application/json"},
            consume=consume,
        )
    except HttpError as error:
        ctx.logger.warning(
            error.code if error.code.startswith("dingtalk_") else "dingtalk_http_failed"
        )
        raise


async def profile(ctx):
    data = await request(ctx, "GET", "v1.0/contact/users/me")
    identifier, name = data.get("unionId"), data.get("nick")
    if not material(identifier, maximum=255) or (
        name is not None
        and (
            type(name) is not str
            or not name.strip()
            or len(name) > 255
            or any(ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF for c in name)
        )
    ):
        raise HttpError("dingtalk_invalid_identity")
    return Profile(union_id=identifier, display_name=name)
