import json
import logging

import httpx
import pytest
from vendor import rpc, tool


async def test_token_connection_empty_identity_replay_restart_disconnect(case):
    declaration = case.declaration.manifest
    assert declaration.id == "tencent-meeting" and len(declaration.operations) == 7
    assert {op.name for op in declaration.operations if op.effects == "write"} == {
        "create_meeting",
        "update_meeting",
        "cancel_meeting",
    }
    case.vendor.empty = True
    view = await case.begin()
    assert view.type == "form"
    saved = await case.complete(view)
    assert saved.status == "succeeded" and saved.data.status == "connected", saved
    connection = saved.data.connection
    assert connection.identity.account_id is None and connection.identity.tenant_id is None
    assert connection.capabilities is None
    count = len(case.vendor.calls)
    assert (await case.complete(view)).data == saved.data
    assert len(case.vendor.calls) == count
    await case.stop()
    await case.reopen()
    assert (await case.invoke(connection, "list_meetings", {})).status == "succeeded"
    disconnected = await case.sdk.disconnect(
        connection.connection_id,
        expected_revision=connection.revision,
        **case.metadata("connection.disconnect", connection_id=str(connection.connection_id)),
    )
    assert disconnected.data.revocation is None
    count = len(case.vendor.calls)
    assert (await case.invoke(connection, "list_meetings", {})).status == "failed"
    assert len(case.vendor.calls) == count


async def test_cross_user_auth_and_operations_are_rejected(case):
    view = await case.begin()
    assert (await case.complete(view, user="user-B")).status == "failed"
    assert not case.vendor.calls
    connection = await case.connect()
    count = len(case.vendor.calls)
    assert (await case.invoke(connection, "list_meetings", {}, user="user-B")).status == "failed"
    assert len(case.vendor.calls) == count


async def test_different_tokens_remain_separate_connections_without_fake_identity(case):
    first = await case.connect()
    result = await case.complete(await case.begin(), token="second-meeting-token")
    assert result.data.status == "connected", result
    second = result.data.connection
    assert first.connection_id != second.connection_id
    for connection, expected in [(first, "test-meeting-token"), (second, "second-meeting-token")]:
        assert (await case.invoke(connection, "list_meetings", {})).status == "succeeded"
        assert case.vendor.calls[-1].headers["x-tencent-meeting-token"] == expected


@pytest.mark.parametrize(
    "value,expected", [("", "pending"), ("bad-token", "failed"), ("bad\ntoken", "pending")]
)
async def test_invalid_tokens_cannot_connect(case, value, expected):
    reply = await case.complete(await case.begin(), token=value)
    assert reply.data.status == expected, reply
    if expected == "pending":
        assert not case.vendor.calls
    assert (await case.sdk.list_connections(**case.metadata("connection.list"))).data == ()


@pytest.mark.parametrize("mode", ["error", "is_error", "version_only", "malformed"])
async def test_business_read_validation_required_to_connect(case, mode):
    async def inject(request):
        data = json.loads(request.content)
        if data["method"] == "tools/call":
            if mode == "error":
                return rpc({"error": {"code": 1, "message": "private-error"}})
            if mode == "is_error":
                return rpc({"isError": True, "content": []})
            if mode == "version_only":
                return tool({"latest_version": "v2"})
            return tool({"meetings": [], "has_more": "false"})

    case.vendor.inject = inject
    reply = await case.complete(await case.begin())
    assert reply.data.status == "failed", reply


async def test_logs_storage_and_public_results_do_not_expose_token_or_vendor_errors(case, caplog):
    caplog.set_level(logging.DEBUG)
    connection = await case.connect()

    async def inject(request):
        return httpx.Response(503, json={"message": "private-vendor-error"})

    case.vendor.inject = inject
    result = await case.invoke(connection, "list_meetings", {})
    assert result.status == "failed"
    for value in ("test-meeting-token", "private-vendor-error"):
        assert value not in caplog.text + repr(result)
        assert all(
            value.encode() not in p.read_bytes()
            for p in (case.root / "data").rglob("*")
            if p.is_file()
        )


async def test_token_rejected_after_connection_cannot_trigger_writes(case):
    connection = await case.connect()
    case.vendor.tokens.clear()
    reply = await case.invoke(
        connection,
        "create_meeting",
        {
            "subject": "x",
            "start_time": "2026-11-03T18:00:00+08:00",
            "end_time": "2026-11-03T19:00:00+08:00",
        },
    )
    assert reply.status == "failed" and not case.vendor.writes
