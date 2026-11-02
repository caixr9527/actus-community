"""Issue-only mutations, explicit label replacement, and no implicit write retries."""

from types import SimpleNamespace

from connector_sdk import HttpError, OperationRejected

from .api import items, object_data, paging, positive, request, result
from .repositories import route


def issue_data(reply, number=None):
    data = object_data(reply)
    if (
        not positive(data.get("id"))
        or not positive(data.get("number"))
        or (number is not None and data["number"] != number)
        or "pull_request" in data
    ):
        raise HttpError("github_not_an_issue")
    return data


async def get(ctx, params):
    reply = await request(ctx, "GET", route(params) + f"/issues/{params.issue_number}")
    return result(issue_data(reply, params.issue_number))


async def listing(ctx, params):
    query = params.model_dump(exclude={"owner", "repo", "labels"}, exclude_none=True)
    if params.labels:
        query["labels"] = ",".join(params.labels)
    reply = await request(ctx, "GET", route(params) + "/issues", params=query)
    data = items(reply, params)
    data["items"] = [item for item in data["items"] if "pull_request" not in item]
    return result(data)


async def labels(ctx, params):
    reply = await request(ctx, "GET", route(params) + "/labels", params=paging(params))
    return result(items(reply, params))


async def check_labels(ctx, params):
    if params.labels is None or not params.labels:
        return
    found, page_number, seen = set(), 1, set()
    for _ in range(20):
        reply = await request(
            ctx, "GET", route(params) + "/labels", params={"page": page_number, "per_page": 100}
        )
        data = items(reply, SimpleNamespace(page=page_number, per_page=100))
        for item in data["items"]:
            if type(item.get("name")) is not str:
                raise HttpError("github_invalid_labels")
            found.add(item["name"])
        if set(params.labels) <= found:
            return
        page_number = data["next_page"]
        if page_number is None:
            raise OperationRejected()
        if page_number in seen:
            raise HttpError("github_invalid_pagination")
        seen.add(page_number)
    raise OperationRejected()


async def preflight(ctx, params, *, update=False, comment=False):
    try:
        if update or comment:
            await get(ctx, params)
        if not comment:
            await check_labels(ctx, params)
    except (HttpError, ValueError, TimeoutError):
        # Only reads happened here; record mutations have not been dispatched.
        raise OperationRejected() from None


async def create(ctx, params):
    await preflight(ctx, params)
    body = params.model_dump(exclude={"owner", "repo"}, exclude_none=True)
    reply = await request(ctx, "POST", route(params) + "/issues", body=body, expected=201)
    data = issue_data(reply)
    # GitHub may silently ignore labels when the user lacks sufficient rights.
    if params.labels is not None and not labels_match(data, params.labels):
        raise HttpError("github_write_receipt_mismatch")
    return result(data)


def labels_match(data, requested):
    labels = data.get("labels")
    return (
        type(labels) is list
        and all(type(x) is dict and type(x.get("name")) is str for x in labels)
        and {x["name"] for x in labels} == set(requested)
    )


async def update(ctx, params):
    await preflight(ctx, params, update=True)
    body = params.model_dump(exclude={"owner", "repo", "issue_number"}, exclude_unset=True)
    reply = await request(ctx, "PATCH", route(params) + f"/issues/{params.issue_number}", body=body)
    data = issue_data(reply, params.issue_number)
    if any(data.get(k) != v for k, v in body.items() if k != "labels"):
        raise HttpError("github_write_receipt_mismatch")
    if "labels" in body and not labels_match(data, body["labels"]):
        raise HttpError("github_write_receipt_mismatch")
    return result(data)


async def comments(ctx, params):
    await get(ctx, params)  # This operation is intentionally Issue-only.
    reply = await request(
        ctx, "GET", route(params) + f"/issues/{params.issue_number}/comments", params=paging(params)
    )
    return result(items(reply, params))


async def comment(ctx, params):
    await preflight(ctx, params, comment=True)
    reply = await request(
        ctx,
        "POST",
        route(params) + f"/issues/{params.issue_number}/comments",
        body={"body": params.body},
        expected=201,
    )
    data = object_data(reply)
    if not positive(data.get("id")) or data.get("body") != params.body:
        raise HttpError("github_invalid_comment")
    return result(data)
