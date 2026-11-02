"""SDK-owned personal Token and an authoritative current-user identity."""

from connector_sdk import ApiKeyAuth, AuthUI, ExternalIdentity, VerifiedConnection
from connector_sdk.auth import HeaderKey

from .knowledge import current_user


class Auth(ApiKeyAuth):
    request_auth = HeaderKey("X-Auth-Token")
    ui = AuthUI(
        title="连接语雀",
        description="填写公网主站的个人 Token，验证当前用户身份。",
        help_url="https://www.yuque.com/settings/tokens",
    )

    async def verify(self, ctx):
        user = await current_user(ctx)
        return VerifiedConnection(
            identity=ExternalIdentity(
                account_id=user.id,
                display_name=user.name or user.login,
            )
        )
