"""Notion validates the generic SDK lifecycle, with no real provider writes."""

import asyncio

import httpx
import pytest
from connector_sdk import AuthorizationError


async def test_empty_settings_and_first_begin_registers_once_across_restart(case):
    assert case.declaration.manifest.config_schema.get("properties", {}) == {}
    assert not case.vendor.registrations
    first, second = await asyncio.gather(case.begin(), case.begin())
    assert first.transaction_id != second.transaction_id
    assert case.vendor.registrations == [{
        "client_name": "actus-notion",
        "redirect_uris": ["https://backend.test/api/connector-oauth/callback"],
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"], "token_endpoint_auth_method": "none",
        "scope": "default",
    }]
    connected = await case.complete(first)
    assert connected.status == "connected"
    await case.runtime.close()
    await case.reopen()
    await case.begin()
    assert len(case.vendor.registrations) == 1
    called = await case.invoke(connected.connection, "search", {"query": "test"})
    assert called.status == "succeeded"


async def test_unknown_registration_never_repeats_after_restart(case):
    async def lost(request):
        raise httpx.ReadError("private registration result", request=request)
    case.vendor.register = lost
    for restart in (False, True):
        if restart:
            await case.runtime.close()
            await case.reopen()
        with pytest.raises(AuthorizationError) as failure:
            await case.begin()
        assert failure.value.code == "oauth_registration_unknown"
        assert "private" not in str(failure.value)
    assert len(case.vendor.registrations) == 1
    assert not case.vendor.forms and not case.vendor.calls


async def test_cancel_registration_waits_cleanup_and_retains_unknown(case):
    entered, cleaning, release = asyncio.Event(), asyncio.Event(), asyncio.Event()
    async def wait(request):
        entered.set()
        try:
            await asyncio.Event().wait()
        finally:
            cleaning.set()
            await release.wait()
    case.vendor.register = wait
    task = asyncio.create_task(case.begin())
    try:
        await asyncio.wait_for(entered.wait(), 1)
        task.cancel()
        await asyncio.wait_for(cleaning.wait(), 1)
        task.cancel()
        await asyncio.sleep(0)
        assert not task.done()
    finally:
        release.set()
        if not task.done():
            task.cancel()
        await asyncio.gather(task, return_exceptions=True)
    assert task.cancelled()
    await case.runtime.close()
    await case.reopen()
    with pytest.raises(AuthorizationError) as failure:
        await case.begin()
    assert failure.value.code == "oauth_registration_unknown"
    assert len(case.vendor.registrations) == 1
