import asyncio
import json
import logging
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest


async def test_oauth_manifest_replay_restart_disconnect(case):
    manifest = case.declaration.manifest
    assert manifest.id == "baidu-netdisk" and len(manifest.operations) == 12
    assert sum(op.effects == "write" for op in manifest.operations) == 6
    view = await case.begin()
    query = parse_qs(urlsplit(view.authorization_url).query)
    assert query["scope"] == ["basic,netdisk"] and "code_challenge" not in query
    assert query["client_id"] == ["test-client"]
    assert (await case.complete(view, state="wrong")).status == "failed"
    assert not case.vendor.tokens
    saved = await case.complete(view)
    assert saved.data.status == "connected" and saved.data.connection.identity.account_id == "456"
    assert saved.data.connection.identity.display_name == "测试账号"
    assert (await case.complete(view)).data == saved.data and len(case.vendor.tokens) == 1
    connection = saved.data.connection
    await case.stop()
    await case.reopen()
    reply = await case.invoke(connection, "get_quota", {})
    assert reply.status == "succeeded" and reply.data["free_bytes"] == 51
    closed = await case.sdk.disconnect(connection.connection_id,
        expected_revision=connection.revision,
        **case.metadata("connection.disconnect", connection_id=str(connection.connection_id)))
    assert closed.data.status == "disconnected" and closed.data.revocation.status == "not_attempted"
    assert (await case.invoke(connection, "get_quota", {})).status == "failed"
    assert len(case.vendor.tokens) == 1


async def test_authorization_and_connection_cannot_cross_users(case):
    view = await case.begin()
    assert (await case.complete(view, user="user-B")).status == "failed"
    assert not case.vendor.tokens
    connection = await case.connect()
    before = len(case.vendor.calls)
    result = await case.invoke(connection, "get_quota", {}, user="user-B")
    assert result.status == "failed" and len(case.vendor.calls) == before


@pytest.mark.parametrize("change", [
    {"access_token": ""}, {"refresh_token": None}, {"expires_in": True},
    {"expires_in": 0}, {"expires_in": 367 * 86400}, {"scope": "basic"},
    {"scope": ["basic", "netdisk"]}, {"access_token": "secret\nvalue"},
])
async def test_invalid_tokens_never_create_connection(case, change):
    case.vendor.token_change = change
    result = await case.complete(await case.begin())
    assert result.data.status == "failed"
    connections = await case.sdk.list_connections(**case.metadata("connection.list"))
    assert connections.data == ()


async def test_missing_token_type_comma_scopes_and_additional_grants(case):
    case.vendor.token_change = {"scope": "basic,netdisk,extra"}
    assert (await case.connect()).identity.account_id == "456"


async def test_directory_without_md5_and_semantic_parent_path_are_preserved(case):
    connection = await case.connect()

    async def inject(request):
        if request.url.params.get("method") == "list":
            return httpx.Response(200, json={"errno": 0, "list": [{
                "fs_id": 99, "server_filename": "目录", "path": "/目录", "isdir": 1,
                "md5": "", "parent_path": "/"}]})

    case.vendor.inject = inject
    reply = await case.invoke(connection, "list_files", {})
    assert reply.status == "succeeded"
    assert reply.data["files"][0]["parent_path"] == "/"
    assert reply.data["files"][0]["md5"] is None


@pytest.mark.parametrize("operation,params,payload,field", [
    ("get_quota", {}, {"errno": 0, "total": 100, "used": 40, "free": 51},
     "expires_within_seven_days"),
    ("search_files", {"query": "a"}, {"errno": 0, "list": []}, "has_more"),
    ("semantic_search", {"query": "a"}, {"error_no": 0, "data": []}, "has_more"),
])
async def test_missing_vendor_flags_remain_unknown(case, operation, params, payload, field):
    connection = await case.connect()

    async def inject(request):
        if request.url.params.get("method") != "uinfo":
            return httpx.Response(200, json=payload)

    case.vendor.inject = inject
    reply = await case.invoke(connection, operation, params)
    assert reply.status == "succeeded" and reply.data[field] is None


JSON_CASES = [
    ("list_files", {}, "list"),
    ("search_files", {"query": "测试"}, "search"),
    ("get_quota", {}, None),
    ("semantic_search", {"query": "发票", "category": 4}, None),
    ("get_file_metadata", {"fs_id": "123"}, "filemetas"),
    ("create_folder", {"path": "new"}, "create"),
    ("copy_file", {"source_path": "/old", "destination_directory": "/new",
                   "new_name": "copy", "conflict_policy": "overwrite"}, "filemanager"),
    ("move_file", {"source_path": "/old", "destination_directory": "/new",
                   "new_name": "moved"}, "filemanager"),
    ("rename_file", {"path": "/old", "new_name": "renamed"}, "filemanager"),
    ("delete_file", {"path": "/old"}, "filemanager"),
]


@pytest.mark.parametrize("name,params,method", JSON_CASES)
async def test_all_json_operations_through_public_server(case, name, params, method):
    connection = await case.connect()
    reply = await case.invoke(connection, name, params)
    assert reply.status == "succeeded", reply
    last = case.vendor.calls[-1]
    assert last.url.params.get("method") == method
    encoded = json.dumps(reply.data)
    assert "must-not-be-returned" not in encoded and "dlink" not in encoded
    if method == "filemanager":
        form = parse_qs(last.content.decode())
        assert form["ondup"] == [params.get("conflict_policy", "fail")]


@pytest.mark.parametrize("name,params", [
    ("delete_file", {"path": "/"}), ("delete_file", {"path": "a/../b"}),
    ("list_files", {"path": "a//b"}), ("list_files", {"limit": True}),
    ("list_files", {"path": "a\\b"}), ("search_files", {"query": " "}),
    ("get_file_metadata", {"fs_id": "0"}), ("rename_file", {"path": "/a", "new_name": "../b"}),
    ("copy_file", {"source_path": "/", "destination_directory": "/a", "new_name": "b"}),
])
async def test_invalid_input_stops_before_vendor(case, name, params):
    connection = await case.connect()
    before = len(case.vendor.calls)
    assert (await case.invoke(connection, name, params)).status == "failed"
    assert len(case.vendor.calls) == before


async def test_rotation_is_serialized_persisted_and_invalid_grant_stops_dispatch(case):
    case.vendor.expires = 1
    connection = await case.connect()
    await case.stop()
    await case.reopen()
    await asyncio.sleep(1.05)
    replies = await asyncio.gather(*(case.invoke(connection, "get_quota", {}) for _ in range(4)))
    assert all(r.status == "succeeded" for r in replies)
    assert case.vendor.generation == 2
    case.vendor.refresh_fail = True
    await case.stop()
    await case.reopen()
    await asyncio.sleep(1.05)
    before = len(case.vendor.calls)
    assert (await case.invoke(connection, "get_quota", {})).status == "failed"
    assert all(r.url.host == "openapi.baidu.com" for r in case.vendor.calls[before:])
    live = await case.sdk.get_connection(connection.connection_id,
        **case.metadata("connection.read", connection_id=str(connection.connection_id)))
    assert live.data.status == "requires_reauthorization"


@pytest.mark.parametrize("status,expected", [
    (503, "requires_reauthorization"), (429, "requires_reauthorization"), (400, "active"),
])
async def test_refresh_http_failure_is_not_mistaken_for_definite_client_rejection(
    case, status, expected,
):
    case.vendor.expires = 1
    connection = await case.connect()
    await asyncio.sleep(1.05)

    async def inject(request):
        if request.url.params.get("grant_type") == "refresh_token":
            return httpx.Response(status, json={"error": "invalid_client"})

    case.vendor.inject = inject
    before = len(case.vendor.calls)
    reply = await case.invoke(connection, "get_quota", {})
    assert reply.status == "failed"
    live = await case.sdk.get_connection(connection.connection_id,
        **case.metadata("connection.read", connection_id=str(connection.connection_id)))
    assert live.data.status == expected
    if expected == "requires_reauthorization":
        assert (await case.invoke(connection, "get_quota", {})).status == "failed"
    assert len(case.vendor.calls) == before + 1


@pytest.mark.parametrize("mode", ["lost_reply", "bad_payload", "vendor_failure"])
async def test_write_uncertainty_never_retries_or_echoes_raw_error(case, mode):
    connection = await case.connect()

    async def inject(request):
        if request.url.params.get("method") != "filemanager":
            return None
        if mode == "lost_reply":
            raise httpx.ReadError("private-vendor-secret")
        if mode == "bad_payload":
            return httpx.Response(200, json={"private-vendor-secret": True})
        return httpx.Response(200, json={"errno": -6, "errmsg": "private-vendor-secret"})

    case.vendor.inject = inject
    before = len(case.vendor.calls)
    reply = await case.invoke(connection, "delete_file", {"path": "/a"})
    assert reply.status == "uncertain" and len(case.vendor.calls) == before + 1
    assert "private-vendor-secret" not in repr(reply)


async def test_query_secrets_do_not_enter_debug_logs_or_plain_store(case, caplog):
    caplog.set_level(logging.DEBUG)
    connection = await case.connect()
    assert (await case.invoke(connection, "get_quota", {})).status == "succeeded"
    for secret in ("test-secret", "test-code", "access-1", "refresh-1"):
        assert secret not in caplog.text
        for file in (case.root / "data").rglob("*"):
            if file.is_file():
                assert secret.encode() not in file.read_bytes()
