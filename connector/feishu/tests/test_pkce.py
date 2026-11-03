"""Exercise the supported endpoint pair without dropping PKCE or retrying failed codes."""

import base64
import hashlib
import json
from urllib.parse import parse_qs, urlsplit

import pytest
from vendor import TOKEN_URL


async def test_authorization_uses_v2_token_endpoint_with_s256(case):
    view = await case.begin()
    url = urlsplit(view.authorization_url)
    assert (url.scheme, url.netloc, url.path) == (
        "https", "accounts.feishu.cn", "/open-apis/authen/v1/authorize")
    query = parse_qs(url.query)
    assert query["code_challenge_method"] == ["S256"]
    assert "code_verifier" not in query and "client_secret" not in query
    reply = await case.complete(view)
    assert reply.data.status == "connected", reply
    token_request, identity_request = case.vendor.calls
    assert str(token_request.url) == "https://open.feishu.cn/open-apis/authen/v2/oauth/token"
    assert identity_request.url.path == "/open-apis/authen/v1/user_info"
    form = case.vendor.tokens[0]
    assert 43 <= len(form["code_verifier"]) <= 128
    digest = hashlib.sha256(form["code_verifier"].encode("ascii")).digest()
    assert base64.urlsafe_b64encode(digest).rstrip(b"=").decode() == query["code_challenge"][0]


@pytest.mark.parametrize("fault", [
    "missing_verifier", "wrong_verifier", "missing_challenge", "wrong_challenge",
])
async def test_pkce_rejection_never_saves_connection_or_retries(case, monkeypatch, capfd, fault):
    from feishu_connector.auth import Protocol

    view = await case.begin()
    if fault.endswith("verifier"):
        original = Protocol.token_request

        def token_request(self, ctx, form):
            # Fault injection uses only the public request-construction extension point.
            form = dict(form)
            if fault == "missing_verifier":
                form.pop("code_verifier")
            else:
                form["code_verifier"] = "x" * 43
            return original(self, ctx, form)

        monkeypatch.setattr(Protocol, "token_request", token_request)
    else:
        case.vendor.challenge = "" if fault == "missing_challenge" else "mismatched-challenge"
    reply = await case.complete(view)
    assert reply.data.status == "failed"
    records = [json.loads(line.removeprefix("ACTUS_DIAGNOSTIC_V1 "))
               for line in capfd.readouterr().err.splitlines()
               if line.startswith("ACTUS_DIAGNOSTIC_V1 ")]
    assert any(r.get("http_status") == 400 and r.get("provider_code") == 20049 for r in records)
    assert len(case.vendor.calls) == len(case.vendor.tokens) == 1
    assert str(case.vendor.calls[0].url) == TOKEN_URL
    assert case.vendor.generation == 0
    assert (await case.sdk.list_connections(**case.metadata("connection.list"))).data == ()
    assert (await case.complete(view)).data == reply.data
    assert len(case.vendor.calls) == 1
