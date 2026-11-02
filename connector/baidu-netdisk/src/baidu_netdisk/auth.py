"""Baidu protocol differences; SDK retains transactions, credentials and refresh ownership."""

import json
import math

from connector_sdk import (
    AuthorizationRejected,
    ConfigRef,
    ExternalIdentity,
    OAuth2AuthorizationCode,
    OAuthClientError,
    OAuthCredential,
    OAuthProtocol,
    OAuthRequest,
    OAuthTokens,
    SecretRef,
    StaticOAuthClient,
    VerifiedConnection,
)
from connector_sdk.auth import QueryKey

from .api import request
from .models import text


class Protocol(OAuthProtocol):
    def authorization_parameters(self, ctx):
        return {"scope": ",".join(ctx.scopes)}

    def token_request(self, ctx, form):
        headers = self.authenticate(ctx, form)
        return OAuthRequest(method="GET", params=form, headers=headers)

    async def token_response(self, ctx, response, *, previous=None):
        def pairs(items):
            result = {}
            for key, value in items:
                if key in result:
                    raise ValueError("invalid_baidu_token_response")
                result[key] = value
            return result

        try:
            data = json.loads(await response.read(), object_pairs_hook=pairs)
        except (ValueError, UnicodeError):
            raise ValueError("invalid_baidu_token_response") from None
        if type(data) is not dict:
            raise ValueError("invalid_baidu_token_response")
        # A transient HTTP failure cannot prove that a rotating refresh token was unused.
        # Only a definite OAuth response may trigger the SDK's client-error recovery path.
        if response.status_code not in (200, 400, 401, 403):
            raise ValueError("baidu_token_exchange_failed")
        error = data.get("error")
        if error == "invalid_client":
            raise OAuthClientError("oauth_client_authentication_failed")
        if error in ("invalid_grant", "invalid refresh token", "invalid refresh"):
            raise AuthorizationRejected()
        if response.status_code != 200 or "error" in data:
            raise ValueError("baidu_token_exchange_failed")
        access, refresh, expires = (data.get(k) for k in
                                    ("access_token", "refresh_token", "expires_in"))
        if (type(access) is not str or not access or type(refresh) is not str or not refresh
                or type(expires) not in (int, float) or not math.isfinite(expires)
                or not 0 < expires <= 366 * 86400):
            raise ValueError("invalid_baidu_token_response")
        text(access)
        text(refresh)
        scope = data.get("scope")
        if scope is None:
            scope = previous.scope if previous is not None else " ".join(ctx.scopes)
        if type(scope) is not str:
            raise ValueError("invalid_baidu_token_response")
        granted = scope.replace(",", " ").split()
        if not {"basic", "netdisk"}.issubset(granted):
            raise AuthorizationRejected()
        return OAuthTokens(OAuthCredential(access_token=access, refresh_token=refresh,
                                            scope=" ".join(granted)), expires)


class Auth(OAuth2AuthorizationCode):
    authorize_url = "https://openapi.baidu.com/oauth/2.0/authorize"
    token_url = "https://openapi.baidu.com/oauth/2.0/token"
    client = StaticOAuthClient(client_id=ConfigRef("client_id"),
                               client_secret=SecretRef("client_secret"),
                               token_endpoint_auth_method="client_secret_post")
    scopes = ("basic", "netdisk")
    pkce = False
    protocol = Protocol()
    request_auth = QueryKey("access_token", field="access_token")

    async def resolve_identity(self, ctx):
        data = await request(ctx, "GET", "rest/2.0/xpan/nas", {"method": "uinfo"})
        account = data.get("uk")
        if type(account) not in (str, int) or not str(account) or len(str(account)) > 255:
            raise AuthorizationRejected()
        text(str(account))
        display = data.get("netdisk_name") or data.get("baidu_name")
        if display is not None:
            if type(display) is not str or len(display) > 255:
                raise AuthorizationRejected()
            text(display)
        return VerifiedConnection(identity=ExternalIdentity(account_id=str(account),
                                                             display_name=display))
