"""Fixed-origin, bounded JSON HTTP with sanitized errors and no retry policy."""

import json
import math

from connector_sdk import HttpError

ORIGIN = "https://www.yuque.com/api/v2/"
RESPONSE_LIMIT = 2 * 1024 * 1024


def failure(code):
    raise HttpError("yuque_" + code)


def decode(content):
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise ValueError
            result[key] = value
        return result

    def invalid(_):
        raise ValueError

    def number(value):
        parsed = float(value)
        if not math.isfinite(parsed):
            raise ValueError
        return parsed

    try:
        if len(content) > RESPONSE_LIMIT:
            raise ValueError
        result = json.loads(
            content, object_pairs_hook=pairs, parse_constant=invalid, parse_float=number
        )
        if type(result) is not dict:
            raise ValueError
        return result
    except (ValueError, UnicodeError, RecursionError):
        failure("invalid_json")


async def request(ctx, method, path, *, params=None, body=None):
    async def consume(response):
        errors = {
            401: "unauthorized",
            403: "forbidden",
            404: "not_found",
            429: "rate_limited",
            400: "invalid_request",
            422: "invalid_request",
        }
        if response.status_code != 200:
            failure(errors.get(response.status_code, "http_failed"))
        if (
            response.headers.get("content-type", "").split(";")[0].strip().lower()
            != "application/json"
        ):
            failure("unsupported_response_type")
        result = decode(await response.read())
        if any(key in result for key in ("error", "errors", "errcode")):
            failure("business_failed")
        if "status" in result and (type(result["status"]) is not int or result["status"] != 200):
            failure("business_failed")
        if "data" not in result:
            failure("invalid_response")
        for value in (result, result["data"]):
            if type(value) is dict:
                if any(key in value for key in ("error", "errors", "errcode")):
                    failure("business_failed")
                if "success" in value and value["success"] is not True:
                    failure("business_failed")
                if "code" in value and (type(value["code"]) is not int or value["code"] != 0):
                    failure("business_failed")
        return result

    try:
        return await ctx.http("yuque").request(
            method,
            path,
            params={key: str(value) for key, value in (params or {}).items()},
            headers={"Accept": "application/json", "User-Agent": "Actus-Yuque/0.1.0"},
            **({"json": body} if body is not None else {}),
            consume=consume,
        )
    except HttpError as error:
        ctx.logger.warning(error.code if error.code.startswith("yuque_") else "yuque_http_failed")
        raise
