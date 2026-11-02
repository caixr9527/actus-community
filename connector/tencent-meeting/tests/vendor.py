"""Documented wire arguments plus explicit compatibility response fixtures, not live captures."""

import copy
import json

import httpx

ID = "6953553464429888300"
CODE = "123456789"
MEETING = {
    "meeting_id": ID,
    "meeting_code": CODE,
    "subject": "产品周会",
    "meeting_type": 0,
    "type": 0,
    "start_time": "1793700000",
    "end_time": "1793703600",
    "join_url": "https://meeting.tencent.com/s/example",
    "status": "MEETING_STATE_INIT",
    "host_key": "private-host-key",
    "password": "private-password",
    "hosts": [{"userid": "private-user-id"}],
    "unknown": "private-vendor-data",
}


def reply(data, status=200):
    return httpx.Response(status, json=data)


def rpc(result):
    return reply({"jsonrpc": "2.0", "id": 1, "result": result})


def tool(data):
    return rpc({"content": [{"type": "text", "text": json.dumps(data)}], "isError": False})


def schema(properties, required=()):
    return {
        "type": "object",
        "properties": properties,
        "required": list(required),
        "additionalProperties": False,
    }


S = {"type": "string"}
N = {"type": "integer"}
CATALOG = {
    "get_user_meetings": schema({"is_show_all_sub_meetings": N, "page_token": S}),
    "get_user_ended_meetings": schema(
        {"start_time": S, "end_time": S, "page_size": N, "page_token": S},
        ("start_time", "end_time"),
    ),
    "get_meeting": schema({"meeting_id": S}, ("meeting_id",)),
    "get_meeting_by_code": schema({"meeting_code": S}, ("meeting_code",)),
    "schedule_meeting": schema(
        {"subject": S, "start_time": S, "end_time": S, "meeting_type": N},
        ("subject", "start_time", "end_time"),
    ),
    "update_meeting": schema(
        {"meeting_id": S, "subject": S, "start_time": S, "end_time": S, "meeting_type": N},
        ("meeting_id",),
    ),
    "cancel_meeting": schema({"meeting_id": S, "meeting_type": N}, ("meeting_id",)),
}


class Vendor:
    def __init__(self):
        self.calls, self.tools, self.writes = [], [], []
        self.inject = None
        self.catalog = copy.deepcopy(CATALOG)
        self.meeting = copy.deepcopy(MEETING)
        self.tokens = {"test-meeting-token", "second-meeting-token"}
        self.empty = False

    async def __call__(self, request):
        self.calls.append(request)
        assert request.url.scheme == "https" and request.url.host == "mcp.meeting.tencent.com"
        assert request.url.path == "/mcp/wemeet-open/v1" and not request.url.query
        assert request.method == "POST"
        assert request.headers["x-skill-version"] == "v1.0.15"
        assert request.headers["content-type"].startswith("application/json")
        assert "authorization" not in request.headers
        if self.inject:
            result = await self.inject(request)
            if result is not None:
                return result
        if request.headers["x-tencent-meeting-token"] not in self.tokens:
            return reply({}, 401)
        data = json.loads(request.content)
        assert data["jsonrpc"] == "2.0" and data["id"] == 1
        if data["method"] == "tools/list":
            assert data["params"] == {}
            return rpc({"tools": [{"name": k, "inputSchema": v} for k, v in self.catalog.items()]})
        assert data["method"] == "tools/call"
        name, arguments = data["params"]["name"], data["params"]["arguments"]
        self.tools.append((name, arguments))
        if name in ("get_user_meetings", "get_user_ended_meetings"):
            return tool({"meetings": [] if self.empty else [self.meeting], "has_more": False})
        if name in ("get_meeting", "get_meeting_by_code"):
            return tool(self.meeting)
        self.writes.append((name, arguments))
        assert arguments["meeting_type"] == 0
        if name == "schedule_meeting":
            return tool(
                self.meeting | {k: arguments[k] for k in ("subject", "start_time", "end_time")}
            )
        if name in ("update_meeting", "cancel_meeting"):
            return tool({"success": True, "meeting_id": arguments["meeting_id"]})
        raise AssertionError("unexpected tool")
