"""Feishu PKCE-compatible OAuth with SDK-owned state, rotation and encrypted storage."""

import asyncio
import math
import time

from connector_sdk import (
    AuthorizationRejected,
    ConfigRef,
    ExternalIdentity,
    OAuth2AuthorizationCode,
    OAuthAccessCredential,
    OAuthClientError,
    OAuthCredential,
    OAuthProtocol,
    OAuthRequest,
    OAuthTokens,
    SecretRef,
    StaticOAuthClient,
    VerifiedConnection,
)
from pydantic import Field

from .api import SCOPES, capabilities, decode, request
from .diagnostics import emit, reason_for, scope


class Credential(OAuthCredential):
    refresh_expires_at: float = Field(gt=0)


def material(value):
    return (type(value) is str and 0 < len(value) <= 16384
            and all(ord(c) > 32 and ord(c) != 127 and not 0xD800 <= ord(c) <= 0xDFFF
                    for c in value))


def duration(value):
    return type(value) in (int, float) and math.isfinite(value) and 0 < value <= 366 * 86400


class Protocol(OAuthProtocol):
    def token_request(self, ctx, form):
        payload = dict(form)
        headers = self.authenticate(ctx, payload)
        return OAuthRequest(json=payload, headers=headers)

    async def exchange(self, ctx, values):
        with scope("oauth_exchange"):
            emit("started")
            try:
                result = await super().exchange(ctx, values)
            except BaseException as error:
                emit("cancelled" if isinstance(error, asyncio.CancelledError) else "failed",
                     reason=reason_for(error))
                raise
            emit("succeeded")
            return result

    async def refresh(self, ctx, credential):
        with scope("oauth_refresh"):
            emit("started")
            try:
                result = await super().refresh(ctx, credential)
            except BaseException as error:
                emit("cancelled" if isinstance(error, asyncio.CancelledError) else "failed",
                     reason=reason_for(error))
                raise
            emit("succeeded")
            return result

    async def token_response(self, ctx, response, *, previous=None):
        emit("observed", phase="token_response", http_status=response.status_code)
        content = await response.read()
        try:
            data = decode(content)
        except Exception:
            emit("failed", phase="token_response", reason="invalid_response")
            raise
        code = data.get("code", 0)
        emit("observed", phase="token_response", http_status=response.status_code,
             provider_code=data.get("code"))
        if type(code) is not int:
            emit("failed", phase="token_response", reason="invalid_response")
            raise ValueError("feishu_invalid_token_response")
        # Only the documented definite HTTP 400 client rejection preserves an old refresh token.
        # Transient statuses remain uncertain even if their body says invalid_client.
        if response.status_code == 400:
            if code == 20002:
                emit("failed", phase="token_response", reason="client_rejected")
                raise OAuthClientError("oauth_client_authentication_failed")
            if code in (20003, 20004, 20008, 20010, 20024, 20026, 20037, 20064,
                        20065, 20066, 20073):
                emit("failed", phase="token_response", reason="provider_rejected")
                raise AuthorizationRejected()
        if response.status_code != 200 or code != 0 or "error" in data:
            emit("failed", phase="token_response", reason="provider_rejected")
            raise ValueError("feishu_token_exchange_failed")
        access, refresh = data.get("access_token"), data.get("refresh_token")
        expires, refresh_expires = data.get("expires_in"), data.get("refresh_token_expires_in")
        scope, kind = data.get("scope"), data.get("token_type")
        checks = {
            "access_valid": material(access), "refresh_valid": material(refresh),
            "access_expiry_valid": duration(expires),
            "refresh_expiry_valid": duration(refresh_expires),
            "token_type_valid": type(kind) is str and kind.lower() == "bearer",
            "scope_valid": (type(scope) is str and len(scope) <= 32768
                            and not any(ord(c) < 32 or ord(c) == 127 for c in scope)),
            "required_scope_granted": (type(scope) is str and len(scope) <= 32768
                                       and "offline_access" in scope.split()),
        }
        if not all(checks.values()):
            emit("failed", phase="token_response", checks=checks,
                 reason="invalid_material" if checks["required_scope_granted"]
                 else "required_scope_missing")
            raise ValueError("feishu_invalid_token_response")
        if previous is not None and refresh == previous.refresh_token.get_secret_value():
            emit("failed", phase="token_response", reason="refresh_not_rotated")
            raise ValueError("feishu_refresh_not_rotated")
        credential = Credential(access_token=access, refresh_token=refresh, scope=scope,
                                refresh_expires_at=time.time() + refresh_expires)
        return OAuthTokens(credential, expires)

    def can_refresh(self, credential):
        return super().can_refresh(credential) and credential.refresh_expires_at > time.time()

    def business_credential(self, credential):
        return OAuthAccessCredential(access_token=credential.access_token, scope=credential.scope)


class Auth(OAuth2AuthorizationCode):
    authorize_url = "https://accounts.feishu.cn/open-apis/authen/v1/authorize"
    # The v1 authorization endpoint documents v2 for PKCE; use it for both grants.
    token_url = "https://open.feishu.cn/open-apis/authen/v2/oauth/token"
    client = StaticOAuthClient(client_id=ConfigRef("app_id"),
                               client_secret=SecretRef("app_secret"),
                               token_endpoint_auth_method="client_secret_post")
    scopes = SCOPES
    pkce = True
    protocol = Protocol()
    credential_model = Credential

    async def resolve_identity(self, ctx):
        with scope("identity", transaction_id=ctx.transaction_id, request_id=ctx.request_id):
            emit("started")
            checks = None
            try:
                data = await request(ctx, "GET", "authen/v1/user_info", diagnostic=emit)
                account, tenant = data.get("open_id"), data.get("tenant_key")
                name = data.get("name")
                checks = {"account_valid": material(account) and len(account) <= 255,
                          "tenant_valid": material(tenant) and len(tenant) <= 255,
                          "name_valid": name is None or type(name) is str and len(name) <= 255}
                if not all(checks.values()):
                    raise AuthorizationRejected()
                result = VerifiedConnection(
                    identity=ExternalIdentity(account_id=account, tenant_id=tenant,
                                              display_name=name or None),
                    capabilities=capabilities(ctx.credential().scope),
                )
            except BaseException as error:
                emit("cancelled" if isinstance(error, asyncio.CancelledError) else "failed",
                     reason="invalid_identity" if checks is not None and not all(checks.values())
                     else reason_for(error), checks=checks)
                raise
            emit("succeeded", checks=checks)
            return result
