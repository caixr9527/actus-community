"""Bounded, explicit operation inputs. Resource tokens never become arbitrary URLs."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator, model_validator

type JsonValue = str | int | float | bool | None | list[JsonValue] | dict[str, JsonValue]
Identifier = Annotated[str, Field(pattern=r"^[A-Za-z0-9_-]{1,256}$")]
Name = Annotated[str, Field(min_length=1, max_length=256, pattern=r"^[^\x00-\x1f\x7f]+$")]
Cursor = Annotated[str, Field(min_length=1, max_length=4096)]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True,
                              allow_inf_nan=False)


class Settings(Model):
    app_id: str = Field(pattern=r"^cli_[A-Za-z0-9_-]{1,200}$", title="飞书 App ID")
    app_secret: SecretStr = Field(min_length=1, max_length=4096, title="飞书 App Secret")

    @field_validator("app_secret")
    @classmethod
    def secret(cls, value):
        if not value.get_secret_value().strip() or any(
            ord(c) <= 32 or ord(c) == 127 for c in value.get_secret_value()
        ):
            raise ValueError("invalid_app_secret")
        return value


class Empty(Model):
    pass


class Result(Model):
    data: dict[str, JsonValue]


class Document(Model):
    document_id: Identifier = Field(description="新版文档 document_id；知识库链接先解析节点")


class Page(Model):
    page_size: int = Field(default=20, ge=1, le=50)
    page_token: Cursor | None = None


class WikiNodes(Page):
    space_id: Identifier
    parent_node_token: Identifier | None = None


class WikiNode(Model):
    token: Identifier = Field(description="知识库链接中的节点 token，并非实际文档 ID")


class Tables(Page):
    app_token: Identifier = Field(description="多维表格资源标识，不是 OAuth 凭据")


class Table(Model):
    app_token: Identifier
    table_id: Identifier


class TablePage(Table, Page):
    pass


class Record(Table):
    record_id: Identifier


class Sort(Model):
    field_name: Name
    desc: bool = False


class Condition(Model):
    field_name: Name
    operator: Literal["is", "isNot", "contains", "doesNotContain", "isEmpty", "isNotEmpty",
                      "isGreater", "isGreaterEqual", "isLess", "isLessEqual"]
    value: list[Annotated[str, Field(max_length=4096)]] = Field(
        default_factory=list, max_length=100)

    @model_validator(mode="after")
    def values(self):
        if (self.operator in {"isEmpty", "isNotEmpty"}) != (len(self.value) == 0):
            raise ValueError("invalid_filter_values")
        return self


class Filter(Model):
    conjunction: Literal["and", "or"] = "and"
    conditions: list[Condition] = Field(min_length=1, max_length=50)


class SearchRecords(TablePage):
    view_id: Identifier | None = None
    field_names: list[Name] | None = Field(default=None, min_length=1, max_length=100)
    sort: list[Sort] | None = Field(default=None, min_length=1, max_length=20)
    filter: Filter | None = None

    @model_validator(mode="after")
    def view_filter(self):
        # Feishu ignores the view's filter when explicit sort/filter is supplied.
        # Reject this ambiguous combination instead of silently broadening the query.
        if self.view_id is not None and (self.filter is not None or self.sort is not None):
            raise ValueError("view_with_filter_or_sort_not_supported")
        return self


class CreateRecord(Table):
    fields: dict[Name, JsonValue] = Field(min_length=1, max_length=100,
                                        description="按字段名赋值；写前核对字段类型及已有选项")


class UpdateRecord(CreateRecord):
    record_id: Identifier
