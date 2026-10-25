"""Standard SDK OAuth; application code resolves only the authenticated identity."""

from connector_sdk import (
    AuthorizationRejected,
    ConfigRef,
    ExternalIdentity,
    OAuth2AuthorizationCode,
    VerifiedConnection,
)

from .mcp import permissions, session
from .protocol import ORIGIN
from .schema import validate


def identifier(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 2048:
        raise AuthorizationRejected()
    return value


class Auth(OAuth2AuthorizationCode):
    authorize_url = ORIGIN + "/authorize"
    token_url = ORIGIN + "/token"
    revocation_url = ORIGIN + "/token"
    issuer = ORIGIN
    client_id = ConfigRef("client_id")
    client_secret = None
    token_endpoint_auth_method = "none"
    scopes = ("default",)

    async def resolve_identity(self, ctx):
        async with session(ctx) as connection:
            tools = await connection.tools()
            if "notion-get-self" not in tools:
                raise AuthorizationRejected()
            validate({}, tools["notion-get-self"])
            data = (await connection.tool("notion-get-self", {})).data
            workspace, user = data.get("workspace"), data.get("user")
            if (not isinstance(workspace, dict) or not isinstance(user, dict)
                    or user.get("type") != "person"):
                raise AuthorizationRejected()
            tenant, account = identifier(workspace.get("id")), identifier(user.get("id"))
            name = user.get("name")
            if not isinstance(name, str) or not name.strip():
                name = None
            return VerifiedConnection(
                identity=ExternalIdentity(account_id=account, tenant_id=tenant, display_name=name),
                capabilities=await permissions(connection, tools),
            )
