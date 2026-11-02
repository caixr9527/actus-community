"""A narrow, explicit personal meeting interface; no arbitrary MCP calls."""

import re
from datetime import UTC, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Identifier = Annotated[str, Field(min_length=1, max_length=20, pattern=r"^[1-9][0-9]*$")]
Title = Annotated[str, Field(min_length=1, max_length=128, pattern=r"\S")]
Cursor = Annotated[str, Field(min_length=1, max_length=4096)]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True)


def timestamp(value):
    if (
        type(value) is not str
        or len(value) > 32
        or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)", value
        )
        or value.endswith("-00:00")
    ):
        raise ValueError("invalid_meeting_time")
    try:
        elapsed = datetime.fromisoformat(value).astimezone(UTC) - datetime(1970, 1, 1, tzinfo=UTC)
        seconds = elapsed.days * 86400 + elapsed.seconds
        if not 0 < seconds < 2**53:
            raise ValueError
        return seconds
    except (ValueError, OverflowError):
        raise ValueError("invalid_meeting_time") from None


def text(value):
    if any(ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF for c in value):
        raise ValueError("invalid_text")
    return value


class Page(Model):
    page_token: Cursor | None = None

    @field_validator("page_token")
    @classmethod
    def cursor(cls, value):
        return text(value) if value is not None else value

    @model_validator(mode="after")
    def no_null(self):
        if any(getattr(self, key) is None for key in self.model_fields_set):
            raise ValueError("explicit_null_not_supported")
        return self


class EndedPage(Page):
    start_time: str
    end_time: str
    page_size: int = Field(default=20, ge=1, le=20)

    @model_validator(mode="after")
    def window(self):
        start, end = timestamp(self.start_time), timestamp(self.end_time)
        if not 0 < end - start <= 31 * 86400:
            raise ValueError("invalid_history_window")
        return self


class Meeting(Model):
    meeting_id: Identifier

    @field_validator("meeting_id")
    @classmethod
    def uint64(cls, value):
        if int(value) >= 2**64:
            raise ValueError("invalid_meeting_id")
        return value


class MeetingCode(Model):
    meeting_code: str = Field(pattern=r"^[0-9]{9}$")


class Create(Model):
    subject: Title
    start_time: str
    end_time: str

    @field_validator("subject")
    @classmethod
    def title(cls, value):
        return text(value)

    @model_validator(mode="after")
    def times(self):
        if timestamp(self.end_time) <= timestamp(self.start_time):
            raise ValueError("invalid_meeting_window")
        return self


class Update(Meeting):
    subject: Title | None = None
    start_time: str | None = None
    end_time: str | None = None

    @field_validator("subject")
    @classmethod
    def title(cls, value):
        return text(value) if value is not None else value

    @model_validator(mode="after")
    def changes(self):
        fields = self.model_fields_set - {"meeting_id"}
        if not fields or any(getattr(self, key) is None for key in fields):
            raise ValueError("invalid_meeting_update")
        if (self.start_time is None) != (self.end_time is None):
            raise ValueError("meeting_times_must_be_paired")
        for key in ("start_time", "end_time"):
            if key in fields:
                timestamp(getattr(self, key))
        if self.start_time is not None and self.end_time is not None:
            if timestamp(self.end_time) <= timestamp(self.start_time):
                raise ValueError("invalid_meeting_window")
        return self


class MeetingView(Model):
    meeting_id: Identifier
    subject: str
    meeting_type: int
    scheduled: bool | None = None
    meeting_code: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    status: str | None = None
    join_url: str | None = None


class MeetingPage(Model):
    meetings: list[MeetingView]
    has_more: bool
    next_page_token: str | None = None


class Receipt(Model):
    meeting_id: Identifier
    accepted: bool
