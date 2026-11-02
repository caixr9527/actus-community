"""OpenAPI-derived compatibility fixtures, not captured live Yuque responses."""

import copy
import json

import httpx

STAMP = "2026-11-02T01:00:00.000Z"
LATER = "2026-11-02T02:00:00.000Z"
USER = {"id": 42, "login": "example", "name": "测试用户", "email": "private-email"}
GROUP = {"id": 7, "login": "team", "name": "团队", "members": ["private-member"]}
REPO = {
    "id": 10,
    "type": "Book",
    "name": "手册",
    "slug": "manual",
    "namespace": "example/manual",
    "public": 0,
    "updated_at": STAMP,
    "user": USER,
}
DOC = {
    "id": 100,
    "book_id": 10,
    "type": "Doc",
    "title": "原文档",
    "slug": "original",
    "format": "markdown",
    "body": "# 原文\n正文",
    "body_draft": "",
    "public": 0,
    "updated_at": STAMP,
    "status": "1",
    "body_html": "private-derived-body",
    "creator": USER,
    "unknown": "private-vendor-field",
}


def reply(data, *, meta=None, status=200):
    return httpx.Response(
        status, json={"data": data} | ({"meta": meta} if meta is not None else {})
    )


class Vendor:
    def __init__(self):
        self.calls, self.writes = [], []
        self.tokens = {"test-yuque-token", "second-yuque-token"}
        self.document, self.repository = copy.deepcopy(DOC), copy.deepcopy(REPO)
        self.inject = None

    async def __call__(self, request):
        self.calls.append(request)
        assert request.url.scheme == "https" and request.url.host == "www.yuque.com"
        assert request.url.path.startswith("/api/v2/")
        assert request.headers["user-agent"] == "Actus-Yuque/0.1.0"
        assert request.headers["accept"] == "application/json"
        assert "authorization" not in request.headers and "token" not in request.url.params
        token = request.headers["x-auth-token"]
        if token not in self.tokens:
            return httpx.Response(401, json={"message": "private-error"})
        if self.inject:
            result = await self.inject(request)
            if result is not None:
                return result
        path, method = request.url.path.removeprefix("/api/v2/"), request.method
        if method == "GET":
            if path == "user":
                return reply(
                    USER | ({"id": 43, "login": "second"} if token == "second-yuque-token" else {})
                )
            if path in {"users/42/groups", "users/43/groups"}:
                assert set(request.url.params) == {"offset"}
                return reply([GROUP])
            if path in {"users/42/repos", "users/43/repos", "groups/7/repos"}:
                assert set(request.url.params) == {"offset", "limit"}
                return reply([self.repository])
            if path == "repos/10":
                return reply(self.repository)
            if path == "repos/10/docs":
                assert request.url.params["deleted"] == "false"
                return reply([self.document], meta={"total": 1})
            if path == "repos/10/docs/100":
                return reply(self.document)
            if path == "search":
                kind = request.url.params["type"]
                data = self.document if kind == "doc" else self.repository
                return reply(
                    [
                        {
                            "id": data["id"],
                            "type": kind,
                            "title": "<em>测试</em>标题",
                            "summary": "<em>摘要</em>",
                            "target": data,
                            "url": "/example/manual/original",
                        }
                    ],
                    meta={"total": 1, "pageNo": int(request.url.params["page"]), "pageSize": 20},
                )
        if method in {"POST", "PUT"}:
            assert request.headers["content-type"].startswith("application/json")
            body = json.loads(request.content)
            assert body["format"] == "markdown" and type(body["public"]) is int
            assert set(body) <= {"title", "body", "format", "public"}
            self.writes.append(request)
            if method == "POST" and path == "repos/10/docs":
                assert body["public"] == 0
                return reply(
                    self.document | body | {"id": 101, "slug": "created", "updated_at": LATER}
                )
            if method == "PUT" and path == "repos/10/docs/100":
                self.document |= body | {"updated_at": LATER}
                return reply(self.document)
        raise AssertionError("unexpected vendor request")
