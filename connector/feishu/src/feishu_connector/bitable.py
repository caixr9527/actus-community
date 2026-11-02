"""Single-record writes with fresh schema validation; no implicit field/option creation."""

import math
from urllib.parse import urlsplit

from connector_sdk import HttpError, OperationRejected

from .api import page, paging, request, require, result


def route(params):
    return f"bitable/v1/apps/{params.app_token}/tables/{params.table_id}"


async def tables(ctx, params):
    require(ctx, "bitable.read")
    data = await request(ctx, "GET", f"bitable/v1/apps/{params.app_token}/tables",
                         params=paging(params))
    return page(data, params.page_size)


async def listing(ctx, params, resource):
    require(ctx, "bitable.read")
    data = await request(ctx, "GET", route(params) + "/" + resource, params=paging(params))
    return page(data, params.page_size)


async def search(ctx, params):
    require(ctx, "bitable.read")
    body = params.model_dump(include={"view_id", "field_names", "sort", "filter"},
                             exclude_none=True)
    data = await request(ctx, "POST", route(params) + "/records/search",
                         params=paging(params), body=body)
    return page(data, params.page_size)


def record_result(data, record_id=None):
    record = data.get("record")
    if (type(record) is not dict or type(record.get("record_id")) is not str
            or not record["record_id"] or type(record.get("fields")) is not dict
            or (record_id is not None and record["record_id"] != record_id)):
        raise HttpError("feishu_invalid_record")
    return result(data)


async def get(ctx, params):
    require(ctx, "bitable.read")
    data = await request(ctx, "GET", route(params) + "/records/" + params.record_id)
    return record_result(data, params.record_id)


async def schema(ctx, params):
    fields, cursor, seen = {}, None, set()
    # No cross-user or cross-call cache. Incomplete schema never authorizes writes.
    for _ in range(20):
        query = {"page_size": 100}
        if cursor is not None:
            query["page_token"] = cursor
        data = await request(ctx, "GET", route(params) + "/fields", params=query)
        page(data, 100)
        for item in data["items"]:
            name, kind = item.get("field_name"), item.get("type")
            if (type(name) is not str or not name or name in fields or type(kind) is not int):
                raise HttpError("feishu_invalid_field_schema")
            fields[name] = item
        if not data["has_more"]:
            return fields
        cursor = data["page_token"]
        if cursor in seen:
            raise HttpError("feishu_invalid_page")
        seen.add(cursor)
    raise HttpError("feishu_field_schema_too_large")


def field_value(field, value):
    kind = field["type"]
    if kind not in (1, 2, 3, 4, 5, 7, 15):
        raise OperationRejected()
    if value is None:
        return  # Explicit null clears a supported field; omission leaves it unchanged.
    valid = False
    if kind == 1:
        valid = type(value) is str and len(value) <= 100000
    elif kind == 2:
        valid = (type(value) in (int, float) and abs(value) < 2**53
                 and math.isfinite(value))
    elif kind in (3, 4):
        prop = field.get("property")
        options = prop.get("options") if type(prop) is dict else None
        if type(options) is not list or any(
            type(option) is not dict or type(option.get("name")) is not str for option in options
        ):
            raise HttpError("feishu_invalid_field_schema")
        names = {option["name"] for option in options}
        if kind == 3:
            valid = type(value) is str and value in names
        else:
            valid = (type(value) is list and len(value) <= 100
                     and all(type(v) is str and v in names for v in value)
                     and len(set(value)) == len(value))
    elif kind == 5:
        valid = type(value) is int and 0 <= value < 2**53
    elif kind == 7:
        valid = type(value) is bool
    elif kind == 15:
        if (type(value) is dict and set(value) <= {"text", "link"}
                and type(value.get("link")) is str and len(value["link"]) <= 8192
                and ("text" not in value or (type(value["text"]) is str
                                             and len(value["text"]) <= 10000))):
            try:
                parsed = urlsplit(value["link"])
                valid = (parsed.scheme in ("http", "https") and bool(parsed.hostname)
                         and parsed.username is None and parsed.password is None
                         and all(ord(c) > 32 for c in value["link"]))
            except ValueError:
                pass
    if not valid:
        raise OperationRejected()


async def write(ctx, params, *, update=False):
    require(ctx, "bitable.write")
    try:
        fields = await schema(ctx, params)
        for name, value in params.fields.items():
            if name not in fields:
                raise OperationRejected()
            field_value(fields[name], value)
    except (HttpError, ValueError, TimeoutError):
        # Every request so far was a schema read; no record write was dispatched.
        raise OperationRejected() from None
    target = route(params) + "/records" + ("/" + params.record_id if update else "")
    data = await request(ctx, "PUT" if update else "POST", target,
                         body={"fields": params.fields})
    return record_result(data, params.record_id if update else None)
