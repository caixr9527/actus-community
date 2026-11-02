"""Explicit new-document reads; plain text is never labelled Markdown."""

from connector_sdk import HttpError

from .api import request, require, result


async def document(ctx, params):
    require(ctx, "docs.read")
    data = await request(ctx, "GET", f"docx/v1/documents/{params.document_id}")
    doc = data.get("document")
    if (type(doc) is not dict or doc.get("document_id") != params.document_id
            or type(doc.get("title")) is not str or type(doc.get("revision_id")) is not int):
        raise HttpError("feishu_invalid_document")
    return result(data)


async def content(ctx, params):
    require(ctx, "docs.read")
    data = await request(ctx, "GET", f"docx/v1/documents/{params.document_id}/raw_content")
    if type(data.get("content")) is not str:
        raise HttpError("feishu_invalid_document")
    return result({**data, "document_id": params.document_id, "format": "plain_text"})
