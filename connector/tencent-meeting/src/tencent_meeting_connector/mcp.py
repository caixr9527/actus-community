"""Pinned stateless JSON-RPC transport matching the publisher's v1.0.15 proxy."""

import json

from connector_sdk import AuthorizationRejected, HttpError, OperationRejected
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError

ORIGIN = "https://mcp.meeting.tencent.com/"
ROUTE = "mcp/wemeet-open/v1"
SKILL_VERSION = "v1.0.15"
TOOLS = frozenset(
    {
        "get_user_meetings",
        "get_user_ended_meetings",
        "get_meeting",
        "get_meeting_by_code",
        "schedule_meeting",
        "update_meeting",
        "cancel_meeting",
    }
)


def failure(code):
    raise HttpError("tencent_meeting_" + code)


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
        failure("invalid_response")


async def rpc(ctx, method, params):
    async def consume(response):
        if response.status_code in (401, 403):
            raise AuthorizationRejected()
        if response.status_code != 200:
            failure("rate_limited" if response.status_code == 429 else "http_failed")
        if (
            response.headers.get("content-type", "").split(";")[0].strip().lower()
            != "application/json"
        ):
            failure("unsupported_response_type")
        data = decode(await response.read())
        if data.get("jsonrpc") != "2.0" or type(data.get("id")) is not int or data["id"] != 1:
            failure("invalid_rpc")
        if ("result" in data) == ("error" in data):
            failure("invalid_rpc")
        if "error" in data:
            # Only standardized dispatch/parameter rejections establish no tool ran.
            error = data["error"]
            if (
                type(error) is dict
                and type(error.get("code")) is int
                and error["code"] in (-32601, -32602)
            ):
                raise OperationRejected()
            failure("rpc_failed")
        if type(data["result"]) is not dict:
            failure("invalid_rpc")
        return data["result"]

    try:
        return await ctx.http("meeting").request(
            "POST",
            ROUTE,
            headers={"Accept": "application/json", "X-Skill-Version": SKILL_VERSION},
            json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
            consume=consume,
        )
    except HttpError as error:
        ctx.logger.warning(
            error.code
            if error.code.startswith("tencent_meeting_")
            else "tencent_meeting_http_failed"
        )
        raise


def schema_safe(value, depth=0):
    if depth > 32:
        failure("unsupported_schema")
    if type(value) is dict:
        if any(key in value for key in ("$ref", "$dynamicRef")):
            failure("unsupported_schema")
        for child in value.values():
            schema_safe(child, depth + 1)
    elif type(value) is list:
        for child in value:
            schema_safe(child, depth + 1)


async def catalog(ctx):
    result, cursor = {}, None
    seen = set()
    for _ in range(10):
        data = await rpc(ctx, "tools/list", {} if cursor is None else {"cursor": cursor})
        tools = data.get("tools")
        if type(tools) is not list or len(tools) > 1000:
            failure("invalid_catalog")
        for tool in tools:
            if type(tool) is not dict or type(tool.get("name")) is not str:
                failure("invalid_catalog")
            name = tool["name"]
            if name in seen:
                failure("invalid_catalog")
            seen.add(name)
            if name not in TOOLS:
                continue
            schema = tool.get("inputSchema")
            if type(schema) is not dict or schema.get("type") != "object":
                failure("invalid_catalog")
            schema_safe(schema)
            try:
                Draft202012Validator.check_schema(schema)
            except SchemaError:
                failure("invalid_catalog")
            result[name] = schema
        following = data.get("nextCursor")
        if following is None:
            return result
        if type(following) is not str or not 0 < len(following) <= 4096 or following == cursor:
            failure("invalid_catalog")
        cursor = following
    failure("catalog_limit")


def validate(catalogue, name, arguments):
    if name not in TOOLS or name not in catalogue:
        raise OperationRejected()
    try:
        Draft202012Validator(catalogue[name]).validate(arguments)
    except ValidationError:
        raise OperationRejected() from None


def payload(result):
    if type(result.get("isError", False)) is not bool or result.get("isError") or "error" in result:
        failure("tool_failed")
    if "structuredContent" in result:
        data = result["structuredContent"]
        if type(data) is not dict:
            failure("invalid_response")
    else:
        content = result.get("content")
        if type(content) is not list or len(content) != 1:
            failure("invalid_response")
        block = content[0]
        if (
            type(block) is not dict
            or block.get("type") != "text"
            or type(block.get("text")) is not str
        ):
            failure("invalid_response")
        try:
            content = block["text"].encode("utf-8")
        except UnicodeError:
            failure("invalid_response")
        data = decode(content)
    if any(key in data for key in ("error", "errcode", "error_info")):
        failure("business_failed")
    if "code" in data:
        if type(data["code"]) is not int or data["code"] != 0 or type(data.get("data")) is not dict:
            failure("business_failed")
        data = data["data"]
        if any(key in data for key in ("error", "errcode", "error_info", "code")):
            failure("business_failed")
    if "success" in data and data["success"] is not True:
        failure("business_failed")
    return data


async def call(ctx, catalogue, name, arguments):
    validate(catalogue, name, arguments)
    return payload(await rpc(ctx, "tools/call", {"name": name, "arguments": arguments}))
