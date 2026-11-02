"""Repository discovery and metadata; no repository mutation."""

from connector_sdk import HttpError

from .api import items, object_data, paging, positive, request, result


def route(params):
    return f"repos/{params.owner}/{params.repo}"


async def list_repositories(ctx, params):
    reply = await request(
        ctx,
        "GET",
        f"user/installations/{params.installation_id}/repositories",
        params=paging(params),
    )
    return result(items(reply, params, "repositories"))


async def get_repository(ctx, params):
    data = object_data(await request(ctx, "GET", route(params)))
    if not positive(data.get("id")) or type(data.get("full_name")) is not str:
        raise HttpError("github_invalid_repository")
    return result(data)
