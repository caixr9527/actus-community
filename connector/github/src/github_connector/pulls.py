"""Read-only PR metadata and explicitly partial patch coverage."""

from connector_sdk import HttpError

from .api import items, object_data, paging, positive, request, result
from .repositories import route


async def listing(ctx, params):
    query = params.model_dump(exclude={"owner", "repo"}, exclude_none=True)
    return result(items(await request(ctx, "GET", route(params) + "/pulls", params=query), params))


def snapshot(data, number):
    try:
        head, base = data["head"]["sha"], data["base"]["sha"]
        if (
            not positive(data.get("number"))
            or data["number"] != number
            or not positive(data["id"])
            or type(data["changed_files"]) is not int
            or data["changed_files"] < 0
            or any(
                type(sha) is not str
                or len(sha) != 40
                or any(c not in "0123456789abcdef" for c in sha)
                for sha in (head, base)
            )
        ):
            raise ValueError
        return head, base, data["changed_files"]
    except (KeyError, TypeError, ValueError):
        raise HttpError("github_invalid_pull_request") from None


async def metadata(ctx, params):
    data = object_data(await request(ctx, "GET", route(params) + f"/pulls/{params.pull_number}"))
    snapshot(data, params.pull_number)
    return data


async def get(ctx, params):
    return result(await metadata(ctx, params))


async def files(ctx, params):
    before = snapshot(await metadata(ctx, params), params.pull_number)
    reply = await request(
        ctx, "GET", route(params) + f"/pulls/{params.pull_number}/files", params=paging(params)
    )
    data = items(reply, params)
    after = snapshot(await metadata(ctx, params), params.pull_number)
    if before != after:
        raise HttpError("github_pull_request_changed")
    for item in data["items"]:
        if type(item.get("filename")) is not str or (
            "patch" in item and type(item["patch"]) is not str
        ):
            raise HttpError("github_invalid_file")
    if len({item["filename"] for item in data["items"]}) != len(data["items"]):
        raise HttpError("github_duplicate_file")
    data["coverage"] = {
        "head_sha": before[0],
        "base_sha": before[1],
        "changed_files": before[2],
        "api_file_limit": 3000,
        "exceeds_api_limit": before[2] > 3000,
        "missing_patch_count": sum("patch" not in item for item in data["items"]),
        "file_list_complete": (
            params.page == 1
            and not data["has_more"]
            and len(data["items"]) == before[2]
            and before[2] <= 3000
        ),
        "patches_are_partial": True,
    }
    return result(data)
