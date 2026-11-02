import asyncio
import json

import httpx
import pytest
from vendor import DOC, STAMP, reply

NEW = {"repository_id": "10", "title": "复核", "body": "# 标题\n新正文"}
CHANGE = {
    "repository_id": "10",
    "document_id": "100",
    "expected_updated_at": STAMP,
    "title": "修改",
}
CASES = [
    ("get_current_user", {}),
    ("list_groups", {}),
    ("list_repositories", {}),
    ("get_repository", {"repository_id": "10"}),
    ("list_documents", {"repository_id": "10"}),
    ("get_document", {"repository_id": "10", "document_id": "100"}),
    ("search", {"query": "测试"}),
    ("create_document", NEW),
    ("update_document", CHANGE),
]


@pytest.mark.parametrize("name,params", CASES)
async def test_nine_operations_project_outputs_and_validate_receipts(case, name, params):
    connection = await case.connect()
    result = await case.invoke(connection, name, params)
    assert result.status == "succeeded", result
    for marker in (
        "private-email",
        "private-member",
        "private-derived-body",
        "private-vendor-field",
        "body_draft",
        "body_html",
    ):
        assert marker not in repr(result)
    if name in {"create_document", "update_document"}:
        assert result.data["accepted"] is True and result.data["content_verified"] is False
        assert len(case.vendor.writes) == 1


@pytest.mark.parametrize(
    "name,params",
    [
        ("list_repositories", {"owner_kind": "group", "group_id": "7"}),
        ("search", {"query": "x", "type": "repo", "scope": "team"}),
        ("search", {"query": "x", "scope": "team/manual"}),
    ],
)
async def test_team_and_search_paths(case, name, params):
    result = await case.invoke(await case.connect(), name, params)
    assert result.status == "succeeded", result
    request = case.vendor.calls[-1]
    if name == "list_repositories":
        assert request.url.path == "/api/v2/groups/7/repos"
    else:
        assert request.url.params["scope"] == params["scope"]
        assert result.data["items"][0]["title"] == "测试标题"


@pytest.mark.parametrize(
    "name,params",
    [
        ("get_repository", {"repository_id": x})
        for x in [
            0,
            True,
            10.0,
            "0",
            "-1",
            "01",
            "../user",
            "https://evil.test",
            "9223372036854775808",
        ]
    ]
    + [
        ("create_document", NEW | {"title": ""}),
        ("create_document", NEW | {"title": " "}),
        ("create_document", NEW | {"title": "x" * 257}),
        ("create_document", NEW | {"title": "a\nb"}),
        ("create_document", NEW | {"body": ""}),
        ("create_document", NEW | {"body": "x\u0000"}),
        ("create_document", NEW | {"body": "中" * 90_000}),
        ("create_document", NEW | {"public": 1}),
        ("create_document", NEW | {"format": "lake"}),
        ("create_document", NEW | {"url": "https://evil.test"}),
        ("update_document", {k: v for k, v in CHANGE.items() if k != "title"}),
        ("update_document", CHANGE | {"title": None}),
        ("update_document", CHANGE | {"body": None}),
        ("update_document", CHANGE | {"slug": "other"}),
        ("update_document", CHANGE | {"expected_updated_at": "2026-11-02T01:00:00"}),
        ("update_document", CHANGE | {"expected_updated_at": "2026-02-30T01:00:00Z"}),
        ("update_document", CHANGE | {"expected_updated_at": "2026-11-02T01:00:00-00:00"}),
        ("update_document", CHANGE | {"expected_updated_at": "2026-11-02T01:00:00+08:99"}),
        ("list_groups", {"limit": 20}),
        ("list_groups", {"offset": -1}),
        ("list_documents", {"repository_id": "10", "limit": 101}),
        ("list_repositories", {"owner_kind": "group"}),
        ("list_repositories", {"group_id": "7"}),
        ("list_repositories", {"host": "https://other.yuque.com"}),
        ("search", {"query": ""}),
        ("search", {"query": "x" * 201}),
        ("search", {"query": "x", "page": 101}),
        ("search", {"query": "x", "scope": "../x"}),
        ("search", {"query": "x", "scope": "https://evil.test"}),
        ("search", {"query": "x", "scope": "a/b", "type": "repo"}),
        ("search", {"query": "x", "page": True}),
        ("get_current_user", {"extra": True}),
    ],
)
async def test_invalid_input_rejected_before_http(case, name, params):
    connection = await case.connect()
    count = len(case.vendor.calls)
    assert (await case.invoke(connection, name, params)).status == "failed"
    assert len(case.vendor.calls) == count


@pytest.mark.parametrize(
    "change",
    [
        {"type": "Sheet"},
        {"format": "lake"},
        {"format": "html"},
        {"format": None},
        {"public": None},
        {"public": True},
        {"updated_at": None},
        {"updated_at": "2026-11-02T03:00:00Z"},
        {"id": 101},
        {"book_id": 11},
        {"body_draft": "别人的草稿"},
        {"body_draft": {}},
        {"body": None},
        {"body": "x" * (256 * 1024 + 1)},
    ],
)
async def test_update_preflight_never_writes_unsupported_or_changed_document(case, change):
    connection = await case.connect()
    case.vendor.document.update(change)
    assert (await case.invoke(connection, "update_document", CHANGE)).status == "failed"
    assert not case.vendor.writes


@pytest.mark.parametrize("name,params", CASES[-2:])
@pytest.mark.parametrize("kind", ["Design", "Sheet", "Resource", None])
async def test_only_document_knowledge_base_is_writable(case, name, params, kind):
    connection = await case.connect()
    case.vendor.repository["type"] = kind
    assert (await case.invoke(connection, name, params)).status == "failed"
    assert not case.vendor.writes


@pytest.mark.parametrize("public", [0, 1, 2])
async def test_title_only_update_preserves_visibility_body_and_slug(case, public):
    connection = await case.connect()
    case.vendor.document["public"] = public
    result = await case.invoke(connection, "update_document", CHANGE)
    assert result.status == "succeeded", result
    wire = json.loads(case.vendor.writes[-1].content)
    assert wire == {"title": "修改", "format": "markdown", "public": public}
    assert case.vendor.document["body"] == DOC["body"]
    assert case.vendor.document["slug"] == DOC["slug"]


async def test_body_update_is_explicit_replacement(case):
    connection = await case.connect()
    params = {k: v for k, v in CHANGE.items() if k != "title"} | {"body": "完整替换"}
    case.vendor.document["body_draft"] = DOC["body"]
    assert (await case.invoke(connection, "update_document", params)).status == "succeeded"
    assert json.loads(case.vendor.writes[-1].content) == {
        "body": "完整替换",
        "format": "markdown",
        "public": 0,
    }


@pytest.mark.parametrize("status", [400, 401, 403, 404, 422, 429, 500])
async def test_preflight_http_failure_never_writes(case, status):
    connection = await case.connect()

    async def inject(request):
        return httpx.Response(status, json={"message": "private-error"})

    case.vendor.inject = inject
    assert (await case.invoke(connection, "create_document", NEW)).status == "failed"
    assert not case.vendor.writes


@pytest.mark.parametrize("name,params", CASES[-2:])
@pytest.mark.parametrize("mode", ["lost", "http", "redirect", "error", "empty", "bad_receipt"])
async def test_sent_writes_stay_uncertain_and_are_not_retried(case, name, params, mode):
    connection = await case.connect()
    sent = []

    async def inject(request):
        if request.method in {"POST", "PUT"}:
            sent.append(request)
            if mode == "lost":
                raise httpx.ReadError("private-network-error")
            if mode == "http":
                return httpx.Response(503, json={"message": "private"})
            if mode == "redirect":
                return httpx.Response(307, headers={"Location": "https://evil.test"})
            if mode == "error":
                return httpx.Response(200, json={"error": "private", "data": DOC})
            if mode == "empty":
                return reply({})
            return reply(DOC | {"book_id": 99})

    case.vendor.inject = inject
    result = await case.invoke(connection, name, params)
    assert result.status == "uncertain", result
    assert len(sent) == 1 and "private" not in repr(result)


@pytest.mark.parametrize(
    "change",
    [
        {"public": 1},
        {"format": "lake"},
        {"title": "错误"},
        {"body": "错误"},
        {"id": 101},
        {"book_id": 11},
        {"slug": "changed"},
        {"updated_at": None},
    ],
)
async def test_mismatched_update_receipt_is_not_success(case, change):
    connection = await case.connect()

    async def inject(request):
        if request.method == "PUT":
            return reply(DOC | {"title": "修改"} | change)

    case.vendor.inject = inject
    assert (await case.invoke(connection, "update_document", CHANGE)).status == "uncertain"


@pytest.mark.parametrize(
    "mode", ["empty_unknown", "short_unknown", "full_unknown", "known_end", "known_more"]
)
async def test_paging_preserves_unknown_and_explicit_total(case, mode):
    connection = await case.connect()
    count = {
        "empty_unknown": 0,
        "short_unknown": 1,
        "full_unknown": 2,
        "known_end": 1,
        "known_more": 1,
    }[mode]

    async def inject(request):
        if request.url.path.endswith("/docs"):
            items = [DOC | {"id": 100 + i} for i in range(count)]
            return reply(
                items,
                meta={"total": 1 if mode == "known_end" else 2}
                if mode.startswith("known")
                else None,
            )

    case.vendor.inject = inject
    result = await case.invoke(connection, "list_documents", {"repository_id": "10", "limit": 2})
    assert result.status == "succeeded", result
    expected = {"known_end": False, "known_more": True}.get(mode)
    assert result.data["has_more"] is expected
    assert result.data["next_offset"] == (count if count and expected is not False else None)


@pytest.mark.parametrize(
    "data,meta",
    [
        ([DOC, DOC], None),
        ([DOC | {"book_id": 11}], None),
        ({}, None),
        ([DOC], {"total": True}),
        ([DOC], {"total": 0}),
        ([], {"total": 2}),
        ([DOC], {"total": -1}),
        ([DOC], []),
        ([DOC], {"total": "1"}),
    ],
)
async def test_malformed_pages_are_not_complete_results(case, data, meta):
    connection = await case.connect()

    async def inject(request):
        if request.url.path.endswith("/docs"):
            return reply(data, meta=meta)

    case.vendor.inject = inject
    assert (
        await case.invoke(connection, "list_documents", {"repository_id": "10"})
    ).status == "failed"


@pytest.mark.parametrize(
    "mode",
    [
        "wrong_page",
        "wrong_size",
        "bool_page",
        "wrong_type",
        "wrong_target",
        "evil_url",
        "userinfo_url",
        "protocol_url",
        "overfull",
    ],
)
async def test_search_contract_anomalies_rejected(case, mode):
    connection = await case.connect()

    async def inject(request):
        if request.url.path.endswith("/search"):
            item = {"id": 100, "type": "doc", "title": "<em>测试</em>", "target": DOC}
            meta = {"pageNo": 1, "pageSize": 20, "total": 1}
            if mode == "wrong_page":
                meta["pageNo"] = 2
            if mode == "bool_page":
                meta["pageNo"] = True
            if mode == "wrong_size":
                meta["pageSize"] = 100
            if mode == "wrong_type":
                item["type"] = "repo"
            if mode == "wrong_target":
                item["target"] = {"id": 99}
            if mode == "evil_url":
                item["url"] = "https://evil.test"
            if mode == "userinfo_url":
                item["url"] = "https://user@www.yuque.com/x"
            if mode == "protocol_url":
                item["url"] = "//evil.test/x"
            return reply([item] * (21 if mode == "overfull" else 1), meta=meta)

    case.vendor.inject = inject
    assert (await case.invoke(connection, "search", {"query": "x"})).status == "failed"


async def test_search_limit_is_not_reported_as_exhausted(case):
    connection = await case.connect()

    async def inject(request):
        if request.url.path.endswith("/search"):
            return reply(
                [{"id": 100, "type": "doc", "title": "x"}],
                meta={"total": 3000, "pageNo": 100, "pageSize": 20},
            )

    case.vendor.inject = inject
    result = await case.invoke(connection, "search", {"query": "x", "page": 100})
    assert result.status == "succeeded" and result.data["has_more"] is True
    assert result.data["next_page"] is None and result.data["page_limit_reached"] is True


@pytest.mark.parametrize(
    "body",
    [
        b"null",
        b"[]",
        b"{",
        b'{"data":{},"data":{}}',
        b'{"data":{"id":NaN}}',
        b'{"data":{"id":1e999}}',
        b"x" * (2 * 1024 * 1024 + 1),
    ],
)
async def test_bad_json_never_accepted(case, body):
    connection = await case.connect()

    async def inject(request):
        return httpx.Response(200, content=body, headers={"Content-Type": "application/json"})

    case.vendor.inject = inject
    assert (await case.invoke(connection, "get_current_user", {})).status == "failed"


async def test_body_draft_never_substituted_for_missing_body(case):
    connection = await case.connect()
    case.vendor.document.pop("body")
    case.vendor.document["body_draft"] = "private-draft"
    result = await case.invoke(
        connection, "get_document", {"repository_id": "10", "document_id": "100"}
    )
    assert result.status == "failed" and "private-draft" not in repr(result)


async def test_original_deadline_does_not_retry_write(case):
    from connector_sdk.client import ClientError

    connection = await case.connect()
    sent = []

    async def inject(request):
        if request.method == "POST":
            sent.append(request)
            await asyncio.Event().wait()

    case.vendor.inject = inject
    invocation = case.invocation(connection, "create_document")
    invocation["deadline"] = asyncio.get_running_loop().time() + 0.2
    with pytest.raises(ClientError) as captured:
        await asyncio.wait_for(case.sdk.invoke("create_document", NEW, **invocation), 2)
    assert captured.value.outcome == "result_unknown" and len(sent) == 1


@pytest.mark.parametrize(
    "change",
    [
        {"success": False},
        {"success": "true"},
        {"error": "private-business-error"},
        {"errors": ["private-business-error"]},
        {"errcode": 400},
        {"code": 400},
        {"code": True},
    ],
)
@pytest.mark.parametrize("nested", [True, False])
async def test_error_indicators_cannot_hide_beside_valid_write_object(case, change, nested):
    connection = await case.connect()

    async def inject(request):
        if request.method == "PUT":
            data = DOC | {"title": "修改"}
            if nested:
                return reply(data | change)
            return httpx.Response(200, json={"data": data} | change)

    case.vendor.inject = inject
    result = await case.invoke(connection, "update_document", CHANGE)
    assert result.status == "uncertain" and "private-business-error" not in repr(result)


async def test_offset_limit_does_not_generate_unusable_continuation(case):
    connection = await case.connect()

    async def inject(request):
        if request.url.path.endswith("/docs"):
            return reply([DOC], meta={"total": 1_000_002})

    case.vendor.inject = inject
    result = await case.invoke(
        connection, "list_documents", {"repository_id": "10", "offset": 1_000_000}
    )
    assert result.status == "succeeded" and result.data["has_more"] is True
    assert result.data["next_offset"] is None and result.data["offset_limit_reached"] is True


async def test_deleted_document_cannot_be_updated(case):
    connection = await case.connect()
    case.vendor.document["deleted_at"] = STAMP
    assert (await case.invoke(connection, "update_document", CHANGE)).status == "failed"
    assert not case.vendor.writes


@pytest.mark.parametrize("content_type", ["text/html", "text/event-stream", ""])
async def test_json_contract_does_not_accept_html_or_stream(case, content_type):
    connection = await case.connect()

    async def inject(request):
        return httpx.Response(200, content=b'{"data":{}}', headers={"Content-Type": content_type})

    case.vendor.inject = inject
    assert (await case.invoke(connection, "get_current_user", {})).status == "failed"


async def test_cancelled_write_does_not_retry(case):
    connection = await case.connect()
    sent = asyncio.Event()
    calls = []

    async def inject(request):
        if request.method == "POST":
            calls.append(request)
            sent.set()
            await asyncio.Event().wait()

    case.vendor.inject = inject
    task = asyncio.create_task(case.invoke(connection, "create_document", NEW))
    await asyncio.wait_for(sent.wait(), 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert len(calls) == 1
