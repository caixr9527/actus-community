import json

import httpx
import pytest
from vendor import BASE, FIELDS, ok, page

TABLE = {"app_token": "base1", "table_id": "table1"}
CASES = [
    ("get_document", {"document_id": "doc1"}, "GET", "/docx/v1/documents/doc1"),
    ("read_document", {"document_id": "doc1"}, "GET", "/docx/v1/documents/doc1/raw_content"),
    ("list_wiki_spaces", {}, "GET", "/wiki/v2/spaces"),
    ("list_wiki_nodes", {"space_id": "123"}, "GET", "/wiki/v2/spaces/123/nodes"),
    ("get_wiki_node", {"token": "wiki1"}, "GET", "/wiki/v2/spaces/get_node"),
    ("list_tables", {"app_token": "base1"}, "GET", "/bitable/v1/apps/base1/tables"),
    ("list_fields", TABLE, "GET", BASE.removeprefix("/open-apis") + "/fields"),
    ("list_views", TABLE, "GET", BASE.removeprefix("/open-apis") + "/views"),
    ("search_records", TABLE, "POST", BASE.removeprefix("/open-apis") + "/records/search"),
    ("get_record", TABLE | {"record_id": "rec1"}, "GET",
     BASE.removeprefix("/open-apis") + "/records/rec1"),
    ("create_record", TABLE | {"fields": {"标题": "新增"}}, "POST",
     BASE.removeprefix("/open-apis") + "/records"),
    ("update_record", TABLE | {"record_id": "rec1", "fields": {"标题": "更新"}}, "PUT",
     BASE.removeprefix("/open-apis") + "/records/rec1"),
]


@pytest.mark.parametrize("name,params,method,path", CASES)
async def test_twelve_operations_follow_frozen_wire_contract(case, name, params, method, path):
    connection = await case.connect()
    reply = await case.invoke(connection, name, params)
    assert reply.status == "succeeded", reply
    assert case.vendor.calls[-1].method == method
    assert case.vendor.calls[-1].url.path == "/open-apis" + path
    if name == "get_wiki_node":
        assert reply.data["data"]["node"]["obj_token"] == "base1"


async def test_search_serializes_conditions_sort_and_opaque_cursor_exactly(case):
    connection = await case.connect()
    values = {"filter": {"conjunction": "and", "conditions": [
        {"field_name": "状态", "operator": "is", "value": ["进行中"]}]},
        "sort": [{"field_name": "日期", "desc": True}], "field_names": ["标题"],
        "page_size": 30, "page_token": "opaque+/=中文"}
    reply = await case.invoke(connection, "search_records", TABLE | values)
    assert reply.status == "succeeded", reply
    request = case.vendor.calls[-1]
    assert dict(request.url.params) == {"page_size": "30", "page_token": "opaque+/=中文"}
    assert json.loads(request.content) == {k: v for k, v in values.items()
                                           if k not in ("page_size", "page_token")}


@pytest.mark.parametrize("name,params", [
    ("read_document", {"document_id": "../doc1"}),
    ("read_document", {"document_id": "https://evil.test"}),
    ("list_wiki_nodes", {"space_id": "123", "page_size": True}),
    ("list_wiki_spaces", {"page_size": 51}),
    ("search_records", TABLE | {"sql": "select *"}),
    ("search_records", TABLE | {"view_id": "view1", "sort": [{"field_name": "标题"}]}),
    ("create_record", TABLE | {"fields": {}}),
    ("create_record", TABLE | {"fields": {"标题": "a"}, "url": "https://evil.test"}),
])
async def test_invalid_input_rejected_before_any_vendor_call(case, name, params):
    connection = await case.connect()
    before = len(case.vendor.calls)
    assert (await case.invoke(connection, name, params)).status == "failed"
    assert len(case.vendor.calls) == before


@pytest.mark.parametrize("fields", [
    {"标题": "值", "数量": 3.5, "状态": "进行中", "标签": ["A", "B"],
     "日期": 1730000000000, "完成": True, "链接": {"text": "示例", "link": "https://example.com"}},
    {"标题": None, "数量": None, "标签": [], "完成": False},
])
async def test_supported_fields_and_explicit_clearing_preserve_values(case, fields):
    connection = await case.connect()
    reply = await case.invoke(connection, "update_record",
                              TABLE | {"record_id": "rec1", "fields": fields})
    assert reply.status == "succeeded", reply
    assert case.vendor.writes == [{"fields": fields}]


@pytest.mark.parametrize("fields", [
    {"不存在": "x"}, {"公式": None}, {"公式": "x"}, {"数量": True}, {"数量": "1"},
    {"日期": 1.5}, {"完成": 1}, {"标题": ["x"]}, {"状态": "新选项"}, {"数量": 10**400},
    {"标签": ["A", "A"]}, {"标签": ["新选项"]}, {"标签": {"A": 1}},
    {"链接": {"link": "javascript:alert(1)"}}, {"链接": {"link": "https://a", "extra": "x"}},
])
async def test_bad_fields_never_write_or_create_options(case, fields):
    connection = await case.connect()
    reply = await case.invoke(connection, "create_record", TABLE | {"fields": fields})
    assert reply.status == "failed"
    assert reply.error.code == "operation_failed", reply
    assert not case.vendor.writes
    assert case.vendor.calls[-1].url.path.endswith("/fields")


async def test_field_schema_fetched_each_time_and_all_pages_before_write(case):
    connection = await case.connect()
    requests = []

    async def inject(request):
        if request.url.path == BASE + "/fields":
            requests.append(dict(request.url.params))
            if "page_token" not in request.url.params:
                return page(FIELDS[:2], more=True, token="next+/=")
            assert request.url.params["page_token"] == "next+/="
            return page(FIELDS[2:])

    case.vendor.inject = inject
    for _ in range(2):
        reply = await case.invoke(connection, "create_record", TABLE | {"fields": {"完成": True}})
        assert reply.status == "succeeded", reply
    assert len(requests) == 4
    case.vendor.inject = None
    case.vendor.fields = []
    assert (await case.invoke(connection, "create_record",
                              TABLE | {"fields": {"完成": True}})).status == "failed"
    assert len(case.vendor.writes) == 2


@pytest.mark.parametrize("payload", [
    {"items": [], "has_more": True},
    {"items": [], "has_more": "false"},
    {"has_more": False},
    {"items": [None], "has_more": False},
])
async def test_malformed_paging_fails_instead_of_empty_success(case, payload):
    connection = await case.connect()

    async def inject(request):
        if request.url.path == "/open-apis/wiki/v2/spaces":
            return ok(payload)

    case.vendor.inject = inject
    assert (await case.invoke(connection, "list_wiki_spaces", {})).status == "failed"


async def test_empty_permission_filtered_page_can_still_have_more(case):
    connection = await case.connect()

    async def inject(request):
        if request.url.path == "/open-apis/wiki/v2/spaces":
            return page([], more=True, token="next")

    case.vendor.inject = inject
    reply = await case.invoke(connection, "list_wiki_spaces", {})
    assert reply.status == "succeeded"
    assert reply.data["data"] == {"items": [], "has_more": True, "page_token": "next"}


@pytest.mark.parametrize("mode", ["timeout", "business", "malformed", "mismatch", "http"])
async def test_write_uncertainty_does_not_retry(case, mode):
    connection = await case.connect()
    sent = []

    async def inject(request):
        if request.url.path == BASE + "/records/rec1" and request.method == "PUT":
            sent.append(request)
            if mode == "timeout":
                raise httpx.ReadTimeout("secret-vendor-body")
            if mode == "business":
                return httpx.Response(200, json={"code": 1255001, "msg": "secret-vendor-body"})
            if mode == "malformed":
                return httpx.Response(200, content=b'{"code":0,"data":null}')
            if mode == "mismatch":
                return ok({"record": {"record_id": "other", "fields": {}}})
            return httpx.Response(503)

    case.vendor.inject = inject
    reply = await case.invoke(connection, "update_record",
                              TABLE | {"record_id": "rec1", "fields": {"标题": "更新"}})
    assert reply.status == "uncertain" and len(sent) == 1, reply
    assert "secret-vendor-body" not in repr(reply)


async def test_cancelled_write_never_retries(case):
    import asyncio

    connection = await case.connect()
    started = asyncio.Event()
    sent = []

    async def inject(request):
        if request.url.path == BASE + "/records":
            sent.append(request)
            started.set()
            await asyncio.Event().wait()

    case.vendor.inject = inject
    task = asyncio.create_task(case.invoke(connection, "create_record",
                                          TABLE | {"fields": {"标题": "新增"}}))
    await asyncio.wait_for(started.wait(), 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert len(sent) == 1


@pytest.mark.parametrize("mode", ["http", "cycle", "duplicate", "unknown", "missing_options"])
async def test_failed_schema_preflight_is_a_definite_no_write(case, mode):
    connection = await case.connect()

    async def inject(request):
        if request.url.path == BASE + "/fields":
            if mode == "http":
                return httpx.Response(503)
            if mode == "cycle":
                return page([], more=True, token="same")
            if mode == "duplicate":
                return page([FIELDS[0], FIELDS[0]])
            if mode == "unknown":
                return page([{"field_name": "标题", "type": "1"}])
            return page([{"field_name": "状态", "type": 3}])

    case.vendor.inject = inject
    reply = await case.invoke(connection, "create_record", TABLE | {"fields": {"状态": "进行中"}})
    assert reply.status == "failed" and reply.error.code == "operation_failed", reply
    assert not case.vendor.writes
    assert all(r.method == "GET" for r in case.vendor.calls if r.url.host == "open.feishu.cn")


@pytest.mark.parametrize("status,payload", [
    (200, b'[]'), (200, b'{"code":0,"code":0,"data":{}}'),
    (200, b'{"code":true,"data":{}}'), (200, b'{"code":0,"data":{"v":NaN}}'),
    (200, b'{"code":0,"data":{}}'), (200, b'{"code":0,"data":{"content":null}}'),
    (200, b'{"code":1254302,"msg":"private"}'),
    (200, b'{"code":1254040,"msg":"private"}'),
    (200, b'{"code":1254290,"msg":"private"}'), (403, b'private'), (429, b'private'),
    (200, b'X' * (1024 * 1024 + 1)),
])
async def test_read_errors_never_become_empty_success(case, status, payload):
    connection = await case.connect()

    async def inject(request):
        if request.url.path.endswith("/raw_content"):
            return httpx.Response(status, content=payload)

    case.vendor.inject = inject
    reply = await case.invoke(connection, "read_document", {"document_id": "doc1"})
    assert reply.status == "failed" and "private" not in repr(reply)


async def test_unsupported_wiki_resource_is_preserved_without_guessing(case):
    connection = await case.connect()

    async def inject(request):
        if request.url.path.endswith("/get_node"):
            return ok({"node": {"node_token": "wiki1", "obj_type": "sheet", "obj_token": "sheet1"}})

    case.vendor.inject = inject
    reply = await case.invoke(connection, "get_wiki_node", {"token": "wiki1"})
    assert reply.status == "succeeded"
    assert reply.data["data"]["node"]["obj_type"] == "sheet"
