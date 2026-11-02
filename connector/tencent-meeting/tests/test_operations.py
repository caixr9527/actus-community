import asyncio
import json

import httpx
import pytest
from vendor import ID, MEETING, rpc, tool

NEW = {
    "subject": "复核会",
    "start_time": "2026-11-03T18:00:00+08:00",
    "end_time": "2026-11-03T19:00:00+08:00",
}
HISTORY = {"start_time": "2026-10-01T00:00:00+08:00", "end_time": "2026-10-02T00:00:00+08:00"}
CASES = [
    ("list_meetings", {}, "get_user_meetings"),
    ("list_ended_meetings", HISTORY, "get_user_ended_meetings"),
    ("get_meeting", {"meeting_id": ID}, "get_meeting"),
    ("get_meeting_by_code", {"meeting_code": "123456789"}, "get_meeting_by_code"),
    ("create_meeting", NEW, "schedule_meeting"),
    ("update_meeting", {"meeting_id": ID, "subject": "修改"}, "update_meeting"),
    ("cancel_meeting", {"meeting_id": ID}, "cancel_meeting"),
]


@pytest.mark.parametrize("name,params,wire", CASES)
async def test_seven_static_operations(case, name, params, wire):
    connection = await case.connect()
    reply = await case.invoke(connection, name, params)
    assert reply.status == "succeeded", reply
    assert case.vendor.tools[-1][0] == wire
    assert all(
        value not in repr(reply)
        for value in (
            "private-host-key",
            "private-password",
            "private-user-id",
            "private-vendor-data",
        )
    )
    if name in {"create_meeting", "update_meeting", "cancel_meeting"}:
        assert case.vendor.writes[-1] == (wire, params | {"meeting_type": 0})


@pytest.mark.parametrize(
    "name,params",
    [
        ("create_meeting", NEW | {"subject": ""}),
        ("create_meeting", NEW | {"subject": " "}),
        ("create_meeting", NEW | {"subject": "x" * 129}),
        ("create_meeting", NEW | {"subject": "x\n"}),
        ("create_meeting", NEW | {"start_time": "2026-11-03T20:00:00+08:00"}),
        ("create_meeting", NEW | {"end_time": "2026-11-03T19:00:00"}),
        ("create_meeting", NEW | {"end_time": "2026-11-03T19:00:00-00:00"}),
        ("create_meeting", NEW | {"end_time": "2026-02-30T19:00:00Z"}),
        ("create_meeting", NEW | {"end_time": "2026-11-03T19:00:00+08:99"}),
        ("create_meeting", NEW | {"end_time": "2026-11-03T19:00:00.1Z"}),
        ("create_meeting", NEW | {"invitees": ["other"]}),
        ("create_meeting", NEW | {"meeting_type": 1}),
        ("update_meeting", {"meeting_id": ID}),
        ("update_meeting", {"meeting_id": ID, "subject": None}),
        ("update_meeting", {"meeting_id": ID, "subject": "x", "hosts": ["other"]}),
        ("cancel_meeting", {"meeting_id": "../other"}),
        ("cancel_meeting", {"meeting_id": "https://evil.test"}),
        ("cancel_meeting", {"meeting_id": "0"}),
        ("cancel_meeting", {"meeting_id": "18446744073709551616"}),
        ("cancel_meeting", {"meeting_id": True}),
        ("cancel_meeting", {"meeting_id": ID, "sub_meeting_id": "other"}),
        ("get_meeting_by_code", {"meeting_code": "123-456-789"}),
        ("get_meeting_by_code", {"meeting_code": 123456789}),
        ("list_meetings", {"page_token": ""}),
        ("list_meetings", {"page_token": None}),
        ("list_meetings", {"page_token": "x\ny"}),
        ("list_meetings", {"userid": "other"}),
        ("list_ended_meetings", HISTORY | {"page_size": 21}),
        ("list_ended_meetings", HISTORY | {"end_time": "2026-12-01T00:00:00Z"}),
    ],
)
async def test_bad_input_rejected_before_any_vendor_request(case, name, params):
    connection = await case.connect()
    before = len(case.vendor.calls)
    result = await case.invoke(connection, name, params)
    assert result.status == "failed" and len(case.vendor.calls) == before


@pytest.mark.parametrize("kind", [1, 2, 5, 6, None, True])
@pytest.mark.parametrize("name", ["update_meeting", "cancel_meeting"])
async def test_nonordinary_meeting_never_mutated(case, kind, name):
    connection = await case.connect()
    case.vendor.meeting["meeting_type"] = kind
    params = {"meeting_id": ID} | ({"subject": "x"} if name == "update_meeting" else {})
    assert (await case.invoke(connection, name, params)).status == "failed"
    assert not case.vendor.writes


async def test_missing_or_changed_schema_rejects_before_write(case):
    connection = await case.connect()
    del case.vendor.catalog["schedule_meeting"]
    assert (await case.invoke(connection, "create_meeting", NEW)).status == "failed"
    assert not case.vendor.writes
    case.vendor.catalog["schedule_meeting"] = {
        "type": "object",
        "properties": {},
        "required": ["unknown_required"],
    }
    assert (await case.invoke(connection, "create_meeting", NEW)).status == "failed"
    assert not case.vendor.writes


@pytest.mark.parametrize(
    "schema",
    [
        None,
        {},
        {"type": "string"},
        {"type": "object", "properties": {"x": {"$ref": "https://evil.test/schema"}}},
        {"type": "object", "properties": {"x": {"$ref": "#/definitions/x"}}},
        {"type": "object", "required": "wrong"},
    ],
)
async def test_unsupported_remote_schema_is_not_followed(case, schema):
    connection = await case.connect()
    case.vendor.catalog["schedule_meeting"] = schema
    assert (await case.invoke(connection, "create_meeting", NEW)).status == "failed"
    assert not case.vendor.writes


async def test_unknown_vendor_tool_not_exposed(case):
    connection = await case.connect()
    case.vendor.catalog["submit_feedback"] = {"type": "object"}
    before = len(case.vendor.calls)
    assert (await case.invoke(connection, "submit_feedback", {})).status == "failed"
    assert len(case.vendor.calls) == before
    assert (await case.invoke(connection, "list_meetings", {})).status == "succeeded"
    assert all(name != "submit_feedback" for name, _ in case.vendor.tools)


@pytest.mark.parametrize("name,params,wire", CASES[4:])
@pytest.mark.parametrize("mode", ["lost", "http", "redirect", "nested_error", "tool_error", "bad"])
async def test_write_result_unknown_never_retries(case, name, params, wire, mode):
    connection = await case.connect()
    sent = []

    async def inject(request):
        data = json.loads(request.content)
        if data["method"] == "tools/call" and data["params"]["name"] == wire:
            sent.append(request)
            if mode == "lost":
                raise httpx.ReadError("private-error")
            if mode == "http":
                return httpx.Response(503, json={"message": "private-error"})
            if mode == "redirect":
                return httpx.Response(307, headers={"location": "https://evil.test/x"})
            if mode == "nested_error":
                return rpc({"error": {"code": 400, "message": "private-error"}})
            if mode == "tool_error":
                return rpc({"isError": True, "content": []})
            return tool({})

    case.vendor.inject = inject
    result = await case.invoke(connection, name, params)
    assert result.status == "uncertain", result
    assert len(sent) == 1 and "private-error" not in repr(result)


@pytest.mark.parametrize("code", [-32601, -32602])
async def test_explicit_rpc_dispatch_rejection_is_not_sent_write(case, code):
    connection = await case.connect()

    async def inject(request):
        data = json.loads(request.content)
        if data["method"] == "tools/call" and data["params"]["name"] == "schedule_meeting":
            return httpx.Response(
                200, json={"jsonrpc": "2.0", "id": 1, "error": {"code": code, "message": "private"}}
            )

    case.vendor.inject = inject
    assert (await case.invoke(connection, "create_meeting", NEW)).status == "failed"


async def test_page_cursor_preserves_empty_page_progress(case):
    connection = await case.connect()

    async def inject(request):
        data = json.loads(request.content)
        if data["method"] == "tools/call":
            if data["params"]["arguments"].get("page_token") == "cursor-2":
                return tool({"meetings": [MEETING], "has_more": False})
            return tool({"meetings": [], "has_more": True, "next_page_token": "cursor-2"})

    case.vendor.inject = inject
    first = await case.invoke(connection, "list_meetings", {})
    assert first.status == "succeeded" and first.data["has_more"]
    assert first.data["meetings"] == [] and first.data["next_page_token"] == "cursor-2"
    second = await case.invoke(connection, "list_meetings", {"page_token": "cursor-2"})
    assert second.status == "succeeded" and second.data["has_more"] is False


@pytest.mark.parametrize(
    "body",
    [
        {"meetings": [], "has_more": True},
        {"meetings": [], "has_more": "false"},
        {"meetings": [], "has_more": True, "next_page_token": "repeat"},
        {"meetings": [], "has_more": False, "next_page_token": "extra"},
        {"meetings": [MEETING, MEETING], "has_more": False},
        {"meetings": [{}], "has_more": False},
        {"has_more": False},
    ],
)
async def test_invalid_paging_not_reported_as_complete(case, body):
    connection = await case.connect()

    async def inject(request):
        if json.loads(request.content)["method"] == "tools/call":
            return tool(body)

    case.vendor.inject = inject
    assert (
        await case.invoke(connection, "list_meetings", {"page_token": "repeat"})
    ).status == "failed"


@pytest.mark.parametrize(
    "change",
    [
        {"meeting_id": "999"},
        {"meeting_type": True},
        {"subject": ""},
        {"join_url": "https://evil.test/x"},
        {"join_url": "javascript:alert(1)"},
        {"join_url": "https://user@meeting.tencent.com/x"},
    ],
)
async def test_detail_mismatch_or_unsafe_url_rejected(case, change):
    connection = await case.connect()
    case.vendor.meeting.update(change)
    assert (await case.invoke(connection, "get_meeting", {"meeting_id": ID})).status == "failed"


async def test_structured_content_and_success_envelope(case):
    connection = await case.connect()

    async def inject(request):
        if json.loads(request.content)["method"] == "tools/call":
            return rpc({"structuredContent": {"code": 0, "data": MEETING}})

    case.vendor.inject = inject
    assert (await case.invoke(connection, "get_meeting", {"meeting_id": ID})).status == "succeeded"


@pytest.mark.parametrize(
    "content",
    [
        b"null",
        b"[]",
        b"{",
        b'{"jsonrpc":"2.0","id":1,"id":2,"result":{}}',
        b'{"jsonrpc":"2.0","id":true,"result":{}}',
        b'{"jsonrpc":"2.0","id":1,"result":{},"error":{}}',
        b"x" * (1024 * 1024 + 1),
    ],
)
async def test_bad_rpc_payload_rejected(case, content):
    connection = await case.connect()

    async def inject(request):
        return httpx.Response(200, content=content, headers={"content-type": "application/json"})

    case.vendor.inject = inject
    assert (await case.invoke(connection, "list_meetings", {})).status == "failed"


async def test_cancelled_write_does_not_resend(case):
    connection = await case.connect()
    sent, started = [], asyncio.Event()

    async def inject(request):
        data = json.loads(request.content)
        if data["method"] == "tools/call" and data["params"]["name"] == "schedule_meeting":
            sent.append(request)
            started.set()
            await asyncio.Event().wait()

    case.vendor.inject = inject
    task = asyncio.create_task(case.invoke(connection, "create_meeting", NEW))
    await asyncio.wait_for(started.wait(), 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert len(sent) == 1


@pytest.mark.parametrize("mode", [1, None, True])
@pytest.mark.parametrize("name", ["update_meeting", "cancel_meeting"])
async def test_quick_or_unclassified_meeting_never_mutated(case, mode, name):
    connection = await case.connect()
    case.vendor.meeting["type"] = mode
    params = {"meeting_id": ID} | ({"subject": "x"} if name == "update_meeting" else {})
    assert (await case.invoke(connection, name, params)).status == "failed"
    assert not case.vendor.writes


@pytest.mark.parametrize(
    "data",
    [
        {"success": False, **MEETING},
        {"success": "true", "meeting_id": ID},
        {"success": True, "meeting_id": "999"},
        {"success": True, "meeting_id": ID, "meeting_type": 1},
        {"success": True, "meeting_id": ID, "meeting_type": True},
    ],
)
async def test_false_or_mismatched_write_acknowledgement_stays_uncertain(case, data):
    connection = await case.connect()

    async def inject(request):
        body = json.loads(request.content)
        if body["method"] == "tools/call" and body["params"]["name"] == "cancel_meeting":
            return tool(data)

    case.vendor.inject = inject
    assert (
        await case.invoke(connection, "cancel_meeting", {"meeting_id": ID})
    ).status == "uncertain"


async def test_partial_time_change_is_rejected_before_read(case):
    connection = await case.connect()
    count = len(case.vendor.calls)
    reply = await case.invoke(
        connection,
        "update_meeting",
        {
            "meeting_id": ID,
            "start_time": NEW["start_time"],
        },
    )
    assert reply.status == "failed" and len(case.vendor.calls) == count


async def test_catalog_is_paginated_without_expanding_tool_manifest(case):
    connection = await case.connect()
    entries = [{"name": name, "inputSchema": value} for name, value in case.vendor.catalog.items()]

    async def inject(request):
        body = json.loads(request.content)
        if body["method"] == "tools/list":
            if body["params"].get("cursor") == "next-catalog":
                return rpc({"tools": entries[3:]})
            return rpc({"tools": entries[:3], "nextCursor": "next-catalog"})

    case.vendor.inject = inject
    assert (await case.invoke(connection, "create_meeting", NEW)).status == "succeeded"
    assert len(case.vendor.writes) == 1


@pytest.mark.parametrize("mode", ["duplicate", "loop", "empty_cursor", "bad_tools"])
async def test_catalog_anomaly_rejected_before_write(case, mode):
    connection = await case.connect()
    count = len(case.vendor.calls)
    entry = {"name": "schedule_meeting", "inputSchema": case.vendor.catalog["schedule_meeting"]}

    async def inject(request):
        if json.loads(request.content)["method"] == "tools/list":
            if mode == "duplicate":
                return rpc({"tools": [entry, entry]})
            if mode == "loop":
                return rpc({"tools": [], "nextCursor": "repeat"})
            if mode == "empty_cursor":
                return rpc({"tools": [], "nextCursor": ""})
            return rpc({"tools": {}})

    case.vendor.inject = inject
    assert (await case.invoke(connection, "create_meeting", NEW)).status == "failed"
    assert not case.vendor.writes and len(case.vendor.calls) <= count + 2


@pytest.mark.parametrize("status", [400, 401, 403, 404, 429, 500])
async def test_preflight_http_failure_never_sends_write(case, status):
    connection = await case.connect()
    count = len(case.vendor.calls)

    async def inject(request):
        return httpx.Response(status, json={"message": "private"})

    case.vendor.inject = inject
    assert (await case.invoke(connection, "create_meeting", NEW)).status == "failed"
    assert len(case.vendor.calls) == count + 1 and not case.vendor.writes


async def test_json_only_contract_rejects_sse_without_retry(case):
    connection = await case.connect()
    count = len(case.vendor.calls)

    async def inject(request):
        return httpx.Response(
            200, text='data: {"jsonrpc":"2.0"}\n\n', headers={"content-type": "text/event-stream"}
        )

    case.vendor.inject = inject
    assert (await case.invoke(connection, "list_meetings", {})).status == "failed"
    assert len(case.vendor.calls) == count + 1


async def test_original_deadline_cancels_write_with_unknown_outcome(case):
    from connector_sdk.client import ClientError

    connection = await case.connect()
    sent = []

    async def inject(request):
        body = json.loads(request.content)
        if body["method"] == "tools/call" and body["params"]["name"] == "schedule_meeting":
            sent.append(request)
            await asyncio.Event().wait()

    case.vendor.inject = inject
    invocation = case.invocation(connection, "create_meeting")
    invocation["deadline"] = asyncio.get_running_loop().time() + 0.2
    with pytest.raises(ClientError) as captured:
        await asyncio.wait_for(case.sdk.invoke("create_meeting", NEW, **invocation), 2)
    assert captured.value.code == "client_deadline_exceeded"
    assert captured.value.outcome == "result_unknown" and len(sent) == 1


async def test_meeting_array_wrapper_is_projected(case):
    connection = await case.connect()

    async def inject(request):
        if json.loads(request.content)["method"] == "tools/call":
            return tool({"meeting_info_list": [MEETING]})

    case.vendor.inject = inject
    reply = await case.invoke(connection, "get_meeting", {"meeting_id": ID})
    assert reply.status == "succeeded" and reply.data["scheduled"] is True
    assert "private-password" not in repr(reply)
