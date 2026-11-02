"""Explicit bounded inputs; omission and replacement have distinct semantics."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator, model_validator

type JsonValue = str | int | float | bool | None | list[JsonValue] | dict[str, JsonValue]
Positive = Annotated[int, Field(gt=0, lt=2**53)]
Label = Annotated[str, Field(min_length=1, max_length=100, pattern=r"^[^\x00-\x1f\x7f]+$")]
Text = Annotated[str, Field(max_length=65536)]
Title = Annotated[str, Field(min_length=1, max_length=256, pattern=r"\S")]


class Model(BaseModel):
    model_config = ConfigDict(
        extra="forbid", strict=True, hide_input_in_errors=True, allow_inf_nan=False
    )


class Settings(Model):
    client_id: str = Field(min_length=1, max_length=255, pattern=r"^[A-Za-z0-9_.-]+$")
    client_secret: SecretStr = Field(min_length=1, max_length=4096)


class Result(Model):
    data: dict[str, JsonValue]


class Page(Model):
    page: int = Field(default=1, ge=1, le=1000000)
    per_page: int = Field(default=30, ge=1, le=100)


class InstallationPage(Page):
    installation_id: Positive


class Repository(Model):
    owner: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9][A-Za-z0-9-]*$")
    repo: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.-]+$")

    @field_validator("repo")
    @classmethod
    def name(cls, value):
        if value in {".", ".."}:
            raise ValueError("invalid_repository")
        return value


class RepositoryPage(Repository, Page):
    pass


class Issue(Repository):
    issue_number: Positive


class IssuePage(Issue, Page):
    pass


class ListIssues(RepositoryPage):
    state: Literal["open", "closed", "all"] = "open"
    labels: list[Label] | None = Field(default=None, min_length=1, max_length=50)
    sort: Literal["created", "updated", "comments"] = "created"
    direction: Literal["asc", "desc"] = "desc"
    since: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

    @field_validator("labels")
    @classmethod
    def query_labels(cls, value):
        if value and any("," in label for label in value):
            raise ValueError("comma_in_label_query_not_supported")
        return value

    @field_validator("since")
    @classmethod
    def timestamp(cls, value):
        if value is not None:
            from datetime import datetime

            datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        return value


class CreateIssue(Repository):
    title: Title
    body: Text = ""
    labels: list[Label] | None = Field(default=None, max_length=50)

    @model_validator(mode="after")
    def explicit_null(self):
        if any(getattr(self, key) is None for key in self.model_fields_set):
            raise ValueError("explicit_null_not_supported")
        if self.labels is not None and len(set(self.labels)) != len(self.labels):
            raise ValueError("duplicate_labels")
        return self


class UpdateIssue(Issue):
    title: Title | None = None
    body: Text | None = None
    labels: list[Label] | None = Field(
        default=None, max_length=50, description="完整替换标签集合；空数组清空，省略不修改"
    )
    state: Literal["open", "closed"] | None = None
    state_reason: Literal["completed", "not_planned", "reopened"] | None = None

    @model_validator(mode="after")
    def update(self):
        changes = self.model_fields_set - {"owner", "repo", "issue_number"}
        if not changes or any(getattr(self, key) is None for key in changes):
            raise ValueError("invalid_issue_update")
        if self.labels is not None and len(set(self.labels)) != len(self.labels):
            raise ValueError("duplicate_labels")
        if self.state_reason is not None:
            expected = "open" if self.state_reason == "reopened" else "closed"
            if self.state != expected:
                raise ValueError("state_reason_requires_matching_state")
        return self


class CreateComment(Issue):
    body: Annotated[str, Field(min_length=1, max_length=65536, pattern=r"\S")]


class Pull(Repository):
    pull_number: Positive


class PullFiles(Pull, Page):
    pass


class ListPulls(RepositoryPage):
    state: Literal["open", "closed", "all"] = "open"
    sort: Literal["created", "updated", "popularity", "long-running"] = "created"
    direction: Literal["asc", "desc"] = "desc"
    base: str | None = Field(default=None, min_length=1, max_length=255)
    head: str | None = Field(default=None, min_length=1, max_length=255)
