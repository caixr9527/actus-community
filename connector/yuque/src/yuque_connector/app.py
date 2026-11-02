"""Nine fixed operations: seven reads and two Markdown writes."""

from connector_sdk import AppSpec, Connector, HttpService, operation

from . import knowledge as k
from . import models as m
from .api import ORIGIN
from .auth import Auth


class App(Connector):
    spec = AppSpec(id="yuque", name="语雀", description="个人知识库查询与 Markdown 文档读写")
    auth = Auth()
    services = {"yuque": HttpService(ORIGIN, auth="connection")}

    @operation(name="get_current_user", description="查询当前 Token 对应的用户。", effects="read")
    async def get_current_user(self, ctx, params: m.Empty) -> m.UserView:
        return await k.current_user(ctx)

    @operation(
        name="list_groups", description="分页查询当前用户的团队；每页固定 100 条。", effects="read"
    )
    async def list_groups(self, ctx, params: m.Groups) -> m.GroupPage:
        return await k.groups(ctx, params)

    @operation(
        name="list_repositories", description="分页查询当前用户或指定团队的知识库。", effects="read"
    )
    async def list_repositories(self, ctx, params: m.Repositories) -> m.RepositoryPage:
        return await k.repositories(ctx, params)

    @operation(name="get_repository", description="按知识库 ID 查询详情。", effects="read")
    async def get_repository(self, ctx, params: m.Repository) -> m.RepositoryView:
        return await k.repository(ctx, params.repository_id)

    @operation(
        name="list_documents", description="分页查询指定知识库的文档元数据。", effects="read"
    )
    async def list_documents(self, ctx, params: m.Documents) -> m.DocumentPage:
        return await k.documents(ctx, params)

    @operation(
        name="get_document",
        description="读取普通文档的原始正文和格式，不读取草稿或附件。",
        effects="read",
    )
    async def get_document(self, ctx, params: m.Document) -> m.DocumentDetail:
        return await k.document(ctx, params)

    @operation(
        name="search", description="搜索文档或知识库；每次一页，每页固定 20 条。", effects="read"
    )
    async def search(self, ctx, params: m.Search) -> m.SearchPage:
        return await k.search(ctx, params)

    @operation(
        name="create_document",
        description="创建私密 Markdown 文档，不添加知识库目录节点。",
        effects="write",
    )
    async def create_document(self, ctx, params: m.Create) -> m.WriteReceipt:
        return await k.create(ctx, params)

    @operation(
        name="update_document",
        description="修改标题或整体替换 Markdown 正文；须提供读取时的更新时间。",
        effects="write",
    )
    async def update_document(self, ctx, params: m.Update) -> m.WriteReceipt:
        return await k.update(ctx, params)
