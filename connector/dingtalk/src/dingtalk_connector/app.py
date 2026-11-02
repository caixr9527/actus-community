"""Five static operations with four explicit write effects."""

from connector_sdk import AppSpec, Connector, HttpService, operation

from . import models as m
from . import todo
from .api import ORIGIN
from .auth import Auth


class App(Connector):
    spec = AppSpec(id="dingtalk", name="钉钉", description="个人待办创建、修改与本人执行状态管理")
    config_model = m.Settings
    auth = Auth()
    services = {"api": HttpService(ORIGIN, auth="connection")}

    @operation(
        name="get_current_user", description="读取当前授权用户的标识和昵称。", effects="read"
    )
    async def get_current_user(self, ctx, params: m.Empty) -> m.Profile:
        return await todo.current_user(ctx, params)

    @operation(
        name="create_personal_todo",
        description="创建个人待办，执行者固定为本人。可能产生待办通知。",
        effects="write",
    )
    async def create_personal_todo(self, ctx, params: m.CreateTodo) -> m.Created:
        return await todo.create(ctx, params)

    @operation(
        name="update_personal_todo",
        description="修改待办标题、描述或截止时间；省略不修改。",
        effects="write",
    )
    async def update_personal_todo(self, ctx, params: m.UpdateTodo) -> m.Receipt:
        return await todo.update(ctx, params)

    @operation(
        name="set_my_executor_status",
        description="完成或恢复本人执行状态，不表示整个任务已完成。",
        effects="write",
    )
    async def set_my_executor_status(self, ctx, params: m.ExecutorStatus) -> m.ExecutorReceipt:
        return await todo.executor_status(ctx, params)

    @operation(
        name="delete_personal_todo",
        description="以当前用户身份删除待办，可能影响其他参与者。",
        effects="write",
    )
    async def delete_personal_todo(self, ctx, params: m.Task) -> m.Receipt:
        return await todo.delete(ctx, params)
