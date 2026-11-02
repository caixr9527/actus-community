"""Feishu OAuth v3 with SDK-owned state, S256, refresh rotation and encrypted storage."""

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
    OAuthTokens,
    SecretRef,
    StaticOAuthClient,
    VerifiedConnection,
)
from pydantic import Field

from .api import SCOPES, capabilities, decode, request


class Credential(OAuthCredential):
    refresh_expires_at: float = Field(gt=0)


def material(value):
    return (type(value) is str and 0 < len(value) <= 16384
            and all(ord(c) > 32 and ord(c) != 127 and not 0xD800 <= ord(c) <= 0xDFFF
                    for c in value))


def duration(value):
    return type(value) in (int, float) and math.isfinite(value) and 0 < value <= 366 * 86400


class Protocol(OAuthProtocol):
    async def token_response(self, ctx, response, *, previous=None):
        data = decode(await response.read())
        code = data.get("code", 0)
        if type(code) is not int:
            raise ValueError("feishu_invalid_token_response")
        # Only the documented definite HTTP 400 client rejection preserves an old refresh token.
        # Transient statuses remain uncertain even if their body says invalid_client.
        if response.status_code == 400:
            if code == 20002:
                raise OAuthClientError("oauth_client_authentication_failed")
            if code in (20003, 20004, 20008, 20010, 20024, 20026, 20037, 20064,
                        20065, 20066, 20073):
                raise AuthorizationRejected()
        if response.status_code != 200 or code != 0 or "error" in data:
            raise ValueError("feishu_token_exchange_failed")
        access, refresh = data.get("access_token"), data.get("refresh_token")
        expires, refresh_expires = data.get("expires_in"), data.get("refresh_token_expires_in")
        scope, kind = data.get("scope"), data.get("token_type")
        if (not material(access) or not material(refresh)
                or not duration(expires) or not duration(refresh_expires)
                or type(kind) is not str or kind.lower() != "bearer"
                or type(scope) is not str or len(scope) > 32768
                or "offline_access" not in scope.split()
                or any(ord(c) < 32 or ord(c) == 127 for c in scope)):
            raise ValueError("feishu_invalid_token_response")
        if previous is not None and refresh == previous.refresh_token.get_secret_value():
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
    token_url = "https://accounts.feishu.cn/oauth/v3/token"
    client = StaticOAuthClient(client_id=ConfigRef("app_id"),
                               client_secret=SecretRef("app_secret"),
                               token_endpoint_auth_method="client_secret_post")
    scopes = SCOPES
    pkce = True
    protocol = Protocol()
    credential_model = Credential

    async def resolve_identity(self, ctx):
        data = await request(ctx, "GET", "authen/v1/user_info")
        account, tenant, name = data.get("open_id"), data.get("tenant_key"), data.get("name")
        if (not material(account) or len(account) > 255
                or not material(tenant) or len(tenant) > 255
                or (name is not None and (type(name) is not str or len(name) > 255))):
            raise AuthorizationRejected()
        return VerifiedConnection(
            identity=ExternalIdentity(account_id=account, tenant_id=tenant,
                                      display_name=name or None),
            capabilities=capabilities(ctx.credential().scope),
        )
