"""SDK-managed personal Token; credential validity is not an invented account ID."""

from connector_sdk import ApiKeyAuth, AuthUI, ExternalIdentity, VerifiedConnection
from connector_sdk.auth import HeaderKey

from . import models as m
from .meetings import listing


class Auth(ApiKeyAuth):
    request_auth = HeaderKey("X-Tencent-Meeting-Token")
    ui = AuthUI(
        title="连接腾讯会议",
        description="在腾讯会议官方页面获取个人 Token，填写后验证连接。",
        help_url="https://meeting.tencent.com/ai-skill.html",
    )

    async def verify(self, ctx):
        await listing(ctx, m.Page())
        # These seven tools do not provide an authoritative current-account ID.
        # SDK connection ownership remains scoped to the platform principal.
        return VerifiedConnection(identity=ExternalIdentity())
