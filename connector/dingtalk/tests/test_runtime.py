import asyncio
import logging
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from connector_sdk import OAuthCredential
from vendor import PROFILE, TOKEN, response

from dingtalk_connector.auth import Protocol


async def test_authorization_identity_replay_restart_and_disconnect(case):
    manifest = case.declaration.manifest
    assert manifest.id == "dingtalk" and len(manifest.operations) == 5
    assert {op.name for op in manifest.operations if op.effects == "read"} == {"get_current_user"}
    view = await case.begin()
    query = parse_qs(urlsplit(view.authorization_url).query)
    assert urlsplit(view.authorization_url).netloc == "login.dingtalk.com"
    assert query["scope"] == ["openid Contact.User.Read Todo.PersonalTodo.Write"]
    assert query["prompt"] == ["consent"] and query["response_type"] == ["code"]
    assert query["redirect_uri"] == ["https://backend.test/api/connector-oauth/callback"]
    assert "code_challenge" not in query and "code_challenge_method" not in query
    assert (await case.complete(view, state="wrong")).status == "failed"
    assert not case.vendor.tokens
    saved = await case.complete(view)
    assert saved.data.status == "connected", saved
    connection = saved.data.connection
    assert connection.identity.account_id == "union-42"
    assert connection.identity.tenant_id is None and connection.capabilities is None
    assert (await case.complete(view)).data == saved.data and len(case.vendor.tokens) == 1
    await case.stop()
    await case.reopen()
    assert (await case.invoke(connection, "get_current_user", {})).status == "succeeded"
    reply = await case.sdk.disconnect(
        connection.connection_id,
        expected_revision=connection.revision,
        **case.metadata("connection.disconnect", connection_id=str(connection.connection_id)),
    )
    assert reply.data.revocation.status == "not_attempted"
    assert (await case.invoke(connection, "get_current_user", {})).status == "failed"


async def test_cross_user_transaction_and_connection_rejected(case):
    view = await case.begin()
    assert (await case.complete(view, user="user-B")).status == "failed"
    assert not case.vendor.tokens
    connection = await case.connect()
    before = len(case.vendor.calls)
    assert (await case.invoke(connection, "get_current_user", {}, user="user-B")).status == "failed"
    assert len(case.vendor.calls) == before


@pytest.mark.parametrize(
    "change",
    [
        {"code": "test-code"},
        {"authCode": ""},
        {"error": "access_denied"},
        {"authCode": "\nprivate"},
        {"iss": "https://evil.test"},
    ],
)
async def test_invalid_or_ambiguous_callback_never_exchanges(case, change):
    assert (await case.complete(await case.begin(), **change)).status == "failed"
    assert not case.vendor.tokens


async def test_denied_callback_without_code_is_terminal(case):
    view = await case.begin()
    state = parse_qs(urlsplit(view.authorization_url).query)["state"][0]
    reply = await case.sdk.complete_authorization(
        view.transaction_id,
        {"state": state, "error": "access_denied"},
        **case.metadata("authorization.complete", transaction_id=str(view.transaction_id)),
    )
    assert reply.data.status == "failed" and not case.vendor.tokens


@pytest.mark.parametrize(
    "change",
    [
        {"accessToken": ""},
        {"accessToken": "\rprivate"},
        {"accessToken": None},
        {"refreshToken": None},
        {"refreshToken": ""},
        {"expireIn": True},
        {"expireIn": 0},
        {"expireIn": -1},
        {"expireIn": "7200"},
        {"expireIn": 367 * 86400},
        {"error": "private-error"},
        {"code": "InvalidParameter"},
        {"errcode": 0},
    ],
)
async def test_invalid_token_material_never_connects(case, change):
    case.vendor.token_change = change
    reply = await case.complete(await case.begin())
    assert reply.data.status == "failed", reply
    assert (await case.sdk.list_connections(**case.metadata("connection.list"))).data == ()


@pytest.mark.parametrize(
    "change",
    [
        {"unionId": None},
        {"unionId": ""},
        {"unionId": True},
        {"unionId": "bad\nvalue"},
        {"nick": ""},
        {"nick": 42},
        {"nick": "bad\nvalue"},
    ],
)
async def test_identity_requires_stable_id(case, change):
    case.vendor.profile_change = change
    assert (await case.complete(await case.begin())).data.status == "failed"


async def test_refresh_serialization_and_persistence(case):
    case.vendor.expires = 1
    connection = await case.connect()
    await case.stop()
    await case.reopen()
    await asyncio.sleep(1.05)
    results = await asyncio.gather(
        *(case.invoke(connection, "get_current_user", {}) for _ in range(4))
    )
    assert all(r.status == "succeeded" for r in results), results
    assert case.vendor.generation == 2
    await case.stop()
    await case.reopen()
    assert (await case.invoke(connection, "get_current_user", {})).status == "succeeded"
    assert case.vendor.generation == 2


async def test_explicitly_repeated_refresh_material_is_supported(case):
    case.vendor.expires = 1
    connection = await case.connect()
    await asyncio.sleep(1.05)
    case.vendor.token_change = {"refreshToken": "dt-refresh-1"}
    assert (await case.invoke(connection, "get_current_user", {})).status == "succeeded"


@pytest.mark.parametrize("mode", ["lost", "invalid", "missing_refresh", "http_400", "http_503"])
async def test_unknown_refresh_blocks_old_material_reuse(case, mode):
    case.vendor.expires = 1
    connection = await case.connect()
    await asyncio.sleep(1.05)

    async def inject(request):
        if request.url.path == TOKEN:
            if mode == "lost":
                raise httpx.ReadError("private-refresh-body")
            if mode == "invalid":
                return httpx.Response(200, content=b"null")
            if mode == "missing_refresh":
                return response({"accessToken": "new-access", "expireIn": 7200})
            return response(
                {"code": "invalid_client", "message": "private"}, 400 if mode == "http_400" else 503
            )

    case.vendor.inject = inject
    before = len(case.vendor.calls)
    for _ in range(2):
        assert (await case.invoke(connection, "get_current_user", {})).status == "failed"
    assert len(case.vendor.calls) == before + 1
    live = await case.sdk.get_connection(
        connection.connection_id,
        **case.metadata("connection.read", connection_id=str(connection.connection_id)),
    )
    assert live.data.status == "requires_reauthorization"


async def test_granted_scopes_are_not_fabricated_and_refresh_is_projected():
    value = Protocol().business_credential(
        OAuthCredential(access_token="private-access", refresh_token="private-refresh")
    )
    assert not hasattr(value, "refresh_token") and value.scope is None


async def test_logs_public_results_and_storage_omit_secrets(case, caplog):
    caplog.set_level(logging.DEBUG)
    connection = await case.connect()

    async def inject(request):
        if request.url.path == PROFILE:
            return response({"message": "private-vendor-body"}, 403)

    case.vendor.inject = inject
    reply = await case.invoke(connection, "get_current_user", {})
    assert reply.status == "failed" and "dingtalk_access_denied" in caplog.text
    for value in ("test-secret", "test-code", "dt-access-1", "dt-refresh-1", "private-vendor-body"):
        assert value not in caplog.text + repr(reply)
        assert all(
            value.encode() not in p.read_bytes()
            for p in (case.root / "data").rglob("*")
            if p.is_file()
        )
