"""Bounded inputs; omitted fields never overwrite existing todo values."""

import re
from datetime import UTC, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator, model_validator

Title = Annotated[str, Field(min_length=1, max_length=50, pattern=r"\S")]
Description = Annotated[str, Field(max_length=1000)]
TaskId = Annotated[str, Field(min_length=1, max_length=256, pattern=r"^[A-Za-z0-9_-]+$")]


def milliseconds(value):
    elapsed = datetime.fromisoformat(value).astimezone(UTC) - datetime(1970, 1, 1, tzinfo=UTC)
    return (elapsed.days * 86400 + elapsed.seconds) * 1000 + elapsed.microseconds // 1000


class Model(BaseModel):
    model_config = ConfigDict(
        extra="forbid", strict=True, hide_input_in_errors=True, allow_inf_nan=False
    )


class Settings(Model):
    client_id: str = Field(min_length=1, max_length=255, pattern=r"^[A-Za-z0-9_.-]+$")
    client_secret: SecretStr = Field(min_length=1, max_length=4096)


class Empty(Model):
    pass


class Profile(Model):
    union_id: str
    display_name: str | None = None


class Created(Model):
    task_id: TaskId
    created_time_ms: int = Field(gt=0, lt=2**53)


class Receipt(Model):
    task_id: TaskId
    success: bool


class ExecutorReceipt(Receipt):
    executor_done: bool


class Changes(Model):
    subject: Title | None = None
    description: Description | None = None
    due_at: str | None = Field(
        default=None,
        max_length=40,
        description="含时区的 RFC3339 截止时间，例如 2026-11-03T18:00:00+08:00；省略不修改",
    )

    @field_validator("subject", "description")
    @classmethod
    def text(cls, value, info):
        if value is not None and any(
            0xD800 <= ord(c) <= 0xDFFF
            or ord(c) == 127
            or (ord(c) < 32 and (info.field_name == "subject" or c not in "\n\r\t"))
            for c in value
        ):
            raise ValueError("invalid_todo_text")
        return value

    @field_validator("due_at")
    @classmethod
    def timestamp(cls, value):
        if value is None:
            return value
        # Require seconds, an explicit zone and millisecond-or-coarser precision.
        if not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?"
            r"(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)",
            value,
        ) or value.endswith("-00:00"):
            raise ValueError("invalid_due_at")
        try:
            if not 0 < milliseconds(value) < 2**53:
                raise ValueError
        except (ValueError, OverflowError, OSError):
            raise ValueError("invalid_due_at") from None
        return value

    @model_validator(mode="after")
    def no_null(self):
        if any(getattr(self, key) is None for key in self.model_fields_set):
            raise ValueError("explicit_null_not_supported")
        return self


class CreateTodo(Changes):
    subject: Title


class Task(Model):
    task_id: TaskId


class UpdateTodo(Changes, Task):
    @model_validator(mode="after")
    def nonempty(self):
        if not self.model_fields_set - {"task_id"}:
            raise ValueError("empty_todo_update")
        return self


class ExecutorStatus(Task):
    done: bool
