"""Explicit JSON operations; no arbitrary MCP dispatch or implicit write retries."""

from connector_sdk import AppSpec, Connector, HttpService, operation

from . import models as m
from .auth import Auth
from .mcp import call
from .protocol import ORIGIN


class App(Connector):
    spec = AppSpec(id="notion", name="Notion", description="Notion 工作区 OAuth 与有界 MCP 工具")
    config_model = m.Settings
    auth = Auth()
    services = {"notion": HttpService(ORIGIN + "/", auth="connection")}

    @operation(name="search", description="搜索已连接的 Notion 工作区内容。", effects="read",
               required_capabilities=("search",))
    async def search(self, ctx, params: m.Search) -> m.Result:
        return await call(ctx, "search", params.model_dump())

    @operation(name="fetch", description="按 ID 或 URL 读取 Notion 页面、数据库或视图。",
               effects="read", required_capabilities=("fetch",))
    async def fetch(self, ctx, params: m.Fetch) -> m.Result:
        return await call(ctx, "fetch", params.model_dump())

    @operation(name="get_users", description="查询 Notion 用户，保留不透明分页游标。",
               effects="read", required_capabilities=("get_users",))
    async def get_users(self, ctx, params: m.Users) -> m.Result:
        return await call(ctx, "get_users", params.model_dump(exclude_none=True))

    @operation(name="get_teams", description="查询 Notion 团队空间。", effects="read",
               required_capabilities=("get_teams",))
    async def get_teams(self, ctx, params: m.Teams) -> m.Result:
        return await call(ctx, "get_teams", params.model_dump(exclude_none=True))

    @operation(name="get_comments", description="读取页面或讨论的评论。", effects="read",
               required_capabilities=("get_comments",))
    async def get_comments(self, ctx, params: m.Comments) -> m.Result:
        return await call(ctx, "get_comments", params.model_dump(exclude_none=True))

    @operation(name="query_database_view", description="仅按既有数据库视图查询，不接受 SQL。",
               effects="read", required_capabilities=("query_database_view",))
    async def query_database_view(self, ctx, params: m.View) -> m.Result:
        return await call(ctx, "query_database_view", params.model_dump(exclude_none=True))

    @operation(name="get_async_task", description="按原 task_id 查询 Notion 异步任务。",
               effects="read", required_capabilities=("get_async_task",))
    async def get_async_task(self, ctx, params: m.Task) -> m.Result:
        return await call(ctx, "get_async_task", params.model_dump())

    @operation(name="create_page", description="在指定父页面下创建一个页面，可返回异步任务。",
               effects="write", required_capabilities=("create_page",))
    async def create_page(self, ctx, params: m.CreatePage) -> m.Result:
        return await call(ctx, "create_page", params.model_dump(exclude_none=True))

    @operation(name="update_page", description="替换单页 Markdown 正文，可返回异步任务。",
               effects="write", required_capabilities=("update_page",))
    async def update_page(self, ctx, params: m.UpdatePage) -> m.Result:
        return await call(ctx, "update_page", params.model_dump(exclude_none=True))

    @operation(name="create_comment", description="添加评论，可能通知工作区协作者。",
               effects="write", required_capabilities=("create_comment",))
    async def create_comment(self, ctx, params: m.CreateComment) -> m.Result:
        return await call(ctx, "create_comment", params.model_dump(exclude_none=True))

    @operation(name="move_pages", description="移动最多 100 个页面或数据库。", effects="write",
               required_capabilities=("move_pages",))
    async def move_pages(self, ctx, params: m.Move) -> m.Result:
        return await call(ctx, "move_pages", params.model_dump(exclude_none=True))

    @operation(name="duplicate_page", description="异步复制页面，返回后查询原异步任务。",
               effects="write", required_capabilities=("duplicate_page", "get_async_task"))
    async def duplicate_page(self, ctx, params: m.Duplicate) -> m.Result:
        return await call(ctx, "duplicate_page", params.model_dump())
