"""Wiki node identifiers and underlying resource identifiers stay distinct."""

from connector_sdk import HttpError
from pydantic import TypeAdapter

from .api import page, paging, request, require, result
from .models import Identifier


async def spaces(ctx, params):
    require(ctx, "wiki.read")
    data = await request(ctx, "GET", "wiki/v2/spaces", params=paging(params))
    return page(data, params.page_size)


async def nodes(ctx, params):
    require(ctx, "wiki.read")
    query = paging(params)
    if params.parent_node_token is not None:
        query["parent_node_token"] = params.parent_node_token
    return page(await request(ctx, "GET", f"wiki/v2/spaces/{params.space_id}/nodes",
                              params=query), params.page_size)


async def node(ctx, params):
    require(ctx, "wiki.read")
    data = await request(ctx, "GET", "wiki/v2/spaces/get_node",
                         params={"token": params.token, "obj_type": "wiki"})
    item = data.get("node")
    if (type(item) is not dict or item.get("node_token") != params.token
            or type(item.get("obj_type")) is not str):
        raise HttpError("feishu_invalid_wiki_node")
    # Validate resource tokens using the same contract as downstream calls.
    TypeAdapter(Identifier).validate_python(item.get("obj_token"), strict=True)
    return result(data)
