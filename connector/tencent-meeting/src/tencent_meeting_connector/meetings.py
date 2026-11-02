"""Projected results, cursor paging and one-time-meeting write preflight."""

from urllib.parse import urlsplit

from connector_sdk import AuthorizationRejected, HttpError, OperationRejected

from . import models as m
from .mcp import call, catalog, failure


def view(data):
    if type(data) is not dict:
        failure("invalid_meeting")
    try:
        identifier = m.Meeting(meeting_id=data.get("meeting_id")).meeting_id
    except ValueError:
        failure("invalid_meeting")
    subject, kind = data.get("subject"), data.get("meeting_type")
    if (
        type(subject) is not str
        or not subject.strip()
        or len(subject) > 4096
        or type(kind) is not int
        or kind < 0
    ):
        failure("invalid_meeting")
    try:
        m.text(subject)
    except ValueError:
        failure("invalid_meeting")
    result = {"meeting_id": identifier, "subject": subject, "meeting_type": kind}
    mode = data.get("type")
    if mode is not None:
        if type(mode) is not int or mode not in (0, 1):
            failure("invalid_meeting")
        result["scheduled"] = mode == 0
    for key in ("meeting_code", "start_time", "end_time", "status", "join_url"):
        value = data.get(key)
        if value is None:
            continue
        if type(value) is not str or not 0 < len(value) <= 4096:
            failure("invalid_meeting")
        try:
            m.text(value)
        except ValueError:
            failure("invalid_meeting")
        if key == "meeting_code" and (
            not value.isascii() or not value.isdigit() or len(value) != 9
        ):
            failure("invalid_meeting")
        if key == "join_url":
            try:
                parsed = urlsplit(value)
                if (
                    parsed.scheme != "https"
                    or parsed.hostname not in {"meeting.tencent.com", "wemeet.qq.com"}
                    or parsed.username is not None
                    or parsed.password is not None
                    or parsed.port not in (None, 443)
                    or "\\" in value
                    or any(ord(c) <= 32 for c in value)
                ):
                    raise ValueError
            except ValueError:
                failure("invalid_join_url")
        if key in ("start_time", "end_time"):
            try:
                if value.isascii() and value.isdigit():
                    if not 0 < int(value) < 2**53:
                        raise ValueError
                else:
                    m.timestamp(value)
            except ValueError:
                failure("invalid_meeting_time")
        result[key] = value
    return m.MeetingView(**result)


def one(data):
    if "meeting_info_list" in data:
        items = data["meeting_info_list"]
        if type(items) is not list or len(items) != 1:
            failure("invalid_meeting")
        data = items[0]
    return view(data)


def page(data, previous):
    if ("meetings" in data) == ("meeting_info_list" in data):
        failure("invalid_page")
    items = data.get("meetings", data.get("meeting_info_list"))
    more, following = data.get("has_more"), data.get("next_page_token")
    if type(items) is not list or len(items) > 1000 or type(more) is not bool:
        failure("invalid_page")
    if more:
        if type(following) is not str or not 0 < len(following) <= 4096 or following == previous:
            failure("invalid_page")
        try:
            m.text(following)
        except ValueError:
            failure("invalid_page")
    elif following not in (None, ""):
        failure("invalid_page")
    meetings = [view(item) for item in items]
    if len({item.meeting_id for item in meetings}) != len(meetings):
        failure("invalid_page")
    return m.MeetingPage(
        meetings=meetings, has_more=more, next_page_token=following if more else None
    )


async def listing(ctx, params, *, ended=False, catalogue=None):
    catalogue = await catalog(ctx) if catalogue is None else catalogue
    arguments = params.model_dump(exclude_none=True)
    if not ended:
        arguments["is_show_all_sub_meetings"] = 0
    data = await call(
        ctx, catalogue, "get_user_ended_meetings" if ended else "get_user_meetings", arguments
    )
    return page(data, params.page_token)


async def get(ctx, params, *, by_code=False):
    data = await call(
        ctx,
        await catalog(ctx),
        "get_meeting_by_code" if by_code else "get_meeting",
        params.model_dump(),
    )
    result = one(data)
    if (
        result.meeting_code != params.meeting_code
        if by_code
        else result.meeting_id != params.meeting_id
    ):
        failure("meeting_mismatch")
    return result


async def preflight(ctx, params):
    try:
        catalogue = await catalog(ctx)
        meeting = one(await call(ctx, catalogue, "get_meeting", {"meeting_id": params.meeting_id}))
        if (
            meeting.meeting_id != params.meeting_id
            or meeting.meeting_type != 0
            or meeting.scheduled is not True
        ):
            raise OperationRejected()
        return catalogue, meeting
    except (HttpError, AuthorizationRejected):
        raise OperationRejected() from None


async def create(ctx, params):
    try:
        catalogue = await catalog(ctx)
    except (HttpError, AuthorizationRejected):
        raise OperationRejected() from None
    data = await call(ctx, catalogue, "schedule_meeting", params.model_dump() | {"meeting_type": 0})
    meeting = one(data)
    if meeting.meeting_type != 0 or meeting.scheduled is False or meeting.subject != params.subject:
        failure("unexpected_meeting_type")
    return meeting


async def update(ctx, params):
    catalogue, _meeting = await preflight(ctx, params)
    arguments = params.model_dump(exclude_none=True) | {"meeting_type": 0}
    data = await call(ctx, catalogue, "update_meeting", arguments)
    return acknowledgement(data, params.meeting_id)


def acknowledgement(data, identifier):
    if "success" in data and data["success"] is not True:
        failure("invalid_receipt")
    if "meeting_type" in data and (
        type(data["meeting_type"]) is not int or data["meeting_type"] != 0
    ):
        failure("unexpected_meeting_type")
    if data.get("success") is True:
        if "meeting_id" in data and data["meeting_id"] != identifier:
            failure("meeting_mismatch")
    else:
        result = one(data)
        if result.meeting_id != identifier or result.meeting_type != 0:
            failure("meeting_mismatch")
    return m.Receipt(meeting_id=identifier, accepted=True)


async def cancel(ctx, params):
    catalogue, _meeting = await preflight(ctx, params)
    data = await call(ctx, catalogue, "cancel_meeting", params.model_dump() | {"meeting_type": 0})
    return acknowledgement(data, params.meeting_id)
