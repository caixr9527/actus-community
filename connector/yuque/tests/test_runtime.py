import json
import logging

import httpx
import pytest
from vendor import USER, reply


async def test_real_identity_replay_restart_disconnect(case):
    manifest = case.declaration.manifest
    assert manifest.id == "yuque" and len(manifest.operations) == 9
    assert {op.name for op in manifest.operations if op.effects == "write"} == {
        "create_document",
        "update_document",
    }
    view = await case.begin()
    assert view.type == "form"
    saved = await case.complete(view)
    assert saved.status == "succeeded" and saved.data.status == "connected", saved
    connection = saved.data.connection
    assert connection.identity.account_id == "42" and connection.identity.tenant_id is None
    assert connection.identity.display_name == "测试用户" and connection.capabilities is None
    count = len(case.vendor.calls)
    assert (await case.complete(view)).data == saved.data
    assert len(case.vendor.calls) == count
    await case.stop()
    await case.reopen()
    assert (await case.invoke(connection, "get_current_user", {})).status == "succeeded"
    disconnected = await case.sdk.disconnect(
        connection.connection_id,
        expected_revision=connection.revision,
        **case.metadata("connection.disconnect", connection_id=str(connection.connection_id)),
    )
    assert disconnected.data.revocation is None
    count = len(case.vendor.calls)
    assert (await case.invoke(connection, "get_current_user", {})).status == "failed"
    assert len(case.vendor.calls) == count


async def test_cross_user_cannot_complete_or_use_connection(case):
    assert (await case.complete(await case.begin(), user="other-user")).status == "failed"
    assert not case.vendor.calls
    connection = await case.connect()
    count = len(case.vendor.calls)
    assert (
        await case.invoke(connection, "get_current_user", {}, user="other-user")
    ).status == "failed"
    assert len(case.vendor.calls) == count


async def test_two_accounts_never_share_credentials(case):
    first = await case.connect()
    second = (await case.complete(await case.begin(), token="second-yuque-token")).data.connection
    assert first.connection_id != second.connection_id and second.identity.account_id == "43"
    for connection, token in [(first, "test-yuque-token"), (second, "second-yuque-token")]:
        assert (await case.invoke(connection, "get_current_user", {})).status == "succeeded"
        assert case.vendor.calls[-1].headers["x-auth-token"] == token


@pytest.mark.parametrize(
    "token,state", [("", "pending"), ("x\ny", "pending"), ("invalid", "failed")]
)
async def test_bad_token_never_connects(case, token, state):
    result = await case.complete(await case.begin(), token=token)
    assert result.data.status == state
    if state == "pending":
        assert not case.vendor.calls
    assert (await case.sdk.list_connections(**case.metadata("connection.list"))).data == ()


@pytest.mark.parametrize(
    "data",
    [
        None,
        [],
        {},
        {"id": True, "login": "x"},
        {"id": 0, "login": "x"},
        {"id": "42", "login": "x"},
        {"id": 42, "login": ""},
        USER | {"error": "private"},
    ],
)
async def test_authoritative_identity_is_required(case, data):
    async def inject(request):
        if data is not None and "error" in data:
            return httpx.Response(200, json={"error": "private", "data": USER})
        return reply(data)

    case.vendor.inject = inject
    assert (await case.complete(await case.begin())).data.status == "failed"


async def test_token_and_raw_errors_never_leak(case, caplog):
    caplog.set_level(logging.DEBUG)
    connection = await case.connect()

    async def inject(request):
        return httpx.Response(503, json={"error": "private-service-error"})

    case.vendor.inject = inject
    result = await case.invoke(connection, "get_current_user", {})
    assert result.status == "failed"
    for marker in ("test-yuque-token", "private-service-error"):
        assert marker not in repr(result) + caplog.text
        assert all(
            marker.encode() not in p.read_bytes()
            for p in (case.root / "data").rglob("*")
            if p.is_file()
        )


async def test_unknown_operation_cannot_send_arbitrary_request(case):
    connection = await case.connect()
    count = len(case.vendor.calls)
    assert (await case.invoke(connection, "delete_document", {"id": "100"})).status == "failed"
    assert len(case.vendor.calls) == count


async def test_invalidated_token_cannot_reach_write(case):
    connection = await case.connect()
    case.vendor.tokens.clear()
    result = await case.invoke(
        connection, "create_document", {"repository_id": "10", "title": "x", "body": "x"}
    )
    assert result.status == "failed" and not case.vendor.writes


async def test_headers_and_identity_are_not_copied_from_user_fields(case):
    connection = await case.connect()
    result = await case.invoke(
        connection, "get_current_user", {"account_id": "other", "token": "other"}
    )
    assert result.status == "failed"
    assert json.loads(case.vendor.calls[-1].content or "{}") == {}


async def test_explicit_group_identity_cannot_be_personal_connection(case):
    async def inject(request):
        return reply(USER | {"type": "Group"})

    case.vendor.inject = inject
    assert (await case.complete(await case.begin())).data.status == "failed"
