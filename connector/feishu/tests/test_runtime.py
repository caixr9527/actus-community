import asyncio
import logging
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from vendor import SCOPES, TOKEN_URL, ok


async def test_oauth_s256_identity_replay_restart_disconnect(case):
    manifest = case.declaration.manifest
    assert manifest.id == "feishu" and len(manifest.operations) == 12
    assert {op.name for op in manifest.operations if op.effects == "write"} == {
        "create_record", "update_record"}
    view = await case.begin()
    query = parse_qs(urlsplit(view.authorization_url).query)
    assert urlsplit(view.authorization_url).hostname == "accounts.feishu.cn"
    assert query["code_challenge_method"] == ["S256"]
    assert set(query["scope"][0].split()) == set(SCOPES.split())
    assert (await case.complete(view, state="wrong")).status == "failed"
    assert not case.vendor.tokens
    saved = await case.complete(view)
    assert saved.data.status == "connected", saved
    connection = saved.data.connection
    assert connection.identity.account_id == "ou_person"
    assert connection.identity.tenant_id == "tenant1"
    assert (await case.complete(view)).data == saved.data
    assert len(case.vendor.tokens) == 1
    await case.stop()
    await case.reopen()
    assert (await case.invoke(connection, "read_document", {"document_id": "doc1"})).status \
        == "succeeded"
    reply = await case.sdk.disconnect(connection.connection_id,
        expected_revision=connection.revision,
        **case.metadata("connection.disconnect", connection_id=str(connection.connection_id)))
    assert reply.data.status == "disconnected"
    assert reply.data.revocation.status == "not_attempted"
    assert (await case.invoke(connection, "list_wiki_spaces", {})).status == "failed"


async def test_users_cannot_share_transactions_or_connections(case):
    view = await case.begin()
    assert (await case.complete(view, user="user-B")).status == "failed"
    assert not case.vendor.tokens
    connection = await case.connect()
    before = len(case.vendor.calls)
    assert (await case.invoke(connection, "list_wiki_spaces", {}, user="user-B")).status == "failed"
    assert len(case.vendor.calls) == before


@pytest.mark.parametrize("change", [
    {"access_token": ""}, {"access_token": "secret\nvalue"}, {"refresh_token": None},
    {"expires_in": True}, {"expires_in": 0}, {"expires_in": 367 * 86400},
    {"refresh_token_expires_in": None}, {"refresh_token_expires_in": -1},
    {"token_type": "Basic"}, {"scope": None}, {"scope": "bitable:app"},
    {"code": True}, {"error": "invalid_grant"},
])
async def test_invalid_token_never_saves_connection(case, change):
    case.vendor.token_change = change
    reply = await case.complete(await case.begin())
    assert reply.data.status == "failed", reply
    assert (await case.sdk.list_connections(**case.metadata("connection.list"))).data == ()


@pytest.mark.parametrize("change", [
    {"open_id": ""}, {"open_id": 9}, {"tenant_key": None}, {"name": 5},
])
async def test_identity_requires_real_person_and_tenant_identifiers(case, change):
    case.vendor.profile_change = change
    assert (await case.complete(await case.begin())).data.status == "failed"


async def test_partial_grants_do_not_authorize_other_operations(case):
    case.vendor.scope = "offline_access docx:document:readonly"
    connection = await case.connect()
    assert (await case.invoke(connection, "read_document", {"document_id": "doc1"})).status \
        == "succeeded"
    before = len(case.vendor.calls)
    assert (await case.invoke(connection, "list_wiki_spaces", {})).status == "failed"
    assert len(case.vendor.calls) == before


async def test_refresh_rotation_serialized_and_persisted(case):
    case.vendor.expires = 1
    connection = await case.connect()
    await case.stop()
    await case.reopen()
    await asyncio.sleep(1.05)
    replies = await asyncio.gather(*(case.invoke(connection, "list_wiki_spaces", {})
                                    for _ in range(4)))
    assert all(reply.status == "succeeded" for reply in replies), replies
    assert case.vendor.generation == 2
    assert [form["grant_type"] for form in case.vendor.tokens] == [
        "authorization_code", "refresh_token"]
    assert set(case.vendor.tokens[1]) == {
        "grant_type", "client_id", "client_secret", "refresh_token"}
    await case.stop()
    await case.reopen()
    assert (await case.invoke(connection, "list_wiki_spaces", {})).status == "succeeded"
    assert case.vendor.generation == 2


@pytest.mark.parametrize("status,code,expected", [
    (400, 20002, "active"), (503, 20002, "requires_reauthorization"),
    (429, 20002, "requires_reauthorization"), (400, 20073, "requires_reauthorization"),
    (400, 20037, "requires_reauthorization"),
])
async def test_refresh_failure_never_dispatches_business(case, status, code, expected):
    case.vendor.expires = 1
    connection = await case.connect()
    await asyncio.sleep(1.05)

    async def inject(request):
        if str(request.url) == TOKEN_URL:
            return httpx.Response(status, json={"code": code, "error": "invalid_client"})

    case.vendor.inject = inject
    before = len(case.vendor.calls)
    assert (await case.invoke(connection, "list_wiki_spaces", {})).status == "failed"
    assert all(str(r.url) == TOKEN_URL for r in case.vendor.calls[before:])
    live = await case.sdk.get_connection(connection.connection_id,
        **case.metadata("connection.read", connection_id=str(connection.connection_id)))
    assert live.data.status == expected


async def test_refresh_scope_reduction_stops_stale_capability_dispatch(case):
    case.vendor.expires = 1
    connection = await case.connect()
    case.vendor.scope = "offline_access docx:document:readonly"
    await asyncio.sleep(1.05)
    before = len(case.vendor.calls)
    assert (await case.invoke(connection, "list_wiki_spaces", {})).status == "failed"
    assert case.vendor.generation == 2
    assert all(str(r.url) == TOKEN_URL for r in case.vendor.calls[before:])


async def test_credentials_and_vendor_error_bodies_do_not_leak(case, caplog):
    caplog.set_level(logging.DEBUG)
    connection = await case.connect()

    async def inject(request):
        if request.url.path.endswith("/raw_content"):
            return httpx.Response(200, json={"code": 999, "msg": "secret-vendor-body"})

    case.vendor.inject = inject
    reply = await case.invoke(connection, "read_document", {"document_id": "doc1"})
    serialized = repr(reply) + caplog.text
    assert "feishu_business_failed" in caplog.text
    for value in ("test-secret", "access-1", "refresh-1", "test-code", "secret-vendor-body"):
        assert value not in serialized
        assert all(value.encode() not in p.read_bytes() for p in (case.root / "data").rglob("*")
                   if p.is_file())


async def test_empty_document_is_a_valid_plain_text_result(case):
    connection = await case.connect()

    async def inject(request):
        if request.url.path.endswith("/raw_content"):
            return ok({"content": ""})

    case.vendor.inject = inject
    reply = await case.invoke(connection, "read_document", {"document_id": "doc1"})
    assert reply.data["data"]["content"] == ""
    assert reply.data["data"]["format"] == "plain_text"


@pytest.mark.parametrize("change", [
    {"refresh_token": "refresh-1"}, {"refresh_token": None},
    {"refresh_token_expires_in": 0},
])
async def test_missing_or_reused_rotating_refresh_result_is_never_replayed(case, change):
    case.vendor.expires = 1
    connection = await case.connect()
    case.vendor.token_change = change
    await asyncio.sleep(1.05)
    before = len(case.vendor.calls)
    assert (await case.invoke(connection, "list_wiki_spaces", {})).status == "failed"
    assert len(case.vendor.calls) == before + 1
    assert str(case.vendor.calls[-1].url) == TOKEN_URL
    assert (await case.invoke(connection, "list_wiki_spaces", {})).status == "failed"
    assert len(case.vendor.calls) == before + 1
