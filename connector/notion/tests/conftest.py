"""Candidate SDK runtime with an isolated encrypted store and a deterministic vendor."""

import json
import os
import time
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit
from uuid import uuid4

import httpx
import jwt
import pytest_asyncio
from connector_sdk import HttpOptions, JwtPlatformAdapter, assemble_config, load_project
from connector_sdk.runtime import Runtime, RuntimeOptions
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from notion_connector.protocol import ORIGIN, PROTOCOL, TOOLS


def object_schema(properties=None, required=()):
    return {"type": "object", "properties": properties or {}, "required": list(required)}


class Vendor:
    def __init__(self):
        self.calls, self.forms, self.closed = [], [], 0
        self.tools = {remote: object_schema() for remote in TOOLS.values()}
        self.tools["notion-get-self"] = object_schema()
        self.identity = {"workspace": {"id": "Workspace RAW", "name": ""},
                         "user": {"id": "Person RAW", "type": "person", "name": ""}}
        self.result = {"content": [{"type": "text", "text": "# Content\n中文"}]}
        self.access = None
        self.refresh_fail = False
        self.expires = 3600
        self.generation = 0
        self.revocations = []
        self.inject = None
        self.cleanup_fail = False

    async def __call__(self, request):
        assert request.url.host == "mcp.notion.com" and request.url.scheme == "https"
        if request.url.path == "/token":
            form = {k: v[0] for k, v in parse_qs(request.content.decode()).items()}
            self.forms.append(form)
            assert form["client_id"] == "registered-client" and "client_secret" not in form
            if "token" in form:
                assert form["token"] == f"refresh-{self.generation}"
                self.revocations.append(form)
                return httpx.Response(200, json={})
            if form["grant_type"] == "refresh_token":
                assert form["refresh_token"] == f"refresh-{self.generation}"
                if self.refresh_fail:
                    return httpx.Response(400, json={"error": "invalid_grant"})
            else:
                assert form["redirect_uri"] == "https://backend.test/api/connector-oauth/callback"
                assert len(form["code_verifier"]) == 43
            self.generation += 1
            return httpx.Response(200, json={"access_token": f"access-{self.generation}",
                                            "refresh_token": f"refresh-{self.generation}",
                                            "token_type": "Bearer", "expires_in": self.expires})
        assert request.url.path == "/mcp"
        assert request.headers["authorization"] == f"Bearer access-{self.generation}"
        if request.method == "DELETE":
            self.closed += 1
            return httpx.Response(500 if self.cleanup_fail else 204)
        body = json.loads(request.content)
        self.calls.append(body)
        if self.inject:
            result = await self.inject(body, request)
            if result is not None:
                return result
        method = body["method"]
        if method == "notifications/initialized":
            return httpx.Response(202)
        if method == "initialize":
            result = {"protocolVersion": PROTOCOL, "capabilities": {"tools": {}},
                      "serverInfo": {"name": "isolated", "version": "1"}}
        elif method == "tools/list":
            result = {"tools": [{"name": k, "inputSchema": v} for k, v in self.tools.items()]}
        else:
            assert body["params"]["name"] in {*TOOLS.values(), "notion-get-self",
                                                "notion-get-tool-access"}
            tool = body["params"]["name"]
            if tool == "notion-get-self":
                result = {"structuredContent": self.identity}
            elif tool == "notion-get-tool-access":
                result = {"structuredContent": {"current_tool_access": self.access}}
            else:
                result = self.result
        return httpx.Response(200, json={"jsonrpc": "2.0", "id": body["id"], "result": result},
                              headers={"mcp-session-id": "isolated-session"})


@pytest_asyncio.fixture
async def case(tmp_path, monkeypatch):
    from connector_sdk import http

    vendor = Vendor()
    monkeypatch.setattr(http, "_make_transport", lambda _: httpx.MockTransport(vendor))
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = key.public_key().public_bytes(serialization.Encoding.PEM,
                                          serialization.PublicFormat.SubjectPublicKeyInfo)
    adapter = JwtPlatformAdapter(issuer="notion-test", audience="sdk", public_key=public)
    declaration = load_project(__import__("pathlib").Path(__file__).parents[1] / "pyproject.toml")
    secret = tmp_path / "credential-key"
    secret.write_bytes(os.urandom(32))
    secret.chmod(0o600)
    configured = assemble_config(declaration, values={"client_id": "registered-client"}, secrets={},
                                 runtime={"installation_id": uuid4(), "data_dir": tmp_path / "data",
                                          "credential_key_file": secret,
                                          "oauth_redirect_uri":
                                          "https://backend.test/api/connector-oauth/callback"})
    runtimes = []
    result = SimpleNamespace(vendor=vendor, declaration=declaration, configured=configured)

    async def reopen():
        runtime = Runtime(declaration, configured, platform=adapter,
                          expected_manifest=declaration.manifest,
                          options=RuntimeOptions(8, 8, 3),
                          http_options=HttpOptions(16, 8, 2, 2, 2, 2, 1024 * 1024, 1024 * 1024))
        runtimes.append(runtime)
        await runtime.start()
        result.runtime = runtime
        return runtime

    def metadata(action, **scope):
        now = int(time.time())
        claims = {"iss": "notion-test", "aud": "sdk", "sub": "user-A", "subject_kind": "user",
                  "iat": now, "exp": now + 60, "action": action,
                  "installation_id": str(configured.runtime.installation_id), **scope}
        return {"installation_id": configured.runtime.installation_id, "request_id": "isolated",
                "token": jwt.encode(claims, key, algorithm="RS256")}

    async def begin():
        return await result.runtime.begin_authorization(**metadata("authorization.create"))

    async def complete(view, **change):
        state = parse_qs(urlsplit(view.authorization_url).query)["state"][0]
        return await result.runtime.complete_authorization(
            view.transaction_id, {"state": state, "code": "private-code", "iss": ORIGIN, **change},
            **metadata("authorization.complete", transaction_id=str(view.transaction_id)))

    async def invoke(connection, name, params):
        return await result.runtime.invoke(
            name, params, connection_id=connection.connection_id, app_version="0.1.1",
            catalog_revision=declaration.manifest.catalog_revision,
            **metadata("operation.invoke", operation_name=name, app_id="notion",
                       app_version="0.1.1", catalog_revision=declaration.manifest.catalog_revision,
                       connection_id=str(connection.connection_id)))

    result.reopen, result.metadata = reopen, metadata
    result.begin, result.complete, result.invoke = begin, complete, invoke
    await reopen()
    try:
        yield result
    finally:
        for runtime in runtimes:
            await runtime.close()
