"""DingTalk's authCode callback and camelCase JSON OAuth token protocol."""

from connector_sdk import (
    AuthorizationRejected,
    ConfigRef,
    ExternalIdentity,
    HttpError,
    OAuth2AuthorizationCode,
    OAuthCredential,
    OAuthProtocol,
    OAuthRequest,
    OAuthTokens,
    SecretRef,
    StaticOAuthClient,
    VerifiedConnection,
)
from connector_sdk.auth import HeaderKey

from .api import SCOPES, decode, material, profile


class Protocol(OAuthProtocol):
    def authorization_parameters(self, ctx):
        return {**super().authorization_parameters(ctx), "prompt": "consent"}

    def callback(self, values):
        mapped = dict(values)
        # Accept only DingTalk's authCode spelling; conflicting spellings are ambiguous.
        if "code" in mapped:
            raise ValueError("dingtalk_invalid_callback")
        if "authCode" in mapped:
            mapped["code"] = mapped.pop("authCode")
        return super().callback(mapped)

    def token_request(self, ctx, form):
        body = {
            "clientId": ctx.client_id,
            "clientSecret": ctx.client_secret.get_secret_value(),
            "grantType": form["grant_type"],
        }
        if form["grant_type"] == "authorization_code":
            body["code"] = form["code"]
        elif form["grant_type"] == "refresh_token":
            body["refreshToken"] = form["refresh_token"]
        else:
            raise ValueError("dingtalk_unsupported_grant")
        return OAuthRequest(json=body, headers={"Accept": "application/json"})

    async def token_response(self, ctx, response, *, previous=None):
        data = decode(await response.read())
        if response.status_code != 200 or any(key in data for key in ("code", "errcode", "error")):
            # No undocumented error-code guesses. After a refresh was sent the SDK
            # must not assume the previous refresh material is still reusable.
            raise ValueError("dingtalk_token_exchange_failed")
        access, refresh, expires = (
            data.get("accessToken"),
            data.get("refreshToken"),
            data.get("expireIn"),
        )
        if (
            not material(access)
            or not material(refresh)
            or (type(expires) is not int or not 0 < expires <= 366 * 86400)
        ):
            raise ValueError("dingtalk_invalid_token_response")
        # DingTalk does not return a granted-scope snapshot or refresh expiry here.
        # Require explicit refresh material, but do not impose GitHub's rotation rule.
        return OAuthTokens(OAuthCredential(access_token=access, refresh_token=refresh), expires)


class Auth(OAuth2AuthorizationCode):
    authorize_url = "https://login.dingtalk.com/oauth2/auth"
    token_url = "https://api.dingtalk.com/v1.0/oauth2/userAccessToken"
    client = StaticOAuthClient(
        client_id=ConfigRef("client_id"),
        client_secret=SecretRef("client_secret"),
        token_endpoint_auth_method="client_secret_post",
    )
    scopes = SCOPES
    # The documented confidential-client flow has no PKCE parameters. Do not
    # claim S256 protection by sending an extension the provider may ignore.
    pkce = False
    protocol = Protocol()
    request_auth = HeaderKey("x-acs-dingtalk-access-token", field="access_token")

    async def resolve_identity(self, ctx):
        try:
            user = await profile(ctx)
        except HttpError:
            raise AuthorizationRejected() from None
        return VerifiedConnection(
            identity=ExternalIdentity(account_id=user.union_id, display_name=user.display_name)
        )
