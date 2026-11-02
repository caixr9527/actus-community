"""Official DingTalk wire shapes simulated only at the HTTP transport boundary."""

import json

import httpx

TOKEN = "/v1.0/oauth2/userAccessToken"
PROFILE = "/v1.0/contact/users/me"
CREATE = "/v1.0/todo/users/me/personalTasks"
TASK = "/v1.0/todo/users/me/tasks/task-1"


def response(data, status=200, headers=None):
    return httpx.Response(status, json=data, headers=headers)


class Vendor:
    def __init__(self):
        self.calls, self.tokens, self.writes = [], [], []
        self.generation, self.expires = 0, 3600
        self.token_change, self.profile_change = {}, {}
        self.inject = None
        self.access_tokens, self.refresh_tokens = set(), set()

    async def __call__(self, request):
        self.calls.append(request)
        assert request.url.scheme == "https" and request.url.host == "api.dingtalk.com"
        assert "authorization" not in request.headers
        if self.inject:
            result = await self.inject(request)
            if result is not None:
                return result
        path, method = request.url.path, request.method
        if path == TOKEN:
            assert method == "POST"
            assert "x-acs-dingtalk-access-token" not in request.headers
            assert request.headers["content-type"].startswith("application/json")
            assert not request.url.query
            body = json.loads(request.content)
            assert body["clientId"] == "ding.test" and body["clientSecret"] == "test-secret"
            self.tokens.append(body)
            if body["grantType"] == "authorization_code":
                assert body == {
                    "clientId": "ding.test",
                    "clientSecret": "test-secret",
                    "grantType": "authorization_code",
                    "code": "test-code",
                }
            else:
                assert body["grantType"] == "refresh_token"
                assert body["refreshToken"] in self.refresh_tokens
                assert set(body) == {"clientId", "clientSecret", "grantType", "refreshToken"}
            self.generation += 1
            data = {
                "accessToken": f"dt-access-{self.generation}",
                "refreshToken": f"dt-refresh-{self.generation}",
                "expireIn": self.expires,
                **self.token_change,
            }
            self.access_tokens.add(data.get("accessToken"))
            self.refresh_tokens.add(data.get("refreshToken"))
            return response(data)
        assert request.headers["x-acs-dingtalk-access-token"] in self.access_tokens
        if path == PROFILE:
            assert method == "GET" and not request.url.query
            return response(
                {
                    "unionId": "union-42",
                    "openId": "open-42",
                    "nick": "测试用户",
                    "mobile": "private-mobile",
                    "email": "private-email",
                    **self.profile_change,
                }
            )
        if path == CREATE:
            assert method == "POST" and not request.url.query
            assert request.headers["content-type"].startswith("application/json")
            body = json.loads(request.content)
            assert body["executorIds"] == ["union-42"]
            assert set(body) <= {"subject", "description", "dueTime", "executorIds"}
            assert type(body["subject"]) is str
            self.writes.append(body)
            return response({"taskId": "task-1", "createdTime": 1793606400000})
        if path == TASK + "/update":
            assert method == "PUT" and not request.url.query
            body = json.loads(request.content)
            assert body and set(body) <= {"subject", "description", "dueTime"}
            self.writes.append(body)
            return response({"success": True})
        if path == TASK + "/updateExecutorStatus":
            assert method == "PUT" and not request.content
            assert dict(request.url.params) in ({"done": "true"}, {"done": "false"})
            self.writes.append(dict(request.url.params))
            return response({"success": True})
        if path == TASK + "/remove":
            assert method == "DELETE" and not request.content and not request.url.query
            self.writes.append({"delete": True})
            return response({"success": "true"})
        raise AssertionError(f"Unexpected wire request {method} {path}")
