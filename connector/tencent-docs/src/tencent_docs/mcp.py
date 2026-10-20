"""Tencent MCP transport through the SDK-owned, bounded HTTP service."""

import codecs
import json

from connector_sdk import AuthorizationRejected, HttpError, OperationRejected

from .models import Result

PROTOCOL = "2025-03-26"


def invalid_constant(_):
    raise ValueError("invalid_json")


def decode(text):
    try:
        value = json.loads(text, parse_constant=invalid_constant)
    except (ValueError, UnicodeError):
        raise HttpError("tencent_invalid_response") from None
    if not isinstance(value, dict):
        raise HttpError("tencent_invalid_response")
    return value


def rpc_result(value, request_id):
    if (
        value.get("jsonrpc") != "2.0"
        or type(value.get("id")) is not int
        or value["id"] != request_id
        or ("result" in value) == ("error" in value)
    ):
        raise HttpError("tencent_invalid_response")
    if "error" in value:
        error = value["error"]
        # Protocol dispatch/parameter rejection confirms that no tool ran.
        if isinstance(error, dict) and error.get("code") in {-32601, -32602}:
            raise OperationRejected()
        raise HttpError("tencent_rpc_failed")
    if not isinstance(value["result"], dict):
        raise HttpError("tencent_invalid_response")
    return value["result"]


def split_lines(text, *, final):
    """SSE accepts LF, CRLF and CR; retain a trailing CR until the next chunk."""
    lines = []
    start = index = 0
    while index < len(text):
        char = text[index]
        if char not in "\r\n":
            index += 1
            continue
        if char == "\r" and index + 1 == len(text) and not final:
            break
        lines.append(text[start:index])
        index += 2 if text[index : index + 2] == "\r\n" else 1
        start = index
    return lines, text[start:]


class Session:
    def __init__(self, ctx):
        self.http = ctx.http("tencent")
        self.session_id = None

    async def post(self, method, params, request_id=None):
        headers = {
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": PROTOCOL,
        }
        if self.session_id is not None:
            headers["Mcp-Session-Id"] = self.session_id
        body = {"jsonrpc": "2.0", "method": method, "params": params}
        if request_id is not None:
            body["id"] = request_id

        async def consume(response):
            if response.status_code in {401, 403}:
                raise AuthorizationRejected()
            if not 200 <= response.status_code < 300:
                raise HttpError("tencent_http_failed")
            session_id = response.headers.get("mcp-session-id")
            if session_id is not None:
                if (
                    not session_id
                    or len(session_id) > 512
                    or not all(33 <= ord(c) <= 126 for c in session_id)
                ):
                    raise HttpError("tencent_invalid_session")
                if self.session_id is not None and session_id != self.session_id:
                    raise HttpError("tencent_invalid_session")
                self.session_id = session_id
            if request_id is None:
                if response.status_code != 202 or await response.read():
                    raise HttpError("tencent_invalid_notification")
                return None
            content_type = response.headers.get("content-type", "").split(";")[0].strip()
            if content_type == "application/json":
                return rpc_result(decode(await response.read()), request_id)
            if content_type != "text/event-stream":
                raise HttpError("tencent_invalid_response")
            decoder = codecs.getincrementaldecoder("utf-8-sig")()
            pending = ""
            data = []

            def line(value):
                if value == "":
                    if not data:
                        return None
                    message = decode("\n".join(data))
                    data.clear()
                    if "id" not in message and message.get("jsonrpc") == "2.0":
                        return None
                    return rpc_result(message, request_id)
                if value.startswith("data:"):
                    data.append(value[5:].removeprefix(" "))
                return None

            def consume_chunk(chunk, *, final=False):
                nonlocal pending
                try:
                    pending += decoder.decode(chunk, final=final)
                except UnicodeError:
                    raise HttpError("tencent_invalid_response") from None
                lines, pending = split_lines(pending, final=final)
                for value in lines:
                    result = line(value)
                    if result is not None:
                        return result
                return None

            async for chunk in response.iter_bytes():
                result = consume_chunk(chunk)
                if result is not None:
                    return result
            result = consume_chunk(b"", final=True)
            if result is not None:
                return result
            # An event is only dispatched on its terminating blank line.
            raise HttpError("tencent_incomplete_event")

        return await self.http.request("POST", "mcp", headers=headers, json=body, consume=consume)

    async def initialize(self):
        result = await self.post(
            "initialize",
            {
                "protocolVersion": PROTOCOL,
                "capabilities": {},
                "clientInfo": {"name": "actus-tencent-docs", "version": "0.1.0"},
            },
            1,
        )
        if result.get("protocolVersion") != PROTOCOL:
            raise HttpError("tencent_protocol_mismatch")
        await self.post("notifications/initialized", {})

    async def close(self):
        if self.session_id is None:
            return

        async def consume(response):
            # MCP servers may decline explicit session termination.
            if response.status_code not in {200, 202, 204, 404, 405}:
                raise HttpError("tencent_session_close_failed")
            await response.read()

        await self.http.request(
            "DELETE",
            "mcp",
            consume=consume,
            headers={"Mcp-Session-Id": self.session_id, "MCP-Protocol-Version": PROTOCOL},
        )


def payload(result):
    if type(result.get("isError", False)) is not bool:
        raise HttpError("tencent_invalid_response")
    if result.get("isError"):
        # A tool failure can follow a partial write. Do not claim a rejection.
        raise HttpError("tencent_tool_failed")
    if "structuredContent" in result:
        value = result["structuredContent"]
        if not isinstance(value, dict):
            raise HttpError("tencent_invalid_response")
        return Result(data=value)
    content = result.get("content")
    if not isinstance(content, list) or len(content) != 1:
        raise HttpError("tencent_invalid_response")
    block = content[0]
    if not isinstance(block, dict) or block.get("type") != "text":
        raise HttpError("tencent_invalid_response")
    text = block.get("text")
    if not isinstance(text, str):
        raise HttpError("tencent_invalid_response")
    return Result(data=decode(text))


async def call(ctx, name, arguments):
    session = Session(ctx)
    try:
        try:
            await session.initialize()
        except (HttpError, AuthorizationRejected):
            # Business tools/call has not been sent.
            raise OperationRejected() from None
        try:
            result = payload(
                await session.post("tools/call", {"name": name, "arguments": arguments}, 2)
            )
            # This vendor operation declares an error field inside its result.
            if name == "get_content" and result.data.get("error"):
                raise HttpError("tencent_tool_failed")
            return result
        except AuthorizationRejected:
            raise OperationRejected() from None
    finally:
        await session.close()


async def profile(ctx):
    session = Session(ctx)
    try:
        await session.initialize()
        return payload(
            await session.post("tools/call", {"name": "get_user_info", "arguments": {}}, 2)
        ).data
    finally:
        await session.close()
