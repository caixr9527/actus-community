"""Public SDK server/client with an isolated encrypted store and mock vendor transport."""

import asyncio
import os
import time
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import httpx
import jwt
import pytest_asyncio
from connector_sdk import HttpOptions, JwtPlatformAdapter, assemble_config, load_project
from connector_sdk.client import ConnectorClient
from connector_sdk.runtime import RuntimeOptions
from connector_sdk.server import ServerOptions, create_app
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from vendor import Vendor

OPTIONS = HttpOptions(8, 4, 2, 2, 2, 2, 2 * 1024 * 1024, 2 * 1024 * 1024)


@pytest_asyncio.fixture
async def case(tmp_path, monkeypatch):
    vendor = Vendor()
    # Network boundary substitution, never SDK private hooks or an application test switch.
    monkeypatch.setattr(httpx, "AsyncHTTPTransport", lambda **_: httpx.MockTransport(vendor))
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    platform = JwtPlatformAdapter(issuer="yuque-test", audience="sdk", public_key=public)
    declaration = load_project(Path(__file__).parents[1] / "pyproject.toml")
    secret = tmp_path / "credential-key"
    secret.write_bytes(os.urandom(32))
    secret.chmod(0o600)
    configured = assemble_config(
        declaration,
        values={},
        secrets={},
        runtime={
            "installation_id": uuid4(),
            "data_dir": tmp_path / "data",
            "credential_key_file": secret,
        },
    )
    result = SimpleNamespace(
        vendor=vendor, declaration=declaration, configured=configured, root=tmp_path
    )
    lifetimes = []

    async def reopen():
        app = create_app(
            declaration,
            configured,
            platform=platform,
            expected_manifest=declaration.manifest,
            runtime_options=RuntimeOptions(8, 8, 5),
            http_options=OPTIONS,
            server_options=ServerOptions(max_request_bytes=2 * 1024 * 1024),
        )
        lifetime = app.router.lifespan_context(app)
        await lifetime.__aenter__()
        sdk = ConnectorClient(
            base_url="https://sdk.test",
            installation_id=configured.runtime.installation_id,
            http_options=OPTIONS,
            transport=httpx.ASGITransport(app=app),
        )
        await sdk.__aenter__()
        lifetimes.append((sdk, lifetime))
        result.sdk = sdk

    async def stop():
        sdk, lifetime = lifetimes.pop()
        try:
            await sdk.__aexit__(None, None, None)
        finally:
            await lifetime.__aexit__(None, None, None)

    def metadata(action, *, user="user-A", **scope):
        now = int(time.time())
        claims = {
            "iss": "yuque-test",
            "aud": "sdk",
            "sub": user,
            "subject_kind": "user",
            "iat": now,
            "exp": now + 60,
            "action": action,
            "installation_id": str(configured.runtime.installation_id),
            **scope,
        }
        return {
            "request_id": "yuque-test",
            "token": jwt.encode(claims, key, algorithm="RS256"),
            "deadline": asyncio.get_running_loop().time() + 5,
        }

    async def begin(**kwargs):
        reply = await result.sdk.begin_authorization(**metadata("authorization.create", **kwargs))
        assert reply.status == "succeeded", reply
        view = reply.data
        return view

    async def complete(view, *, user="user-A", token="test-yuque-token"):
        return await result.sdk.complete_authorization(
            view.transaction_id,
            {"api_key": token},
            **metadata(
                "authorization.complete", user=user, transaction_id=str(view.transaction_id)
            ),
        )

    async def connect():
        reply = await complete(await begin())
        assert reply.status == "succeeded" and reply.data.status == "connected", reply
        return reply.data.connection

    def invocation(connection, operation, **kwargs):
        manifest = declaration.manifest
        return dict(
            connection_id=connection.connection_id,
            app_version=manifest.version,
            catalog_revision=manifest.catalog_revision,
            **metadata(
                "operation.invoke",
                operation_name=operation,
                app_id=manifest.id,
                app_version=manifest.version,
                catalog_revision=manifest.catalog_revision,
                connection_id=str(connection.connection_id),
                **kwargs,
            ),
        )

    async def invoke(connection, name, params, **kwargs):
        return await result.sdk.invoke(name, params, **invocation(connection, name, **kwargs))

    result.reopen, result.stop, result.metadata = reopen, stop, metadata
    result.begin, result.complete, result.connect = begin, complete, connect
    result.invoke, result.invocation = invoke, invocation
    await reopen()
    try:
        yield result
    finally:
        while lifetimes:
            await stop()
