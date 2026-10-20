import base64

from connector_sdk import (
    ApiKeyAuth,
    AppSpec,
    AuthUI,
    Connector,
    ExternalIdentity,
    HttpService,
    VerifiedConnection,
    operation,
)
from connector_sdk.auth import HeaderKey
from pydantic import BaseModel, ConfigDict, Field

from .common import CommonOperations
from .doc import DocOperations
from .manage import ManageOperations
from .mcp import call, profile
from .models import (
    CreateDocument,
    ListFiles,
    ListSpaceNodes,
    ListSpaces,
    ReadDocument,
    Result,
    SearchFiles,
)
from .sheet import SheetOperations
from .slides import SlidesOperations
from .smartsheet import SmartsheetOperations


class Profile(BaseModel):
    model_config = ConfigDict(strict=True)
    user_id: str = Field(min_length=1, pattern=r"\S")
    nick: str | None = None


class Auth(ApiKeyAuth):
    request_auth = HeaderKey("Authorization")
    ui = AuthUI(
        title="连接腾讯文档",
        description="输入腾讯文档个人 Token，验证账号后保存连接。",
        help_url="https://docs.qq.com",
    )

    async def verify(self, ctx) -> VerifiedConnection:
        identity = Profile.model_validate(await profile(ctx))
        return VerifiedConnection(
            identity=ExternalIdentity(
                account_id=identity.user_id,
                display_name=identity.nick or None,
            )
        )


class App(
    CommonOperations,
    DocOperations,
    ManageOperations,
    SheetOperations,
    SlidesOperations,
    SmartsheetOperations,
    Connector,
):
    spec = AppSpec(id="tencent-docs", name="腾讯文档", description="腾讯文档个人账号应用")
    auth = Auth()
    services = {"tencent": HttpService("https://docs.qq.com/openapi/", auth="connection")}

    @operation(name="list_files", description="分页列出最近文档，每页最多 20 条。", effects="read")
    async def list_files(self, ctx, params: ListFiles) -> Result:
        return await call(
            ctx,
            "manage.recent_online_file",
            {
                "num": params.page,
                "count": params.page_size,
                "order_by": {"recent_view": 0, "recent_edit": 1, "name": 2}[params.sort_by],
            },
        )

    @operation(name="search_files", description="按标题关键字搜索文档。", effects="read")
    async def search_files(self, ctx, params: SearchFiles) -> Result:
        return await call(ctx, "manage.search_file", {"search_key": params.keyword})

    @operation(name="list_spaces", description="分页列出当前账号的知识空间。", effects="read")
    async def list_spaces(self, ctx, params: ListSpaces) -> Result:
        return await call(
            ctx,
            "query_space_list",
            {
                "num": params.page,
                "descending": params.descending,
                "query_by": {"all": 0, "owned": 1, "joined": 2}[params.ownership],
                "order_by": {"recent_view": 1, "recent_edit": 2, "created": 3}[params.sort_by],
            },
        )

    @operation(name="list_space_nodes", description="分页读取指定空间的节点。", effects="read")
    async def list_space_nodes(self, ctx, params: ListSpaceNodes) -> Result:
        return await call(
            ctx,
            "query_space_node",
            {
                "space_id": params.space_id,
                "parent_id": params.parent_id,
                "num": params.page,
            },
        )

    @operation(
        name="read_document",
        description="读取文档正文；编辑定位请使用结构查询操作。",
        effects="read",
    )
    async def read_document(self, ctx, params: ReadDocument) -> Result:
        return await call(ctx, "get_content", {"file_id": params.file_id})

    @operation(name="create_document", description="以 Markdown 新建 Word 文档。", effects="write")
    async def create_document(self, ctx, params: CreateDocument) -> Result:
        return await call(
            ctx,
            "doc.create_with_markdown",
            {
                "title": params.title,
                "base64_markdown": base64.b64encode(params.markdown.encode()).decode("ascii"),
            },
        )
