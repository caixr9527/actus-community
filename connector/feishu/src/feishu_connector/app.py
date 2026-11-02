"""Twelve static operations. The SDK owns authorization, permits and lifecycle."""

from connector_sdk import AppSpec, Connector, HttpService, operation

from . import bitable, docs, wiki
from . import models as m
from .api import ORIGIN
from .auth import Auth


class App(Connector):
    spec = AppSpec(id="feishu", name="飞书", description="读取文档与知识库，查询和更新多维表格")
    config_model = m.Settings
    auth = Auth()
    services = {"api": HttpService(ORIGIN, auth="connection")}

    @operation(name="get_document", description="读取新版文档标题与版本信息。", effects="read",
               required_capabilities=("docs.read",))
    async def get_document(self, ctx, params: m.Document) -> m.Result:
        return await docs.document(ctx, params)

    @operation(name="read_document", description="读取新版文档纯文本，不保留富文本格式。",
               effects="read", required_capabilities=("docs.read",))
    async def read_document(self, ctx, params: m.Document) -> m.Result:
        return await docs.content(ctx, params)

    @operation(name="list_wiki_spaces", description="分页列出当前用户可访问的知识空间。",
               effects="read", required_capabilities=("wiki.read",))
    async def list_wiki_spaces(self, ctx, params: m.Page) -> m.Result:
        return await wiki.spaces(ctx, params)

    @operation(name="list_wiki_nodes", description="分页列出知识空间的根节点或指定节点的子节点。",
               effects="read", required_capabilities=("wiki.read",))
    async def list_wiki_nodes(self, ctx, params: m.WikiNodes) -> m.Result:
        return await wiki.nodes(ctx, params)

    @operation(name="get_wiki_node", description="解析知识库节点的实际资源类型和标识。",
               effects="read", required_capabilities=("wiki.read",))
    async def get_wiki_node(self, ctx, params: m.WikiNode) -> m.Result:
        return await wiki.node(ctx, params)

    @operation(name="list_tables", description="分页列出多维表格中的数据表。", effects="read",
               required_capabilities=("bitable.read",))
    async def list_tables(self, ctx, params: m.Tables) -> m.Result:
        return await bitable.tables(ctx, params)

    @operation(name="list_fields", description="分页读取数据表字段类型与选项。", effects="read",
               required_capabilities=("bitable.read",))
    async def list_fields(self, ctx, params: m.TablePage) -> m.Result:
        return await bitable.listing(ctx, params, "fields")

    @operation(name="list_views", description="分页列出数据表视图。", effects="read",
               required_capabilities=("bitable.read",))
    async def list_views(self, ctx, params: m.TablePage) -> m.Result:
        return await bitable.listing(ctx, params, "views")

    @operation(name="search_records", description="查询记录；视图与显式过滤排序不能混用。",
               effects="read", required_capabilities=("bitable.read",))
    async def search_records(self, ctx, params: m.SearchRecords) -> m.Result:
        return await bitable.search(ctx, params)

    @operation(name="get_record", description="按 record_id 读取单条记录。", effects="read",
               required_capabilities=("bitable.read",))
    async def get_record(self, ctx, params: m.Record) -> m.Result:
        return await bitable.get(ctx, params)

    @operation(name="create_record", description="新增单条记录，支持基础字段及已有选项。",
               effects="write", required_capabilities=("bitable.write",))
    async def create_record(self, ctx, params: m.CreateRecord) -> m.Result:
        return await bitable.write(ctx, params)

    @operation(name="update_record", description="按 ID 部分更新单条记录；显式 null 清空字段。",
               effects="write", required_capabilities=("bitable.write",))
    async def update_record(self, ctx, params: m.UpdateRecord) -> m.Result:
        return await bitable.write(ctx, params, update=True)
