"""Strict inputs and small projected results; IDs are lossless decimal strings."""

import re
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ID = Annotated[str, Field(min_length=1, max_length=19, pattern=r"^[1-9][0-9]*$")]
Title = Annotated[str, Field(min_length=1, max_length=256, pattern=r"\S")]
BODY_LIMIT = 256 * 1024


def identifier(value):
    if type(value) is not str or not re.fullmatch(r"[1-9][0-9]{0,18}", value):
        raise ValueError("invalid_id")
    if int(value) >= 2**63:
        raise ValueError("invalid_id")
    return value


def text(value, *, multiline=False):
    if any(
        (ord(c) < 32 and not (multiline and c in "\n\r\t"))
        or ord(c) == 127
        or 0xD800 <= ord(c) <= 0xDFFF
        for c in value
    ):
        raise ValueError("invalid_text")
    return value


def timestamp(value):
    if (
        type(value) is not str
        or not re.fullmatch(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
            r"(?:\.[0-9]{1,6})?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])",
            value,
        )
        or value.endswith("-00:00")
    ):
        raise ValueError("invalid_timestamp")
    try:
        datetime.fromisoformat(value)
    except ValueError:
        raise ValueError("invalid_timestamp") from None
    return value


class Model(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True)


class Input(Model):
    @model_validator(mode="after")
    def fields(self):
        for key in self.model_fields_set:
            value = getattr(self, key)
            if value is None:
                raise ValueError("explicit_null_not_supported")
            if type(value) is str:
                text(value, multiline=key == "body")
                if key.endswith("_id"):
                    identifier(value)
        return self


class Empty(Input):
    pass


class Groups(Input):
    offset: int = Field(default=0, ge=0, le=1_000_000)


class Page(Groups):
    limit: int = Field(default=20, ge=1, le=100)


class Repositories(Page):
    owner_kind: Literal["user", "group"] = "user"
    group_id: ID | None = None

    @model_validator(mode="after")
    def owner(self):
        if (self.owner_kind == "group") != (self.group_id is not None):
            raise ValueError("group_id_required_only_for_group")
        return self


class Repository(Input):
    repository_id: ID


class Documents(Page):
    repository_id: ID


class Document(Repository):
    document_id: ID


class Search(Input):
    query: str = Field(min_length=1, max_length=200, pattern=r"\S")
    type: Literal["doc", "repo"] = "doc"
    scope: str | None = Field(default=None, min_length=1, max_length=400)
    page: int = Field(default=1, ge=1, le=100)

    @field_validator("scope")
    @classmethod
    def scope_path(cls, value):
        if value is not None and not re.fullmatch(r"[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)?", value):
            raise ValueError("invalid_search_scope")
        return value

    @model_validator(mode="after")
    def scope_kind(self):
        if self.type == "repo" and self.scope is not None and "/" in self.scope:
            raise ValueError("repository_search_requires_owner_scope")
        return self


class Create(Repository):
    title: Title
    body: str = Field(min_length=1, max_length=BODY_LIMIT)

    @field_validator("body")
    @classmethod
    def body_size(cls, value):
        text(value, multiline=True)
        if len(value.encode("utf-8")) > BODY_LIMIT:
            raise ValueError("body_too_large")
        return value


class Update(Document):
    expected_updated_at: str = Field(max_length=32)
    title: Title | None = None
    body: str | None = Field(default=None, min_length=1, max_length=BODY_LIMIT)

    @model_validator(mode="after")
    def change(self):
        timestamp(self.expected_updated_at)
        if self.title is None and self.body is None:
            raise ValueError("empty_update")
        if self.body is not None:
            Create.body_size(self.body)
        return self


class UserView(Model):
    id: str
    login: str
    name: str | None = None


class GroupView(UserView):
    pass


class RepositoryView(Model):
    id: str
    name: str
    slug: str
    type: str
    public: int | None = None
    namespace: str | None = None
    updated_at: str | None = None


class DocumentView(Model):
    id: str
    repository_id: str
    title: str
    slug: str
    type: str
    public: int | None = None
    updated_at: str | None = None


class DocumentDetail(DocumentView):
    format: str
    body: str
    status: str | None = None


class OffsetResult(Model):
    offset: int
    limit: int
    total: int | None = None
    has_more: bool | None = None
    next_offset: int | None = None
    offset_limit_reached: bool


class GroupPage(OffsetResult):
    items: list[GroupView]


class RepositoryPage(OffsetResult):
    items: list[RepositoryView]


class DocumentPage(OffsetResult):
    items: list[DocumentView]


class SearchItem(Model):
    id: str
    type: Literal["doc", "repo"]
    title: str
    summary: str | None = None
    url: str | None = None
    repository_id: str | None = None


class SearchPage(Model):
    items: list[SearchItem]
    page: int
    page_size: int
    total: int | None = None
    has_more: bool | None = None
    next_page: int | None = None
    page_limit_reached: bool


class WriteReceipt(Model):
    document: DocumentView
    accepted: bool
    content_verified: bool
