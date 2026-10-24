from connector_sdk import (
    AppSpec,
    AuthorizationRejected,
    AuthUI,
    ConfigRef,
    Connector,
    CredentialModel,
    ExternalIdentity,
    FormAuth,
    FormAuthResult,
    HttpService,
    operation,
)
from connector_sdk.auth import Bearer
from pydantic import BaseModel, ConfigDict, Field, SecretStr


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    api_base_url: str = Field(description="服务管理员配置的工单 API HTTPS 地址")


class Login(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    tenant: str = Field(
        min_length=1, max_length=100, pattern=r"^[^\s\x00-\x1f\x7f]+$", title="租户",
    )
    username: str = Field(
        min_length=1, max_length=100, pattern=r"^[^\s\x00-\x1f\x7f]+$", title="用户名",
    )
    password: SecretStr = Field(min_length=1, max_length=1024, title="密码")


class Token(CredentialModel):
    token: SecretStr = Field(min_length=1)


class LoginReply(BaseModel):
    model_config = ConfigDict(strict=True, hide_input_in_errors=True)
    authenticated: bool
    token: SecretStr | None = Field(default=None, min_length=1)


class Profile(BaseModel):
    model_config = ConfigDict(strict=True, hide_input_in_errors=True)
    account_id: str = Field(min_length=1, pattern=r"\S")
    tenant_id: str = Field(min_length=1, pattern=r"\S")
    display_name: str | None = None
    permissions: list[str] | None = None


class Auth(FormAuth):
    input_model = Login
    credential_model = Token
    request_auth = Bearer()
    ui = AuthUI(
        title="连接工单示例",
        description="输入租户、用户名和密码，验证身份后仅保存业务 Token。",
    )

    async def verify(self, ctx, submission: Login) -> FormAuthResult:
        reply = LoginReply.model_validate(await ctx.http("login").request_json(
            "POST", "login", json={
                "tenant": submission.tenant,
                "username": submission.username,
                "password": submission.password.get_secret_value(),
            },
        ))
        if not reply.authenticated:
            raise AuthorizationRejected()
        if reply.token is None:
            raise ValueError("invalid_login_response")
        credential = Token(token=reply.token)
        profile = Profile.model_validate(
            await ctx.http("api", credential=credential).get_json("me"),
        )
        if profile.tenant_id != submission.tenant:
            raise AuthorizationRejected()
        return FormAuthResult(
            credential=credential,
            identity=ExternalIdentity(
                account_id=profile.account_id,
                tenant_id=profile.tenant_id,
                display_name=profile.display_name,
            ),
            capabilities={"tickets.read": "tickets.read" in profile.permissions}
            if profile.permissions is not None else None,
        )


class ListTickets(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(default="", max_length=200)
    limit: int = Field(default=20, ge=1, le=100)


class Ticket(BaseModel):
    model_config = ConfigDict(strict=True)
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)


class Tickets(BaseModel):
    model_config = ConfigDict(strict=True)
    items: list[Ticket] = Field(max_length=100)


class App(Connector):
    spec = AppSpec(id="form-demo", name="多字段工单示例", description="密码换取 Token 后读取工单")
    config_model = Settings
    auth = Auth()
    services = {
        "login": HttpService(ConfigRef("api_base_url"), auth="none"),
        "api": HttpService(ConfigRef("api_base_url"), auth="connection"),
    }

    @operation(
        name="list_tickets", description="按关键词读取工单，最多返回 100 条。", effects="read",
        required_capabilities=("tickets.read",),
    )
    async def list_tickets(self, ctx, params: ListTickets) -> Tickets:
        return Tickets.model_validate(await ctx.http("api").get_json(
            "tickets", params={"q": params.query, "limit": str(params.limit)},
        ))
