"""Discovery is scoped by the current GitHub App user token."""

from .api import items, paging, request, result


async def list_installations(ctx, params):
    reply = await request(ctx, "GET", "user/installations", params=paging(params))
    return result(items(reply, params, "installations"))
