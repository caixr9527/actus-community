"""Bounded Streamable HTTP using only the SDK-owned HTTP scope."""

import codecs
import json
from contextlib import asynccontextmanager

from connector_sdk import AuthorizationRejected, HttpError, OperationRejected

from .models import Result
from .protocol import CLIENT_NAME, PROTOCOL, TOOLS
from .schema import arguments, validate

LIMIT = 256 * 1024


def decode(text):
    def invalid(_):
        raise ValueError("invalid_json")
    try:
        return json.loads(text, parse_constant=invalid)
    except (ValueError, UnicodeError, RecursionError):
        raise HttpError("notion_invalid_response") from None


def rpc_result(value, request_id):
    if (not isinstance(value, dict) or value.get("jsonrpc") != "2.0"
            or type(value.get("id")) is not int or value["id"] != request_id
            or ("result" in value) == ("error" in value)):
        raise HttpError("notion_invalid_response")
    if "error" in value:
        error = value["error"]
        if isinstance(error, dict) and error.get("code") in {-32601, -32602}:
            raise OperationRejected()
        raise HttpError("notion_rpc_failed")
    if not isinstance(value["result"], dict):
        raise HttpError("notion_invalid_response")
    return value["result"]


def split_lines(text):
    lines, start, index = [], 0, 0
    while index < len(text):
        if text[index] not in "\r\n":
            index += 1
            continue
        lines.append(text[start:index])
        index += 2 if text[index:index + 2] == "\r\n" else 1
        start = index
    return lines, text[start:]


class Session:
    def __init__(self, ctx):
        self.http = ctx.http("notion")
        self.session_id = None
        self.request_id = 0

    async def post(self, method, params, *, notification=False):
        self.request_id += 1
        request_id = self.request_id
        body = {"jsonrpc": "2.0", "method": method, "params": params}
        if not notification:
            body["id"] = request_id
        headers = {"Accept": "application/json, text/event-stream",
                   "MCP-Protocol-Version": PROTOCOL}
        if self.session_id is not None:
            headers["Mcp-Session-Id"] = self.session_id

        async def consume(response):
            if response.status_code in {401, 403}:
                raise AuthorizationRejected()
            if not 200 <= response.status_code < 300:
                raise HttpError("notion_http_failed")
            session_id = response.headers.get("mcp-session-id")
            if session_id is not None:
                if (not session_id or len(session_id) > 512
                        or not all(33 <= ord(c) <= 126 for c in session_id)
                        or self.session_id is not None and self.session_id != session_id):
                    raise HttpError("notion_invalid_session")
                self.session_id = session_id
            if notification:
                if response.status_code != 202 or await response.read():
                    raise HttpError("notion_invalid_notification")
                return None
            content_type = response.headers.get("content-type", "").split(";")[0].strip()
            if content_type == "application/json":
                return rpc_result(decode(await response.read()), request_id)
            if content_type != "text/event-stream":
                raise HttpError("notion_invalid_response")
            decoder = codecs.getincrementaldecoder("utf-8-sig")()
            pending, data, trailing_cr = "", [], False

            def chunk_lines(chunk, *, final=False):
                nonlocal pending, trailing_cr
                try:
                    text = decoder.decode(chunk, final=final)
                except UnicodeError:
                    raise HttpError("notion_invalid_response") from None
                if text:
                    if trailing_cr:
                        text = text.removeprefix("\n")
                    trailing_cr = text.endswith("\r")
                    pending += text
                lines, pending = split_lines(pending)
                for line in lines:
                    if line == "" and data:
                        message = decode("\n".join(data))
                        data.clear()
                        if (isinstance(message, dict) and "id" not in message
                                and message.get("jsonrpc") == "2.0"):
                            continue
                        return rpc_result(message, request_id)
                    if line.startswith("data:"):
                        data.append(line[5:].removeprefix(" "))
                return None

            async for chunk in response.iter_bytes():
                result = chunk_lines(chunk)
                if result is not None:
                    return result
            result = chunk_lines(b"", final=True)
            if result is not None:
                return result
            raise HttpError("notion_incomplete_event")

        return await self.http.request("POST", "mcp", headers=headers, json=body, consume=consume)

    async def initialize(self):
        result = await self.post("initialize", {"protocolVersion": PROTOCOL, "capabilities": {},
                                 "clientInfo": {"name": CLIENT_NAME, "version": "0.1.0"}})
        if result.get("protocolVersion") != PROTOCOL:
            raise HttpError("notion_protocol_mismatch")
        await self.post("notifications/initialized", {}, notification=True)

    async def close(self):
        if self.session_id is None:
            return

        async def consume(response):
            if response.status_code not in {200, 202, 204, 404, 405}:
                raise HttpError("notion_session_close_failed")
            await response.read()

        await self.http.request("DELETE", "mcp", consume=consume,
                                headers={"Mcp-Session-Id": self.session_id,
                                         "MCP-Protocol-Version": PROTOCOL})

    async def tools(self):
        tools, cursor, seen = {}, None, set()
        for _ in range(16):
            page = await self.post("tools/list", {} if cursor is None else {"cursor": cursor})
            items = page.get("tools")
            if not isinstance(items, list) or len(items) > 256:
                raise HttpError("notion_invalid_tools")
            for tool in items:
                if (not isinstance(tool, dict) or not isinstance(tool.get("name"), str)
                        or not isinstance(tool.get("inputSchema"), dict)
                        or tool["name"] in tools or len(tools) >= 256):
                    raise HttpError("notion_invalid_tools")
                tools[tool["name"]] = tool["inputSchema"]
            cursor = page.get("nextCursor")
            if cursor is None:
                return tools
            if (not isinstance(cursor, str) or not cursor or len(cursor) > 4096 or cursor in seen):
                raise HttpError("notion_invalid_cursor")
            seen.add(cursor)
        raise HttpError("notion_tools_limit")

    async def tool(self, name, args):
        return payload(await self.post("tools/call", {"name": name, "arguments": args}))


@asynccontextmanager
async def session(ctx):
    connection = Session(ctx)
    try:
        await connection.initialize()
        yield connection
    finally:
        try:
            await connection.close()
        except Exception:
            # Cleanup failure cannot turn a completed write into a retryable failure.
            ctx.logger.warning("notion_session_close_failed")


def payload(result):
    if type(result.get("isError", False)) is not bool:
        raise HttpError("notion_invalid_response")
    if result.get("isError"):
        raise HttpError("notion_tool_failed")
    if "structuredContent" in result:
        value = result["structuredContent"]
        if not isinstance(value, dict):
            raise HttpError("notion_invalid_response")
    else:
        content = result.get("content")
        if (not isinstance(content, list) or not content or len(content) > 64
                or any(not isinstance(b, dict) or b.get("type") != "text"
                       or not isinstance(b.get("text"), str) for b in content)):
            raise HttpError("notion_invalid_response")
        text = "\n".join(b["text"] for b in content)
        try:
            parsed = decode(text)
        except HttpError:
            parsed = {"text": text}
        value = parsed if isinstance(parsed, dict) else {"value": parsed}
    try:
        result_model = Result(data=value)
        if len(result_model.model_dump_json().encode()) > LIMIT:
            raise HttpError("notion_result_too_large")
        return result_model
    except (ValueError, RecursionError):
        raise HttpError("notion_invalid_response") from None


async def permissions(connection, tools):
    """Missing tools are unavailable; listing alone says nothing about authorization."""
    result = {name: False for name, remote in TOOLS.items() if remote not in tools}
    if "notion-get-tool-access" not in tools:
        return result
    validate({}, tools["notion-get-tool-access"])
    data = (await connection.tool("notion-get-tool-access", {})).data
    access = data.get("current_tool_access")
    if not isinstance(access, dict):
        raise HttpError("notion_invalid_access")
    for name, remote in TOOLS.items():
        entry = access.get(remote.removeprefix("notion-").replace("-", "_"))
        status = entry.get("status") if isinstance(entry, dict) else None
        if remote in tools and status in {"available", "available_with_limit"}:
            result[name] = True
        elif status in {"not_enabled", "plan_required", "full_version_required"}:
            result[name] = False
    return result


async def call(ctx, name, params):
    if name not in TOOLS:
        raise OperationRejected()
    sent = False
    try:
        async with session(ctx) as connection:
            tools = await connection.tools()
            remote = TOOLS[name]
            if (remote not in tools
                    or name == "duplicate_page" and TOOLS["get_async_task"] not in tools):
                raise OperationRejected()
            caps = await permissions(connection, tools)
            if (caps.get(name) is False
                    or name == "duplicate_page" and caps.get("get_async_task") is False):
                raise OperationRejected()
            if name == "duplicate_page" or params.get("allow_async") is True:
                task_schema = tools.get(TOOLS["get_async_task"])
                if task_schema is None or caps.get("get_async_task") is False:
                    raise OperationRejected()
                # Confirm the exposed polling contract before accepting an async write.
                arguments("get_async_task", {"task_id": "00000000-0000-0000-0000-000000000000"},
                          task_schema)
            args = arguments(name, params, tools[remote])
            sent = True
            return await connection.tool(remote, args)
    except AuthorizationRejected:
        raise OperationRejected() from None
    except HttpError:
        if not sent:
            raise OperationRejected() from None
        raise
