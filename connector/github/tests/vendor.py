"""GitHub's public wire contracts mocked only at the HTTP transport boundary."""

import base64
import hashlib
import json
from urllib.parse import parse_qs

import httpx

ROOT = "/repos/octo/demo"


def response(data, status=200, headers=None):
    return httpx.Response(status, json=data, headers=headers)


class Vendor:
    def __init__(self):
        self.calls, self.tokens, self.writes = [], [], []
        self.challenge = ""
        self.generation, self.expires = 0, 3600
        self.token_change, self.profile_change = {}, {}
        self.inject = None
        self.issue = {
            "id": 100,
            "number": 7,
            "title": "Problem",
            "body": "Details",
            "state": "open",
            "state_reason": None,
            "labels": [{"name": "bug"}],
        }
        self.pull = {
            "id": 200,
            "number": 8,
            "title": "Fix",
            "changed_files": 2,
            "head": {"sha": "a" * 40},
            "base": {"sha": "b" * 40},
        }

    async def __call__(self, request):
        self.calls.append(request)
        assert request.url.scheme == "https"
        if self.inject:
            result = await self.inject(request)
            if result is not None:
                return result
        if request.url.host == "github.com":
            assert request.url.path == "/login/oauth/access_token" and request.method == "POST"
            assert request.headers["accept"] == "application/json"
            assert "authorization" not in request.headers
            assert request.headers["content-type"].startswith("application/x-www-form-urlencoded")
            form = {k: v[0] for k, v in parse_qs(request.content.decode()).items()}
            assert form["client_id"] == "Iv1.test" and form["client_secret"] == "test-secret"
            self.tokens.append(form)
            if "grant_type" not in form:
                assert form["code"] == "test-code"
                assert form["redirect_uri"] == "https://backend.test/api/connector-oauth/callback"
                digest = hashlib.sha256(form["code_verifier"].encode()).digest()
                assert base64.urlsafe_b64encode(digest).rstrip(b"=").decode() == self.challenge
            else:
                assert form["grant_type"] == "refresh_token"
                assert form["refresh_token"] == f"ghr_{self.generation}"
            self.generation += 1
            return response(
                {
                    "access_token": f"ghu_{self.generation}",
                    "refresh_token": f"ghr_{self.generation}",
                    "expires_in": self.expires,
                    "refresh_token_expires_in": 15897600,
                    "scope": "",
                    "token_type": "bearer",
                    **self.token_change,
                }
            )
        assert request.url.host == "api.github.com"
        assert request.headers["authorization"] == f"Bearer ghu_{self.generation}"
        assert request.headers["x-github-api-version"] == "2026-03-10"
        assert request.headers["user-agent"] == "actus-github/0.1.0"
        path, method = request.url.path, request.method
        if path == "/user":
            return response({"id": 42, "login": "octo", "type": "User", **self.profile_change})
        if path == "/user/installations":
            return response(
                {
                    "total_count": 1,
                    "installations": [
                        {"id": 1, "account": {"login": "octo"}, "permissions": {"issues": "write"}}
                    ],
                }
            )
        if path == "/user/installations/1/repositories":
            return response(
                {"total_count": 1, "repositories": [{"id": 10, "full_name": "octo/demo"}]}
            )
        if path in (ROOT, "/repositories/10"):
            return response({"id": 10, "full_name": "octo/demo"})
        if path == ROOT + "/labels":
            return response([{"id": 3, "name": "bug"}, {"id": 4, "name": "ready"}])
        if path == ROOT + "/issues":
            if method == "GET":
                return response([self.issue, self.issue | {"number": 8, "pull_request": {}}])
            assert method == "POST"
            body = json.loads(request.content)
            self.writes.append(body)
            return response(
                self.issue | body | {"labels": [{"name": name} for name in body.get("labels", [])]},
                201,
            )
        if path == ROOT + "/issues/7":
            if method == "GET":
                return response(self.issue)
            assert method == "PATCH"
            body = json.loads(request.content)
            self.writes.append(body)
            updated = self.issue | body
            if "labels" in body:
                updated["labels"] = [{"name": name} for name in body["labels"]]
            return response(updated)
        if path == ROOT + "/issues/8":
            return response(self.issue | {"number": 8, "pull_request": {}})
        if path == ROOT + "/issues/7/comments":
            if method == "GET":
                return response([{"id": 300, "body": "hello"}])
            assert method == "POST"
            body = json.loads(request.content)
            self.writes.append(body)
            return response({"id": 301, **body}, 201)
        if path == ROOT + "/pulls":
            return response([self.pull])
        if path == ROOT + "/pulls/8":
            return response(self.pull)
        if path == ROOT + "/pulls/8/files":
            return response(
                [
                    {"filename": "a.py", "patch": "@@ ...", "status": "modified"},
                    {"filename": "image.png", "status": "added"},
                ]
            )
        raise AssertionError(f"Unexpected wire request {method} {path}")
