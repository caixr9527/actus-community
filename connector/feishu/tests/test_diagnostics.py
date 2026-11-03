"""Safe diagnostics through the public SDK authorization entry points."""

import asyncio
import json

import httpx
import pytest
from vendor import SCOPES, TOKEN_URL, ok

PREFIX = "ACTUS_DIAGNOSTIC_V1 "


def events(capfd):
    return [json.loads(line.removeprefix(PREFIX)) for line in capfd.readouterr().err.splitlines()
            if line.startswith(PREFIX)]


async def test_success_records_phases_without_credentials_or_identity(case, capfd):
    view = await case.begin()
    assert (await case.complete(view)).data.status == "connected"
    records = events(capfd)
    assert any(r["phase"] == "oauth_exchange" and r["outcome"] == "succeeded" for r in records)
    assert any(r["phase"] == "identity" and r["outcome"] == "succeeded"
               and r["transaction_id"] == str(view.transaction_id) for r in records)
    assert any(r.get("http_status") == 200 and r.get("provider_code") == 0 for r in records)
    text = json.dumps(records)
    for value in ("test-secret", "test-code", "access-1", "refresh-1", "ou_person", "tenant1"):
        assert value not in text


@pytest.mark.parametrize("change,check", [
    ({"refresh_token": None}, "refresh_valid"),
    ({"refresh_token_expires_in": 0}, "refresh_expiry_valid"),
    ({"scope": "bitable:app"}, "required_scope_granted"),
    ({"token_type": "Basic"}, "token_type_valid"),
])
async def test_invalid_material_has_precise_flags_but_still_fails(case, capfd, change, check):
    case.vendor.token_change = change
    reply = await case.complete(await case.begin())
    assert reply.data.status == "failed"
    records = events(capfd)
    assert any(r["phase"] == "token_response" and r["outcome"] == "failed"
               and r.get("checks", {}).get(check) is False for r in records)
    assert len(case.vendor.tokens) == 1
    assert (await case.sdk.list_connections(**case.metadata("connection.list"))).data == ()


async def test_provider_error_and_malformed_body_are_not_echoed(case, capfd):
    async def inject(request):
        if str(request.url) == TOKEN_URL:
            return httpx.Response(400, json={"code": 20002, "msg": "sensitive-provider-message"})

    case.vendor.inject = inject
    reply = await case.complete(await case.begin())
    assert reply.data.error_code == "oauth_client_authentication_failed"
    records = events(capfd)
    assert any(r.get("provider_code") == 20002 and r.get("http_status") == 400 for r in records)
    assert "sensitive-provider-message" not in json.dumps(records)

    async def malformed(request):
        if str(request.url) == TOKEN_URL:
            return httpx.Response(200, content=b"sensitive-not-json")

    case.vendor.inject = malformed
    assert (await case.complete(await case.begin())).data.status == "failed"
    records = events(capfd)
    assert any(r.get("reason") == "invalid_response" for r in records)
    assert "sensitive-not-json" not in json.dumps(records)


async def test_identity_failure_reports_status_without_consuming_extra_body(case, capfd):
    class Unreadable(httpx.AsyncByteStream):
        async def __aiter__(self):
            raise AssertionError("diagnostics must not read a previously unread error body")
            yield b""  # pragma: no cover

    async def inject(request):
        if request.url.path.endswith("user_info"):
            return httpx.Response(403, stream=Unreadable())

    case.vendor.inject = inject
    assert (await case.complete(await case.begin())).data.status == "failed"
    records = events(capfd)
    assert any(r["phase"] == "identity" and r.get("http_status") == 403 for r in records)
    assert any(r["phase"] == "identity" and r["outcome"] == "failed" for r in records)


async def test_transport_failure_is_not_retried(case, capfd):
    calls = 0

    async def inject(request):
        nonlocal calls
        if str(request.url) == TOKEN_URL:
            calls += 1
            raise httpx.ReadTimeout("sensitive-network-message")

    case.vendor.inject = inject
    assert (await case.complete(await case.begin())).data.status == "failed"
    records = events(capfd)
    assert any(r["phase"] == "oauth_exchange" and r["outcome"] == "failed" for r in records)
    assert calls == 1
    assert "sensitive-network-message" not in json.dumps(records)


async def test_concurrent_exchanges_have_separate_attempts(case, capfd):
    ready, release = asyncio.Event(), asyncio.Event()
    requests = 0

    async def inject(request):
        nonlocal requests
        if str(request.url) == TOKEN_URL:
            requests += 1
            if requests == 2:
                ready.set()
            await release.wait()
            return httpx.Response(200, json={"code": 0, "access_token": "private-access",
                "refresh_token": "private-refresh", "token_type": "Bearer", "scope": SCOPES,
                "expires_in": 3600, "refresh_token_expires_in": 604800})
        if request.url.path.endswith("user_info"):
            return ok({"open_id": "private-account", "tenant_key": "private-tenant"})

    case.vendor.inject = inject
    a, b = await case.begin(), await case.begin(user="user-B")
    tasks = [asyncio.create_task(case.complete(a)),
             asyncio.create_task(case.complete(b, user="user-B"))]
    try:
        await asyncio.wait_for(ready.wait(), 2)
        release.set()
        assert all(r.data.status == "connected" for r in await asyncio.gather(*tasks))
    finally:
        release.set()
        await asyncio.gather(*tasks, return_exceptions=True)
    records = events(capfd)
    attempts = {r["attempt_id"] for r in records if r["phase"] == "oauth_exchange"}
    assert len(attempts) == 2
    assert {r["attempt_id"] for r in records if r["phase"] == "token_response"} == attempts
    assert {r["transaction_id"] for r in records if r["phase"] == "identity"} == {
        str(a.transaction_id), str(b.transaction_id)}


async def test_diagnostic_write_failure_does_not_change_authorization(case, monkeypatch):
    from feishu_connector import diagnostics

    def fail(_):
        raise OSError("injected diagnostic failure")

    monkeypatch.setattr(diagnostics, "_write", fail)
    assert (await case.complete(await case.begin())).data.status == "connected"


async def test_wrong_state_does_not_enter_exchange_or_emit_context(case, capfd):
    view = await case.begin()
    assert (await case.complete(view, state="wrong")).status == "failed"
    assert not events(capfd)
    assert not case.vendor.tokens


async def test_cancelled_exchange_preserves_cancellation_and_clears_context(monkeypatch, capfd):
    from feishu_connector.auth import Protocol
    from feishu_connector.diagnostics import emit

    entered = asyncio.Event()

    class Context:
        code_verifier = None
        redirect_uri = "https://backend.test/callback"

        async def request(self, *_args, **_kwargs):
            entered.set()
            await asyncio.Event().wait()

    # Replace only request construction, not the exchange flow or cancellation handling.
    monkeypatch.setattr(Protocol, "token_request", lambda self, ctx, form: form)
    task = asyncio.create_task(Protocol().exchange(Context(), {"code": "private-code"}))
    await asyncio.wait_for(entered.wait(), 1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    records = events(capfd)
    assert any(r["outcome"] == "cancelled" and r["reason"] == "cancelled" for r in records)
    emit("failed", reason="processing_failed")
    assert not events(capfd)


async def test_refresh_has_distinct_diagnostics_and_keeps_original_rules(case, capfd):
    case.vendor.expires = 1
    connection = await case.connect()
    events(capfd)
    await asyncio.sleep(1.05)
    assert (await case.invoke(connection, "list_wiki_spaces", {})).status == "succeeded"
    records = events(capfd)
    assert any(r["phase"] == "oauth_refresh" and r["outcome"] == "succeeded" for r in records)
    assert len(case.vendor.tokens) == 2


async def test_missing_provider_code_is_not_reported_as_zero(case, capfd):
    async def inject(request):
        if str(request.url) == TOKEN_URL:
            return httpx.Response(200, json={"access_token": "private-access",
                "refresh_token": "private-refresh", "token_type": "Bearer", "scope": SCOPES,
                "expires_in": 3600, "refresh_token_expires_in": 604800})
        if request.url.path.endswith("user_info"):
            return ok({"open_id": "private-account", "tenant_key": "private-tenant"})

    case.vendor.inject = inject
    assert (await case.complete(await case.begin())).data.status == "connected"
    records = events(capfd)
    token_records = [r for r in records if r["phase"] == "token_response"]
    assert token_records
    assert all("provider_code" not in r for r in token_records)
