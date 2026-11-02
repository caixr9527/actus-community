"""Projected knowledge APIs and read-before-write checks for Markdown documents."""

from html.parser import HTMLParser
from urllib.parse import urlsplit

from connector_sdk import HttpError, OperationRejected

from . import models as m
from .api import failure, request


def object_data(value):
    if type(value) is not dict:
        failure("invalid_response")
    return value


def wire_id(value):
    if type(value) is not int or not 0 < value < 2**63:
        failure("invalid_id")
    return str(value)


def string(value, *, limit=4096, empty=False, multiline=False):
    if type(value) is not str or len(value) > limit or (not empty and not value.strip()):
        failure("invalid_text")
    try:
        return m.text(value, multiline=multiline)
    except ValueError:
        failure("invalid_text")


def optional_string(value, **kwargs):
    return None if value is None else string(value, **kwargs)


def updated_at(value):
    if value is None:
        return None
    try:
        return m.timestamp(value)
    except ValueError:
        failure("invalid_timestamp")


def visibility(value):
    if value is not None and (type(value) is not int or value not in (0, 1, 2)):
        failure("invalid_visibility")
    return value


def user_view(data, *, group=False):
    data = object_data(data)
    if "type" in data and data["type"] != ("Group" if group else "User"):
        failure("invalid_identity_type")
    model = m.GroupView if group else m.UserView
    return model(
        id=wire_id(data.get("id")),
        login=string(data.get("login"), limit=255),
        name=optional_string(data.get("name"), limit=255),
    )


async def current_user(ctx):
    return user_view((await request(ctx, "GET", "user"))["data"])


def repository_view(data):
    data = object_data(data)
    return m.RepositoryView(
        id=wire_id(data.get("id")),
        name=string(data.get("name")),
        slug=string(data.get("slug"), limit=1024),
        type=string(data.get("type"), limit=64),
        public=visibility(data.get("public")),
        namespace=optional_string(data.get("namespace"), limit=2048),
        updated_at=updated_at(data.get("updated_at")),
    )


def document_view(data):
    data = object_data(data)
    return m.DocumentView(
        id=wire_id(data.get("id")),
        repository_id=wire_id(data.get("book_id")),
        title=string(data.get("title")),
        slug=string(data.get("slug"), limit=1024),
        type=string(data.get("type"), limit=64),
        public=visibility(data.get("public")),
        updated_at=updated_at(data.get("updated_at")),
    )


def detail(data):
    base = document_view(data)
    if base.type != "Doc":
        failure("unsupported_document_type")
    format_ = data.get("format")
    if format_ not in ("markdown", "lake", "html"):
        failure("unsupported_document_format")
    body = string(data.get("body"), limit=m.BODY_LIMIT, empty=True, multiline=True)
    if len(body.encode("utf-8")) > m.BODY_LIMIT:
        failure("body_too_large")
    state = data.get("status")
    if state is not None:
        if type(state) is int and state in (0, 1):
            state = str(state)
        if type(state) is not str or state not in ("0", "1"):
            failure("invalid_document_status")
    return m.DocumentDetail(**base.model_dump(), format=format_, body=body, status=state)


def page_items(envelope, limit):
    items = envelope["data"]
    if type(items) is not list or len(items) > limit:
        failure("invalid_page")
    return items


def unique(items):
    if len({item.id for item in items}) != len(items):
        failure("duplicate_results")


def pagination(envelope, offset, limit, count):
    meta = object_data(envelope.get("meta", {}))
    total = meta.get("total")
    if total is not None and (type(total) is not int or not 0 <= total < 2**53):
        failure("invalid_page")
    more = None
    if total is not None:
        if (count and offset + count > total) or (offset < total and count == 0):
            failure("invalid_page")
        more = offset + count < total
    return {
        "offset": offset,
        "limit": limit,
        "total": total,
        "has_more": more,
        # Without total this is only a continuation candidate, never proof of another page.
        "next_offset": offset + count
        if count and more is not False and offset + count <= 1_000_000
        else None,
        "offset_limit_reached": bool(count and more is not False and offset + count > 1_000_000),
    }


async def groups(ctx, params):
    user = await current_user(ctx)
    envelope = await request(
        ctx, "GET", f"users/{user.id}/groups", params={"offset": params.offset}
    )
    items = [user_view(item, group=True) for item in page_items(envelope, 100)]
    unique(items)
    return m.GroupPage(items=items, **pagination(envelope, params.offset, 100, len(items)))


async def repositories(ctx, params):
    if params.owner_kind == "user":
        path = f"users/{(await current_user(ctx)).id}/repos"
    else:
        path = f"groups/{params.group_id}/repos"
    envelope = await request(
        ctx, "GET", path, params={"offset": params.offset, "limit": params.limit}
    )
    items = [repository_view(item) for item in page_items(envelope, params.limit)]
    unique(items)
    return m.RepositoryPage(
        items=items, **pagination(envelope, params.offset, params.limit, len(items))
    )


async def repository(ctx, identifier):
    result = repository_view((await request(ctx, "GET", f"repos/{identifier}"))["data"])
    if result.id != identifier:
        failure("repository_mismatch")
    return result


async def documents(ctx, params):
    envelope = await request(
        ctx,
        "GET",
        f"repos/{params.repository_id}/docs",
        params={"offset": params.offset, "limit": params.limit, "deleted": "false"},
    )
    items = [document_view(item) for item in page_items(envelope, params.limit)]
    unique(items)
    if any(item.repository_id != params.repository_id for item in items):
        failure("repository_mismatch")
    return m.DocumentPage(
        items=items, **pagination(envelope, params.offset, params.limit, len(items))
    )


async def document_data(ctx, params):
    data = object_data(
        (await request(ctx, "GET", f"repos/{params.repository_id}/docs/{params.document_id}"))[
            "data"
        ]
    )
    result = detail(data)
    if result.id != params.document_id or result.repository_id != params.repository_id:
        failure("document_mismatch")
    return data, result


async def document(ctx, params):
    return (await document_data(ctx, params))[1]


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def snippet(value):
    raw = string(value, limit=16_384, empty=True, multiline=True)
    parser = PlainText()
    parser.feed(raw)
    parser.close()
    return string("".join(parser.parts), limit=16_384, empty=True, multiline=True)


def search_url(value):
    if value is None:
        return None
    value = string(value, limit=4096)
    if value.startswith("/") and not value.startswith("//"):
        value = "https://www.yuque.com" + value
    try:
        parsed = urlsplit(value)
        if (
            parsed.scheme != "https"
            or parsed.hostname != "www.yuque.com"
            or parsed.username is not None
            or parsed.password is not None
            or parsed.port not in (None, 443)
            or "\\" in value
            or any(c.isspace() for c in value)
        ):
            raise ValueError
    except ValueError:
        failure("invalid_search_url")
    return value


def search_item(data, kind):
    data = object_data(data)
    identifier = wire_id(data.get("id"))
    if data.get("type") != kind:
        failure("search_type_mismatch")
    repository_id = None
    if data.get("target") is not None:
        target = object_data(data["target"])
        if wire_id(target.get("id")) != identifier:
            failure("search_target_mismatch")
        if kind == "doc" and target.get("book_id") is not None:
            repository_id = wire_id(target["book_id"])
    return m.SearchItem(
        id=identifier,
        type=kind,
        title=snippet(data.get("title")),
        summary=snippet(data["summary"]) if data.get("summary") is not None else None,
        url=search_url(data.get("url")),
        repository_id=repository_id,
    )


async def search(ctx, params):
    query = {"q": params.query, "type": params.type, "page": params.page}
    if params.scope is not None:
        query["scope"] = params.scope
    envelope = await request(ctx, "GET", "search", params=query)
    items = [search_item(item, params.type) for item in page_items(envelope, 20)]
    unique(items)
    meta = object_data(envelope.get("meta", {}))
    for key, expected in (("pageNo", params.page), ("pageSize", 20)):
        if key in meta and (type(meta[key]) is not int or meta[key] != expected):
            failure("invalid_page")
    paging = pagination(envelope, (params.page - 1) * 20, 20, len(items))
    candidate = params.page + 1 if paging["next_offset"] is not None and params.page < 100 else None
    return m.SearchPage(
        items=items,
        page=params.page,
        page_size=20,
        total=paging["total"],
        has_more=paging["has_more"],
        next_page=candidate,
        page_limit_reached=params.page == 100 and paging["has_more"] is not False,
    )


def receipt(data, params, *, public, title, body, slug=None):
    result = detail(data)
    if (
        result.repository_id != params.repository_id
        or result.type != "Doc"
        or result.format != "markdown"
        or result.public != public
        or result.title != title
        or result.body != body
        or result.updated_at is None
        or (slug is not None and result.slug != slug)
        or (isinstance(params, m.Update) and result.id != params.document_id)
    ):
        failure("invalid_write_receipt")
    return m.WriteReceipt(
        document=m.DocumentView(**result.model_dump(exclude={"format", "body", "status"})),
        accepted=True,
        content_verified=False,
    )


async def create(ctx, params):
    try:
        repo = await repository(ctx, params.repository_id)
        if repo.type != "Book":
            raise OperationRejected()
    except HttpError:
        raise OperationRejected() from None
    data = object_data(
        (
            await request(
                ctx,
                "POST",
                f"repos/{params.repository_id}/docs",
                body={
                    "title": params.title,
                    "body": params.body,
                    "format": "markdown",
                    "public": 0,
                },
            )
        )["data"]
    )
    return receipt(data, params, public=0, title=params.title, body=params.body)


async def update(ctx, params):
    try:
        repo = await repository(ctx, params.repository_id)
        data, existing = await document_data(ctx, params)
        draft = data.get("body_draft")
        if (
            repo.type != "Book"
            or existing.format != "markdown"
            or existing.public is None
            or existing.updated_at != params.expected_updated_at
            or data.get("deleted_at") not in (None, "")
            or (draft is not None and (type(draft) is not str or draft not in ("", existing.body)))
        ):
            raise OperationRejected()
    except HttpError:
        raise OperationRejected() from None
    body = params.model_dump(include={"title", "body"}, exclude_none=True)
    body |= {"format": "markdown", "public": existing.public}
    result = object_data(
        (
            await request(
                ctx, "PUT", f"repos/{params.repository_id}/docs/{params.document_id}", body=body
            )
        )["data"]
    )
    return receipt(
        result,
        params,
        public=existing.public,
        title=params.title if params.title is not None else existing.title,
        body=params.body if params.body is not None else existing.body,
        slug=existing.slug,
    )
