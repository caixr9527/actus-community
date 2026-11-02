"""Application inputs and explicit, non-secret vendor result projections."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

MAX_FILE_BYTES = 100 * 1024 * 1024
PART_BYTES = 4 * 1024 * 1024


def text(value: str) -> str:
    if not value.strip() or any(
        ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF for c in value
    ):
        raise ValueError("invalid_netdisk_text")
    return value


def path(value: str) -> str:
    text(value)
    if value == "/":
        return value
    parts = value.removeprefix("/").split("/")
    if "\\" in value or any(p in {"", ".", ".."} for p in parts):
        raise ValueError("invalid_netdisk_path")
    return "/" + "/".join(parts)


def name(value: str) -> str:
    text(value)
    if len(value) > 255 or value in {".", ".."} or any(c in value for c in "/\\"):
        raise ValueError("invalid_netdisk_name")
    return value


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True,
                              allow_inf_nan=False)


class Settings(Model):
    client_id: str = Field(min_length=1, max_length=4096, title="百度应用 AppKey")
    client_secret: SecretStr = Field(min_length=1, max_length=4096, title="百度应用 SecretKey")

    @field_validator("client_id", "client_secret")
    @classmethod
    def valid_material(cls, value):
        text(value.get_secret_value() if isinstance(value, SecretStr) else value)
        return value


class Empty(Model):
    pass


class Directory(Model):
    path: str = Field(default="/", min_length=1, max_length=1024)

    @field_validator("path")
    @classmethod
    def valid_path(cls, value):
        return path(value)


class ListFiles(Directory):
    start: int = Field(default=0, ge=0, le=100000)
    limit: int = Field(default=50, ge=1, le=100)


class Search(Directory):
    query: str = Field(min_length=1, max_length=30)
    page: int = Field(default=1, ge=1, le=1000)
    limit: int = Field(default=50, ge=1, le=100)

    @field_validator("query")
    @classmethod
    def valid_query(cls, value):
        return text(value)


class Semantic(Directory):
    query: str = Field(min_length=1, max_length=512)
    limit: int = Field(default=50, ge=1, le=100)
    category: int | None = Field(default=None, ge=1, le=7)

    @field_validator("query")
    @classmethod
    def valid_query(cls, value):
        return text(value)


class FileID(Model):
    fs_id: str = Field(pattern=r"^[1-9][0-9]{0,31}$")


class NonRoot(Directory):
    path: str = Field(min_length=1, max_length=1024)

    @field_validator("path")
    @classmethod
    def non_root(cls, value):
        if value == "/":
            raise ValueError("netdisk_root_not_allowed")
        return value


class CreateFolder(NonRoot):
    rename_on_conflict: bool = False


class Rename(NonRoot):
    new_name: str = Field(min_length=1, max_length=255)

    @field_validator("new_name")
    @classmethod
    def valid_name(cls, value):
        return name(value)


class CopyMove(Model):
    source_path: str = Field(min_length=1, max_length=1024)
    destination_directory: str = Field(min_length=1, max_length=1024)
    new_name: str = Field(min_length=1, max_length=255)
    conflict_policy: Literal["fail", "newcopy", "overwrite", "skip"] = "fail"

    @field_validator("source_path", "destination_directory")
    @classmethod
    def valid_path(cls, value, info):
        value = path(value)
        if info.field_name == "source_path" and value == "/":
            raise ValueError("netdisk_root_not_allowed")
        return value

    @field_validator("new_name")
    @classmethod
    def valid_name(cls, value):
        return name(value)


class Upload(Model):
    destination_path: str = Field(default="/", min_length=1, max_length=1024)

    @field_validator("destination_path")
    @classmethod
    def valid_path(cls, value):
        return path(value)


class FileRecord(Model):
    fs_id: str = Field(pattern=r"^[1-9][0-9]{0,31}$")
    name: str = Field(min_length=1, max_length=255)
    path: str | None = None
    parent_path: str | None = None
    size_bytes: int | None = Field(default=None, ge=0)
    is_directory: bool | None = None
    category: int | None = Field(default=None, ge=1, le=7)
    modified_at: int | None = Field(default=None, ge=0)
    created_at: int | None = Field(default=None, ge=0)
    md5: str | None = Field(default=None, pattern=r"^[a-fA-F0-9]{32}$")
    content: str | None = None
    ocr: str | None = None

    @field_validator("name")
    @classmethod
    def valid_name(cls, value):
        return name(value)

    @field_validator("path", "parent_path")
    @classmethod
    def valid_path(cls, value):
        return path(value) if value is not None else None


class FileResult(Model):
    file: FileRecord


class ListResult(Model):
    files: list[FileRecord] = Field(max_length=1000)
    start: int
    limit: int
    next_start: int
    has_more: bool


class SearchResult(Model):
    files: list[FileRecord] = Field(max_length=1000)
    page: int
    limit: int
    has_more: bool | None


class SemanticResult(Model):
    files: list[FileRecord] = Field(max_length=1000)
    limit: int
    has_more: bool | None


class Quota(Model):
    total_bytes: int = Field(ge=0)
    used_bytes: int = Field(ge=0)
    free_bytes: int = Field(ge=0)
    expires_within_seven_days: bool | None


class ManagedItem(Model):
    path: str | None = None


class Managed(Model):
    operation: Literal["copy", "move", "rename", "delete"]
    items: list[ManagedItem] = Field(max_length=1)
    task_id: str | None = None


class Uploaded(Model):
    external_resource_id: str | None = None
    file_name: str
    size_bytes: Annotated[int, Field(ge=1, le=MAX_FILE_BYTES)]
    provider_path: str
