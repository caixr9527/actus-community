"""GitHub App user tokens, not OAuth App scope grants or installation tokens."""

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

from .api import decode, object_data, positive, request


class Credential(OAuthCredential):
    refresh_expires_at: float = Field(gt=0)


def token(value, prefix):
    return (
        type(value) is str
        and value.startswith(prefix)
        and len(prefix) < len(value) <= 16384
        and value.isascii()
        and all(ord(c) > 32 and ord(c) < 127 for c in value)
    )


class Protocol(OAuthProtocol):
    def token_request(self, ctx, form):
        form = dict(form)
        if form.get("grant_type") == "authorization_code":
            del form["grant_type"]
        headers = self.authenticate(ctx, form)
        headers["Accept"] = "application/json"
        return OAuthRequest(data=form, headers=headers)

    async def token_response(self, ctx, response, *, previous=None):
        data = decode(await response.read())
        if type(data) is not dict:
            raise ValueError("github_invalid_token_response")
        # GitHub can return OAuth errors with HTTP 200. Only definite client rejection
        # may let the SDK retain an old refresh credential, never transient responses.
        if response.status_code in (200, 400, 401):
            error = data.get("error")
            if error == "incorrect_client_credentials":
                raise OAuthClientError("oauth_client_authentication_failed")
            if error in ("bad_verification_code", "bad_refresh_token", "access_denied"):
                raise AuthorizationRejected()
        if response.status_code != 200 or "error" in data:
            raise ValueError("github_token_exchange_failed")
        access, refresh = data.get("access_token"), data.get("refresh_token")
        expires, refresh_expires = data.get("expires_in"), data.get("refresh_token_expires_in")
        if (
            not token(access, "ghu_")
            or not token(refresh, "ghr_")
            or type(expires) is not int
            or not 0 < expires <= 366 * 86400
            or type(refresh_expires) is not int
            or not 0 < refresh_expires <= 366 * 86400
            or data.get("scope") != ""
            or type(data.get("token_type")) is not str
            or data["token_type"].lower() != "bearer"
        ):
            raise ValueError("github_invalid_token_response")
        if previous is not None and refresh == previous.refresh_token.get_secret_value():
            raise ValueError("github_refresh_not_rotated")
        return OAuthTokens(
            Credential(
                access_token=access,
                refresh_token=refresh,
                scope="",
                refresh_expires_at=time.time() + refresh_expires,
            ),
            expires,
        )

    def can_refresh(self, credential):
        return super().can_refresh(credential) and credential.refresh_expires_at > time.time()

    def business_credential(self, credential):
        return OAuthAccessCredential(access_token=credential.access_token, scope="")


class Auth(OAuth2AuthorizationCode):
    authorize_url = "https://github.com/login/oauth/authorize"
    token_url = "https://github.com/login/oauth/access_token"
    client = StaticOAuthClient(
        client_id=ConfigRef("client_id"),
        client_secret=SecretRef("client_secret"),
        token_endpoint_auth_method="client_secret_post",
    )
    scopes = ("offline_access",)
    pkce = True
    credential_model = Credential
    protocol = Protocol()

    async def resolve_identity(self, ctx):
        profile = object_data(await request(ctx, "GET", "user"))
        identifier, login, kind = profile.get("id"), profile.get("login"), profile.get("type")
        if (
            not positive(identifier)
            or type(login) is not str
            or not login.strip()
            or len(login) > 255
            or kind != "User"
        ):
            raise AuthorizationRejected()
        # App registration permissions, installation access and user rights are resource-specific.
        # An empty scope is expected, and cannot be turned into global capability grants.
        return VerifiedConnection(
            identity=ExternalIdentity(account_id=str(identifier), display_name=login)
        )
