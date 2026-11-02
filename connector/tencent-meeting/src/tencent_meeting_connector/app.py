"""Seven static operations; only ordinary one-time meetings may be mutated."""

from connector_sdk import AppSpec, Connector, HttpService, operation

from . import meetings
from . import models as m
from .auth import Auth
from .mcp import ORIGIN


class App(Connector):
    spec = AppSpec(
        id="tencent-meeting", name="腾讯会议", description="个人会议查询、预约、修改与取消"
    )
    auth = Auth()
    services = {"meeting": HttpService(ORIGIN, auth="connection")}

    @operation(name="list_meetings", description="分页查询即将开始、进行中的会议。", effects="read")
    async def list_meetings(self, ctx, params: m.Page) -> m.MeetingPage:
        return await meetings.listing(ctx, params)

    @operation(
        name="list_ended_meetings", description="按时间范围分页查询已结束会议。", effects="read"
    )
    async def list_ended_meetings(self, ctx, params: m.EndedPage) -> m.MeetingPage:
        return await meetings.listing(ctx, params, ended=True)

    @operation(
        name="get_meeting", description="按会议 ID 查询详情，不返回主持人密钥。", effects="read"
    )
    async def get_meeting(self, ctx, params: m.Meeting) -> m.MeetingView:
        return await meetings.get(ctx, params)

    @operation(name="get_meeting_by_code", description="按 9 位会议号查询详情。", effects="read")
    async def get_meeting_by_code(self, ctx, params: m.MeetingCode) -> m.MeetingView:
        return await meetings.get(ctx, params, by_code=True)

    @operation(
        name="create_meeting", description="预约一次性普通会议，可能产生会议通知。", effects="write"
    )
    async def create_meeting(self, ctx, params: m.Create) -> m.MeetingView:
        return await meetings.create(ctx, params)

    @operation(
        name="update_meeting",
        description="修改一次性普通会议；修改时间须提供起止时间。",
        effects="write",
    )
    async def update_meeting(self, ctx, params: m.Update) -> m.Receipt:
        return await meetings.update(ctx, params)

    @operation(
        name="cancel_meeting", description="取消一次性普通会议，可能通知参会者。", effects="write"
    )
    async def cancel_meeting(self, ctx, params: m.Meeting) -> m.Receipt:
        return await meetings.cancel(ctx, params)
