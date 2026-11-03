"""Fixed-origin HTTP, safe business errors and lossless bounded results."""

import json

from connector_sdk import HttpError, OperationRejected

from .models import Result

ORIGIN = "https://open.feishu.cn/"
SCOPES = ("offline_access", "docx:document:readonly", "wiki:wiki:readonly", "bitable:app")
CAPABILITIES = {
    "docs.read": {"docx:document:readonly", "docx:document"},
    "wiki.read": {"wiki:wiki:readonly", "wiki:wiki"},
    "bitable.read": {"bitable:app:readonly", "bitable:app"},
    "bitable.write": {"bitable:app"},
}


def decode(content):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError
            result[key] = value
        return result

    def invalid(_):
        raise ValueError

    try:
        if len(content) > 1024 * 1024:
            raise ValueError
        value = json.loads(content, object_pairs_hook=pairs, parse_constant=invalid)
        if type(value) is not dict:
            raise ValueError
        return value
    except (ValueError, UnicodeError, RecursionError):
        raise HttpError("feishu_invalid_response") from None


def capabilities(scope):
    granted = set((scope or "").split())
    return {key: bool(granted & accepted) for key, accepted in CAPABILITIES.items()}


def require(ctx, capability):
    # Refresh can narrow scopes; never rely on the initial identity snapshot alone.
    if not capabilities(ctx.credential().scope)[capability]:
        raise OperationRejected()


async def request(ctx, method, route, *, params=None, body=None, diagnostic=None):
    async def consume(response):
        if diagnostic is not None:
            diagnostic("observed", http_status=response.status_code)
        if response.status_code == 429:
            raise HttpError("feishu_rate_limited")
        if response.status_code in (401, 403):
            raise HttpError("feishu_access_denied")
        if response.status_code != 200:
            raise HttpError("feishu_http_failed")
        payload = decode(await response.read())
        code = payload.get("code")
        if diagnostic is not None:
            diagnostic("observed", http_status=response.status_code, provider_code=code)
        if type(code) is not int:
            raise HttpError("feishu_invalid_response")
        if code != 0:
            if code == 1254290:
                raise HttpError("feishu_rate_limited")
            if code in (1254302, 1254304):
                raise HttpError("feishu_access_denied")
            if code in (1254040, 1254041, 1254043, 1254044):
                raise HttpError("feishu_resource_not_found")
            # Raw vendor messages may contain business data or credentials.
            raise HttpError("feishu_business_failed")
        data = payload.get("data")
        if type(data) is not dict:
            raise HttpError("feishu_invalid_response")
        return data

    query = {key: str(value) for key, value in params.items()} if params is not None else None
    try:
        return await ctx.http("api").request(method, "open-apis/" + route,
                                             params=query, json=body, consume=consume)
    except HttpError as error:
        # SDK b9 returns fixed public operation errors. Keep safe categories in host logs.
        ctx.logger.warning(error.code if error.code.startswith("feishu_") else "feishu_http_failed")
        raise


def result(data):
    return Result(data=data)


def page(data, page_size):
    items, more, token = (data.get(k) for k in ("items", "has_more", "page_token"))
    if (type(items) is not list or len(items) > page_size
            or any(type(item) is not dict for item in items) or type(more) is not bool
            or (token is not None and (type(token) is not str or len(token) > 4096))
            or (more and not token)):
        raise HttpError("feishu_invalid_page")
    return result(data)


def paging(params):
    return params.model_dump(include={"page_size", "page_token"}, exclude_none=True)
