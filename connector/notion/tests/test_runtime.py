import asyncio
from urllib.parse import parse_qs, urlsplit

import pytest
from connector_sdk import AuthorizationError

from notion_connector.protocol import TOOLS


async def connect(case):
    result = await case.complete(await case.begin())
    assert result.status == "connected", result
    return result.connection


async def test_manifest_pkce_identity_restart_and_revoke(case):
    manifest = case.declaration.manifest
    assert manifest.id == "notion" and len(manifest.operations) == 12
    assert sum(op.effects == "write" for op in manifest.operations) == 5
    assert manifest.auth.type == "oauth2"
    view = await case.begin()
    query = parse_qs(urlsplit(view.authorization_url).query)
    assert query["code_challenge_method"] == ["S256"] and query["scope"] == ["default"]
    assert query["client_id"] == ["registered-client"] and not case.vendor.calls
    with pytest.raises(AuthorizationError):
        await case.complete(view, iss="https://wrong.test")
    assert not case.vendor.forms
    result = await case.complete(view)
    connection = result.connection
    assert connection.identity.account_id == "Person RAW"
    assert connection.identity.tenant_id == "Workspace RAW"
    assert connection.identity.display_name is None
    assert connection.capabilities == {}
    assert await case.complete(view) == result
    assert len(case.vendor.forms) == 1
    await case.runtime.close()
    await case.reopen()
    called = await case.invoke(connection, "search", {"query": "hello"})
    assert called.status == "succeeded" and "中文" in called.data["data"]["text"]
    disconnected = await case.runtime.disconnect(
        connection.connection_id, expected_revision=connection.revision,
        **case.metadata("connection.disconnect", connection_id=str(connection.connection_id)))
    assert disconnected.status == "disconnected" and disconnected.revocation.status == "accepted"
    assert len(case.vendor.revocations) == 1 and case.vendor.closed >= 2


@pytest.mark.parametrize("change", [
    {"user": {"id": "bot", "type": "bot"}},
    {"user": {"id": " ", "type": "person"}},
    {"workspace": {"id": ""}}, {"workspace": None},
])
async def test_untrusted_identity_never_saves_connection(case, change):
    case.vendor.identity.update(change)
    assert (await case.complete(await case.begin())).status == "failed"
    assert not await case.runtime.list_connections(**case.metadata("connection.list"))


CASES = [
    ("search", {"query": "Q"}, {"query": "Q"}),
    ("fetch", {"id": "page"}, {"id": "page"}),
    ("get_users", {"start_cursor": "cursor RAW", "page_size": 2},
     {"start_cursor": "cursor RAW", "page_size": 2}),
    ("get_teams", {}, {}),
    ("get_comments", {"page_id": "p", "include_resolved": False},
     {"page_id": "p", "include_resolved": False}),
    ("query_database_view", {"view_url": "view", "include_archived": False},
     {"mode": "view", "view_url": "view", "is_archived": False}),
    ("get_async_task", {"task_id": "t"}, {"task_id": "t"}),
    ("create_page", {"parent_id": "p", "title": "Title"},
     {"pages": [{"properties": {"title": "Title"}, "content": ""}], "parent": {"page_id": "p"}}),
    ("update_page", {"page_id": "p", "content": "new"},
     {"page_id": "p", "command": "replace_content", "new_str": "new"}),
    ("create_comment", {"page_id": "p", "markdown": "hello"},
     {"page_id": "p", "markdown": "hello"}),
    ("move_pages", {"page_or_database_ids": ["p"], "parent_type": "workspace"},
     {"page_or_database_ids": ["p"], "new_parent": {"type": "workspace"}}),
    ("duplicate_page", {"page_id": "p"}, {"page_id": "p"}),
]


@pytest.mark.parametrize("name,params,expected", CASES)
async def test_twelve_explicit_tools_with_actual_runtime(case, name, params, expected):
    connection = await connect(case)
    assert (await case.invoke(connection, name, params)).status == "succeeded"
    assert case.vendor.calls[-1]["params"] == {"name": TOOLS[name], "arguments": expected}


async def test_live_schema_permission_and_polling_reject_before_write(case):
    connection = await connect(case)
    case.vendor.tools[TOOLS["create_page"]] = {
        "type": "object", "properties": {"new_required": {"type": "string"}},
        "required": ["new_required"]}
    before = len(case.vendor.calls)
    result = await case.invoke(connection, "create_page", {"parent_id": "p", "title": "T"})
    assert result.status == "failed" and result.error.code == "operation_failed"
    assert not any(c.get("params", {}).get("name") == TOOLS["create_page"]
                   for c in case.vendor.calls[before:])
    del case.vendor.tools[TOOLS["get_async_task"]]
    assert (await case.invoke(connection, "duplicate_page", {"page_id": "p"})).status == "failed"
    case.vendor.tools["notion-get-tool-access"] = {"type": "object"}
    case.vendor.access = {"create_comment": {"status": "not_enabled"}}
    assert (await case.invoke(connection, "create_comment", {
        "page_id": "p", "markdown": "hello"})).status == "failed"


@pytest.mark.parametrize("params", [
    {"view_url": "v", "sql": "SELECT 1"}, {"view_url": ""},
    {"view_url": "v", "page_size": 101},
])
async def test_invalid_local_input_never_reaches_vendor(case, params):
    connection = await connect(case)
    before = len(case.vendor.calls)
    assert (await case.invoke(connection, "query_database_view", params)).status == "failed"
    assert len(case.vendor.calls) == before


@pytest.mark.parametrize("result", [
    {"isError": True, "content": [{"type": "text", "text": "private-vendor-error"}]},
    {"content": [{"type": "text", "text": "x" * (256 * 1024)}]},
    {"structuredContent": []},
])
async def test_write_errors_are_not_rejections_or_empty_success(case, result):
    connection = await connect(case)
    case.vendor.result = result
    reply = await case.invoke(connection, "create_page", {"parent_id": "p", "title": "T"})
    assert reply.status == "uncertain" and "private-vendor-error" not in repr(reply)
    assert sum(c.get("params", {}).get("name") == TOOLS["create_page"]
               for c in case.vendor.calls) == 1


async def test_cleanup_failure_preserves_write_success(case, caplog):
    connection = await connect(case)
    case.vendor.cleanup_fail = True
    assert (await case.invoke(connection, "duplicate_page", {"page_id": "p"})).status == "succeeded"
    assert "notion_session_close_failed" in caplog.text


async def test_rotation_concurrency_restart_and_invalid_grant(case):
    case.vendor.expires = 1
    connection = await connect(case)
    await case.runtime.close()
    await case.reopen()
    case.vendor.expires = 3600
    await asyncio.sleep(1.1)
    replies = await asyncio.gather(*(case.invoke(connection, "get_teams", {}) for _ in range(5)))
    assert all(r.status == "succeeded" for r in replies)
    assert case.vendor.generation == 2
    await case.runtime.close()
    await case.reopen()
    live = await case.runtime.get_connection(
        connection.connection_id,
        **case.metadata("connection.read", connection_id=str(connection.connection_id)))
    disconnected = await case.runtime.disconnect(
        connection.connection_id, expected_revision=live.revision,
        **case.metadata("connection.disconnect", connection_id=str(connection.connection_id)))
    assert disconnected.revocation.status == "accepted"
    assert case.vendor.revocations[0]["token"] == "refresh-2"


async def test_refresh_failure_blocks_business_dispatch(case):
    case.vendor.expires = 1
    connection = await connect(case)
    case.vendor.refresh_fail = True
    await asyncio.sleep(1.1)
    before = len(case.vendor.calls)
    result = await case.invoke(connection, "get_teams", {})
    assert result.status == "failed" and len(case.vendor.calls) == before
    live = await case.runtime.get_connection(
        connection.connection_id,
        **case.metadata("connection.read", connection_id=str(connection.connection_id)))
    assert live.status == "requires_reauthorization"


@pytest.mark.parametrize("params", [
    {"page_or_database_ids": ["p"], "parent_type": "page_id"},
    {"page_or_database_ids": ["p"], "parent_type": "workspace", "parent_id": "p"},
    {"page_or_database_ids": [], "parent_type": "workspace"},
])
async def test_invalid_move_parent_never_dispatches(case, params):
    connection = await connect(case)
    before = len(case.vendor.calls)
    result = await case.invoke(connection, "move_pages", params)
    assert result.status == "failed" and len(case.vendor.calls) == before
