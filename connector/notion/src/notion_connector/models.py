"""Stable application arguments; SDK validates them before any vendor request."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

type JsonValue = str | int | float | bool | None | list[JsonValue] | dict[str, JsonValue]

Identifier = Annotated[str, Field(min_length=1, max_length=2048)]
Cursor = Annotated[str, Field(min_length=1, max_length=200)]


class Model(BaseModel):
    model_config = ConfigDict(
        extra="forbid", strict=True, hide_input_in_errors=True, allow_inf_nan=False
    )


class Settings(Model):
    pass


class Result(Model):
    data: dict[str, JsonValue]


class Search(Model):
    query: str = Field(min_length=1, max_length=1000)


class Fetch(Model):
    id: Identifier


class Users(Model):
    query: str | None = Field(default=None, min_length=1, max_length=100)
    user_id: str | None = Field(default=None, min_length=1, max_length=100)
    start_cursor: Cursor | None = None
    page_size: int | None = Field(default=None, ge=1, le=100)


class Teams(Model):
    query: str | None = Field(default=None, min_length=1, max_length=100)


class Comments(Model):
    page_id: Identifier
    discussion_id: Identifier | None = None
    include_all_blocks: bool | None = None
    include_resolved: bool | None = None


class View(Model):
    view_url: Identifier
    start_cursor: Cursor | None = None
    page_size: int | None = Field(default=None, ge=1, le=100)
    include_archived: bool | None = None


class Task(Model):
    task_id: str = Field(min_length=1, max_length=255)


class CreatePage(Model):
    parent_id: Identifier
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(default="", max_length=32768)
    allow_async: bool | None = None


class UpdatePage(Model):
    page_id: Identifier
    content: str = Field(max_length=32768)
    allow_async: bool | None = None


class CreateComment(Model):
    page_id: Identifier
    markdown: str = Field(min_length=1, max_length=4096)
    discussion_id: Identifier | None = None
    selection_with_ellipsis: str | None = Field(default=None, min_length=3, max_length=1000)


class Move(Model):
    page_or_database_ids: list[Identifier] = Field(min_length=1, max_length=100)
    parent_type: Literal["page_id", "database_id", "data_source_id", "workspace"]
    parent_id: Identifier | None = None

    @model_validator(mode="after")
    def parent(self):
        if (self.parent_type == "workspace") != (self.parent_id is None):
            raise ValueError("invalid_parent")
        return self


class Duplicate(Model):
    page_id: Identifier
