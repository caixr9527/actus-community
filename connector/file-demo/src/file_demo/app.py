"""A fixed service supplies metadata and bytes; the platform owns artifact registration."""

from connector_sdk import (
    ApiKeyAuth,
    AppSpec,
    AuthorizationRejected,
    AuthUI,
    ConfigRef,
    Connector,
    ExternalIdentity,
    FileInput,
    FileOutput,
    HttpService,
    OperationRejected,
    VerifiedConnection,
    operation,
)
from connector_sdk.auth import Bearer
from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_FILE_BYTES = 100 * 1024 * 1024


def text(value):
    if not value.strip() or any(
        ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF for c in value
    ):
        raise ValueError("invalid_file_service_identifier")
    return value


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    api_base_url: str = Field(description="服务管理员配置的固定文件 API 地址")


class Profile(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True)
    account_id: str = Field(min_length=1, max_length=255)
    tenant_id: str | None = Field(default=None, min_length=1, max_length=255)
    display_name: str | None = Field(default=None, max_length=255)
    permissions: list[str] | None = Field(default=None, max_length=64)

    @field_validator("account_id", "tenant_id")
    @classmethod
    def identifier(cls, value):
        return None if value is None else text(value)


class Auth(ApiKeyAuth):
    request_auth = Bearer("api_key")
    ui = AuthUI(
        title="连接通用文件示例", description="输入固定文件服务的 Token，验证账号后保存连接。"
    )

    async def verify(self, ctx) -> VerifiedConnection:
        async def consume(response):
            if response.status_code in (401, 403):
                raise AuthorizationRejected()
            if response.status_code != 200:
                raise ValueError("file_service_unavailable")
            return Profile.model_validate_json(await response.read(), strict=True)

        profile = await ctx.http("api").request("GET", "me", consume=consume)
        return VerifiedConnection(
            identity=ExternalIdentity(
                account_id=profile.account_id,
                tenant_id=profile.tenant_id,
                display_name=profile.display_name,
            ),
            capabilities={
                name: name in profile.permissions for name in ("files.read", "files.write")
            }
            if profile.permissions is not None
            else None,
        )


class DownloadFile(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True)
    file_id: str = Field(min_length=1, max_length=255, description="固定服务中的原样文件标识")

    @field_validator("file_id")
    @classmethod
    def identifier(cls, value):
        return text(value)


class Metadata(DownloadFile):
    file_name: str = Field(min_length=1, max_length=255)
    mime_type: str | None = Field(default=None, min_length=1, max_length=255)
    size_bytes: int | None = Field(default=None, ge=0, lt=2**53)


class UploadParams(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True)


class UploadResult(Metadata):
    size_bytes: int = Field(ge=0, lt=2**53)

    @field_validator("file_name")
    @classmethod
    def name(cls, value):
        text(value)
        if value in {".", ".."} or "/" in value or "\\" in value:
            raise ValueError("file_service_response_invalid")
        return value

    @field_validator("mime_type")
    @classmethod
    def mime(cls, value):
        return text(value) if value is not None else None


class App(Connector):
    spec = AppSpec(
        id="file-demo", name="通用文件示例", description="通过固定服务上传和下载单个文件"
    )
    config_model = Settings
    auth = Auth()
    services = {"api": HttpService(ConfigRef("api_base_url"), auth="connection")}

    @operation(
        name="upload_file",
        description="将一个平台文件上传为固定服务中的新文件。",
        effects="write",
        transport="file_input",
        max_file_bytes=MAX_FILE_BYTES,
        required_capabilities=("files.write",),
    )
    async def upload_file(self, ctx, params: UploadParams, file: FileInput) -> UploadResult:
        async def consume(response):
            # This service guarantees these statuses mean no file was created.
            if response.status_code in (400, 401, 403, 413):
                raise OperationRejected()
            if response.status_code != 201:
                raise ValueError("file_service_response_invalid")
            result = UploadResult.model_validate_json(await response.read(), strict=True)
            if (
                result.file_name != file.file_name
                or result.mime_type != file.mime_type
                or (file.size_bytes is not None and result.size_bytes != file.size_bytes)
            ):
                raise ValueError("file_service_response_invalid")
            return result

        metadata = {"file_name": file.file_name}
        if file.mime_type is not None:
            metadata["mime_type"] = file.mime_type
        return await ctx.http("api").request_file(
            "POST",
            "files",
            file=file,
            max_file_bytes=MAX_FILE_BYTES,
            params=metadata,
            consume=consume,
        )

    @operation(
        name="download_file",
        description="按文件标识下载固定服务中的单个文件。",
        effects="read",
        transport="file_output",
        max_file_bytes=MAX_FILE_BYTES,
        required_capabilities=("files.read",),
    )
    async def download_file(self, ctx, params: DownloadFile) -> FileOutput:
        metadata = Metadata.model_validate(
            await ctx.http("api").get_json(
                "files/metadata",
                params={"file_id": params.file_id},
            )
        )
        if metadata.file_id != params.file_id:
            raise ValueError("file_service_response_invalid")
        return await ctx.http("api").get_file(
            "files/content",
            params={"file_id": params.file_id},
            file_name=metadata.file_name,
            mime_type=metadata.mime_type,
            size_bytes=metadata.size_bytes,
            external_resource_id=metadata.file_id,
            max_file_bytes=MAX_FILE_BYTES,
        )
