"""Deterministic Feishu wire contracts, substituted only at the HTTPX transport boundary."""

import base64
import hashlib
import json
from urllib.parse import parse_qs

import httpx

SCOPES = "offline_access docx:document:readonly wiki:wiki:readonly bitable:app"
BASE = "/open-apis/bitable/v1/apps/base1/tables/table1"
FIELDS = [
    {"field_name": "标题", "field_id": "fld1", "type": 1},
    {"field_name": "数量", "field_id": "fld2", "type": 2},
    {"field_name": "状态", "field_id": "fld3", "type": 3,
     "property": {"options": [{"name": "进行中"}, {"name": "已完成"}]}},
    {"field_name": "标签", "field_id": "fld4", "type": 4,
     "property": {"options": [{"name": "A"}, {"name": "B"}]}},
    {"field_name": "日期", "field_id": "fld5", "type": 5},
    {"field_name": "完成", "field_id": "fld6", "type": 7},
    {"field_name": "链接", "field_id": "fld7", "type": 15},
    {"field_name": "公式", "field_id": "fld8", "type": 20},
]


def ok(data):
    return httpx.Response(200, json={"code": 0, "msg": "success", "data": data})


def page(items, *, more=False, token=None):
    result = {"items": items, "has_more": more}
    if token is not None:
        result["page_token"] = token
    return ok(result)


class Vendor:
    def __init__(self):
        self.calls, self.tokens, self.writes = [], [], []
        self.challenge = ""
        self.generation, self.expires = 0, 3600
        self.token_change, self.profile_change = {}, {}
        self.scope = SCOPES
        self.inject = None
        self.fields = FIELDS
        self.record = {"record_id": "rec1", "fields": {"标题": [{"type": "text", "text": "测试"}]}}

    async def __call__(self, request):
        self.calls.append(request)
        assert request.url.scheme == "https"
        if self.inject:
            response = await self.inject(request)
            if response is not None:
                return response
        if request.url.host == "accounts.feishu.cn":
            assert request.url.path == "/oauth/v3/token" and request.method == "POST"
            assert request.headers["content-type"].startswith("application/x-www-form-urlencoded")
            assert "authorization" not in request.headers
            form = {k: v[0] for k, v in parse_qs(request.content.decode()).items()}
            assert form["client_id"] == "cli_test" and form["client_secret"] == "test-secret"
            self.tokens.append(form)
            if form["grant_type"] == "authorization_code":
                assert form["redirect_uri"] == (
                    "https://backend.test/api/connector-oauth/callback")
                digest = hashlib.sha256(form["code_verifier"].encode()).digest()
                assert base64.urlsafe_b64encode(digest).rstrip(b"=").decode() == self.challenge
            else:
                assert form["grant_type"] == "refresh_token"
                assert form["refresh_token"] == f"refresh-{self.generation}"
                assert "code_verifier" not in form and "redirect_uri" not in form
            self.generation += 1
            return httpx.Response(200, json={
                "code": 0, "access_token": f"access-{self.generation}",
                "refresh_token": f"refresh-{self.generation}", "token_type": "Bearer",
                "expires_in": self.expires, "refresh_token_expires_in": 604800,
                "scope": self.scope, **self.token_change})
        assert request.url.host == "open.feishu.cn"
        assert request.headers["authorization"] == f"Bearer access-{self.generation}"
        assert "access_token" not in request.url.params
        path = request.url.path
        if path == "/open-apis/authen/v1/user_info":
            return ok({"open_id": "ou_person", "tenant_key": "tenant1", "name": "测试用户",
                       **self.profile_change})
        if path == "/open-apis/docx/v1/documents/doc1":
            return ok({"document": {"document_id": "doc1", "revision_id": 8, "title": "说明"}})
        if path == "/open-apis/docx/v1/documents/doc1/raw_content":
            return ok({"content": "项目说明\n正文"})
        if path == "/open-apis/wiki/v2/spaces":
            return page([{"space_id": "123", "name": "项目"}])
        if path == "/open-apis/wiki/v2/spaces/123/nodes":
            return page([{"node_token": "wiki1", "obj_type": "docx", "obj_token": "doc1"}])
        if path == "/open-apis/wiki/v2/spaces/get_node":
            assert dict(request.url.params) == {"token": "wiki1", "obj_type": "wiki"}
            return ok({"node": {"node_token": "wiki1", "obj_type": "bitable",
                                "obj_token": "base1"}})
        if path == "/open-apis/bitable/v1/apps/base1/tables":
            return page([{"table_id": "table1", "name": "项目表"}])
        if path == BASE + "/fields":
            return page(self.fields)
        if path == BASE + "/views":
            return page([{"view_id": "view1", "view_name": "表格视图"}])
        if path == BASE + "/records/search":
            assert request.method == "POST"
            return page([self.record])
        if path == BASE + "/records/rec1" and request.method == "GET":
            return ok({"record": self.record})
        if path in (BASE + "/records", BASE + "/records/rec1"):
            assert request.method == ("POST" if path.endswith("records") else "PUT")
            body = json.loads(request.content)
            assert set(body) == {"fields"}
            self.writes.append(body)
            return ok({"record": {"record_id": "rec1", "fields": body["fields"]}})
        raise AssertionError(f"unexpected request: {request.method} {path}")
