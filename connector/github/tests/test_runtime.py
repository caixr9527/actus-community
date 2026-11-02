import asyncio
import logging
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest


async def test_oauth_identity_replay_restart_and_local_disconnect(case):
    manifest = case.declaration.manifest
    assert manifest.id == "github" and len(manifest.operations) == 13
    assert {op.name for op in manifest.operations if op.effects == "write"} == {
        "create_issue",
        "update_issue",
        "create_issue_comment",
    }
    view = await case.begin()
    query = parse_qs(urlsplit(view.authorization_url).query)
    assert query["scope"] == ["offline_access"] and query["code_challenge_method"] == ["S256"]
    assert (await case.complete(view, state="wrong")).status == "failed"
    assert not case.vendor.tokens
    saved = await case.complete(view)
    assert saved.data.status == "connected", saved
    connection = saved.data.connection
    assert connection.identity.account_id == "42" and connection.identity.tenant_id is None
    assert connection.capabilities is None
    assert (await case.complete(view)).data == saved.data and len(case.vendor.tokens) == 1
    await case.stop()
    await case.reopen()
    assert (await case.invoke(connection, "list_installations", {})).status == "succeeded"
    reply = await case.sdk.disconnect(
        connection.connection_id,
        expected_revision=connection.revision,
        **case.metadata("connection.disconnect", connection_id=str(connection.connection_id)),
    )
    assert reply.data.revocation.status == "not_attempted"
    assert (await case.invoke(connection, "list_installations", {})).status == "failed"


async def test_cross_user_transactions_and_connections_rejected(case):
    view = await case.begin()
    assert (await case.complete(view, user="user-B")).status == "failed"
    assert not case.vendor.tokens
    connection = await case.connect()
    before = len(case.vendor.calls)
    assert (
        await case.invoke(connection, "list_installations", {}, user="user-B")
    ).status == "failed"
    assert len(case.vendor.calls) == before


@pytest.mark.parametrize(
    "change",
    [
        {"access_token": "ghp_classic"},
        {"access_token": "ghu_\nsecret"},
        {"refresh_token": None},
        {"refresh_token": "ghr_"},
        {"token_type": "Basic"},
        {"expires_in": True},
        {"expires_in": 0},
        {"expires_in": 367 * 86400},
        {"refresh_token_expires_in": None},
        {"refresh_token_expires_in": -1},
        {"scope": "repo"},
        {"scope": None},
        {"error": "bad_verification_code"},
    ],
)
async def test_bad_token_responses_never_create_connection(case, change):
    case.vendor.token_change = change
    assert (await case.complete(await case.begin())).data.status == "failed"
    assert (await case.sdk.list_connections(**case.metadata("connection.list"))).data == ()


@pytest.mark.parametrize(
    "change",
    [
        {"id": True},
        {"id": 0},
        {"login": ""},
        {"login": None},
        {"type": "Bot"},
    ],
)
async def test_identity_requires_stable_user_id(case, change):
    case.vendor.profile_change = change
    assert (await case.complete(await case.begin())).data.status == "failed"


async def test_rotation_serializes_and_survives_restart(case):
    case.vendor.expires = 1
    connection = await case.connect()
    await case.stop()
    await case.reopen()
    await asyncio.sleep(1.05)
    replies = await asyncio.gather(
        *(case.invoke(connection, "list_installations", {}) for _ in range(4))
    )
    assert all(r.status == "succeeded" for r in replies), replies
    assert case.vendor.generation == 2
    await case.stop()
    await case.reopen()
    assert (await case.invoke(connection, "list_installations", {})).status == "succeeded"
    assert case.vendor.generation == 2


@pytest.mark.parametrize(
    "status,error,expected",
    [
        (200, "incorrect_client_credentials", "active"),
        (400, "incorrect_client_credentials", "active"),
        (503, "incorrect_client_credentials", "requires_reauthorization"),
        (429, "incorrect_client_credentials", "requires_reauthorization"),
        (200, "bad_refresh_token", "requires_reauthorization"),
    ],
)
async def test_refresh_error_never_reaches_business(case, status, error, expected):
    case.vendor.expires = 1
    connection = await case.connect()
    await asyncio.sleep(1.05)

    async def inject(request):
        if request.url.host == "github.com":
            return httpx.Response(status, json={"error": error, "error_description": "private"})

    case.vendor.inject = inject
    before = len(case.vendor.calls)
    assert (await case.invoke(connection, "list_installations", {})).status == "failed"
    assert len(case.vendor.calls) == before + 1
    live = await case.sdk.get_connection(
        connection.connection_id,
        **case.metadata("connection.read", connection_id=str(connection.connection_id)),
    )
    assert live.data.status == expected
    if expected != "active":
        assert (await case.invoke(connection, "list_installations", {})).status == "failed"
        assert len(case.vendor.calls) == before + 1


@pytest.mark.parametrize(
    "change",
    [
        {"refresh_token": "ghr_1"},
        {"refresh_token": None},
        {"refresh_token_expires_in": 0},
    ],
)
async def test_unknown_rotation_result_blocks_reuse(case, change):
    case.vendor.expires = 1
    connection = await case.connect()
    case.vendor.token_change = change
    await asyncio.sleep(1.05)
    before = len(case.vendor.calls)
    for _ in range(2):
        assert (await case.invoke(connection, "list_installations", {})).status == "failed"
    assert len(case.vendor.calls) == before + 1


async def test_log_and_storage_do_not_expose_credentials_or_vendor_errors(case, caplog):
    caplog.set_level(logging.DEBUG)
    connection = await case.connect()

    async def inject(request):
        if request.url.path == "/user/installations":
            return httpx.Response(403, json={"message": "private-vendor-body"})

    case.vendor.inject = inject
    reply = await case.invoke(connection, "list_installations", {})
    assert reply.status == "failed" and "github_access_denied" in caplog.text
    for value in ("ghu_1", "ghr_1", "test-secret", "test-code", "private-vendor-body"):
        assert value not in caplog.text + repr(reply)
        assert all(
            value.encode() not in p.read_bytes()
            for p in (case.root / "data").rglob("*")
            if p.is_file()
        )
