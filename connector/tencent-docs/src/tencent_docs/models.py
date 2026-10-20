from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

type JsonValue = str | int | float | bool | None | list[JsonValue] | dict[str, JsonValue]


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)


class Result(BaseModel):
    """Preserve vendor JSON, missing fields and opaque protobuf data."""

    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)
    data: dict[str, JsonValue]


class ListFiles(Input):
    page: int = Field(default=1, ge=1, le=10000)
    page_size: int = Field(default=20, ge=1, le=20)
    sort_by: Literal["recent_view", "recent_edit", "name"] = "recent_view"


class SearchFiles(Input):
    keyword: str = Field(min_length=1, max_length=512)


class ListSpaces(Input):
    page: int = Field(default=0, ge=0, le=10000)
    ownership: Literal["all", "owned", "joined"] = "all"
    sort_by: Literal["recent_view", "recent_edit", "created"] = "recent_view"
    descending: bool = True


class ListSpaceNodes(Input):
    space_id: str = Field(min_length=1, max_length=512)
    parent_id: str = Field(default="", max_length=512)
    page: int = Field(default=0, ge=0, le=10000)


class ReadDocument(Input):
    file_id: str = Field(min_length=1, max_length=512)


class CreateDocument(Input):
    title: str = Field(min_length=1, max_length=255)
    markdown: str = Field(min_length=1, max_length=32768)
