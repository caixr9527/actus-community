"""A typed generic adapter using the public SDK only."""

from pathlib import Path
from types import SimpleNamespace

import pytest
from connector_sdk import (
    AuthorizationRejected,
    FileInput,
    FileOutput,
    OperationRejected,
    load_project,
)
from pydantic import ValidationError

from file_demo.app import MAX_FILE_BYTES, App, Auth, DownloadFile, UploadParams


class Context:
    def __init__(self, metadata=None, status=200, permissions=None):
        self.metadata = metadata or {
            "file_id": "原样/标识",
            "file_name": "a.json",
            "mime_type": None,
            "size_bytes": None,
        }
        self.status, self.permissions = status, permissions
        self.calls = []

    def http(self, name):
        assert name == "api"
        owner = self

        class Client:
            async def request(self, method, path, *, consume):
                import json

                async def read():
                    return json.dumps(
                        {"account_id": " a ", "permissions": owner.permissions}
                    ).encode()

                return await consume(SimpleNamespace(status_code=owner.status, read=read))

            async def get_json(self, path, **kwargs):
                owner.calls.append((path, kwargs))
                return owner.metadata

            async def get_file(self, path, **kwargs):
                owner.calls.append((path, kwargs))

                async def content():
                    yield b"raw\x00file"

                return FileOutput(
                    content=content(),
                    **{k: v for k, v in kwargs.items() if k not in {"params", "max_file_bytes"}},
                )

        return Client()


def test_manifest_has_two_generic_file_operations():
    declared = load_project(Path(__file__).resolve().parents[1] / "pyproject.toml")
    assert declared.manifest.id == "file-demo" and declared.manifest.auth.type == "api_key"
    assert set(declared.operations) == {"download_file", "upload_file"}
    op = next(op for op in declared.manifest.operations if op.name == "download_file")
    assert op.transport == "file_output" and op.output_schema is None
    assert op.effects == "read" and op.max_file_bytes == MAX_FILE_BYTES
    assert set(op.input_schema["properties"]) == {"file_id"}
    assert "https://" not in declared.manifest.to_json()
    upload = next(op for op in declared.manifest.operations if op.name == "upload_file")
    assert upload.transport == "file_input" and upload.effects == "write"
    assert upload.max_file_bytes == MAX_FILE_BYTES and upload.output_schema is not None
    assert upload.input_schema.get("properties", {}) == {}


@pytest.mark.parametrize("permissions", [None, [], ["files.read"]])
async def test_identity_and_unknown_permissions_are_preserved(permissions):
    value = await Auth().verify(Context(permissions=permissions))
    assert value.identity.account_id == " a " and value.identity.tenant_id is None
    assert value.capabilities == (
        None
        if permissions is None
        else {name: name in permissions for name in ("files.read", "files.write")}
    )


@pytest.mark.parametrize("status", [401, 403, 429, 500])
async def test_invalid_authorization_never_succeeds(status):
    with pytest.raises(AuthorizationRejected if status in (401, 403) else ValueError):
        await Auth().verify(Context(status=status))


@pytest.mark.parametrize(
    "values",
    [
        {},
        {"file_id": " "},
        {"file_id": "a\nb"},
        {"file_id": "\ud800"},
        {"file_id": 1},
        {"file_id": "x" * 256},
        {"file_id": "a", "url": "https://other.test"},
    ],
)
def test_parameters_are_strict(values):
    with pytest.raises(ValidationError):
        DownloadFile.model_validate(values)


@pytest.mark.parametrize("size", [None, 0, 10])
async def test_download_preserves_metadata_and_uses_a_query_identifier(size):
    ctx = Context()
    ctx.metadata["size_bytes"] = size
    result = await App().download_file(ctx, DownloadFile(file_id="原样/标识"))
    assert type(result) is FileOutput and result.size_bytes == size and result.mime_type is None
    assert ctx.calls == [
        ("files/metadata", {"params": {"file_id": "原样/标识"}}),
        (
            "files/content",
            {
                "params": {"file_id": "原样/标识"},
                "file_name": "a.json",
                "mime_type": None,
                "size_bytes": size,
                "external_resource_id": "原样/标识",
                "max_file_bytes": MAX_FILE_BYTES,
            },
        ),
    ]
    await result.content.aclose()


@pytest.mark.parametrize(
    "change",
    [
        {"file_id": "other"},
        {"size_bytes": True},
        {"size_bytes": -1},
        {"size_bytes": "0"},
        {"file_name": "../path"},
        {"url": "https://other.test"},
    ],
)
async def test_invalid_metadata_never_yields_a_successful_output(change):
    ctx = Context()
    ctx.metadata.update(change)
    with pytest.raises(ValueError):
        await App().download_file(ctx, DownloadFile(file_id="原样/标识"))


class UploadContext:
    def __init__(self, status=201, change=None):
        self.status, self.change, self.calls = status, change or {}, []

    def http(self, name):
        assert name == "api"
        return self

    async def request_file(self, method, path, **kwargs):
        import json

        assert (method, path) == ("POST", "files")
        assert kwargs["max_file_bytes"] == MAX_FILE_BYTES
        self.calls.append(kwargs["params"])
        size = sum([len(chunk) async for chunk in kwargs["file"].content])
        value = {
            "file_id": "原样/标识",
            "file_name": "原样.bin",
            "mime_type": None,
            "size_bytes": size,
        } | self.change

        async def read():
            return json.dumps(value).encode()

        return await kwargs["consume"](SimpleNamespace(status_code=self.status, read=read))


@pytest.mark.parametrize("size", [None, 0, 9])
async def test_upload_returns_typed_service_result(size):
    async def source():
        yield b"" if size == 0 else b"raw\x00bytes"

    context = UploadContext()
    result = await App().upload_file(
        context, UploadParams(), FileInput(file_name="原样.bin", size_bytes=size, content=source())
    )
    assert result.file_id == "原样/标识" and result.size_bytes == (0 if size == 0 else 9)
    assert context.calls == [{"file_name": "原样.bin"}]


@pytest.mark.parametrize("status", [200, 202, 400, 401, 403, 413, 429, 500])
async def test_upload_only_definite_no_effect_rejections_are_rejected(status):
    async def source():
        yield b"x"

    with pytest.raises(OperationRejected if status in (400, 401, 403, 413) else ValueError):
        await App().upload_file(
            UploadContext(status), UploadParams(), FileInput(file_name="原样.bin", content=source())
        )


@pytest.mark.parametrize(
    "change",
    [
        {"file_id": " "},
        {"file_name": "../x"},
        {"file_name": "other"},
        {"mime_type": " "},
        {"mime_type": "text/plain"},
        {"size_bytes": True},
        {"size_bytes": -1},
        {"size_bytes": "1"},
        {"size_bytes": 2},
        {"url": "https://other.test"},
    ],
)
async def test_upload_receipt_is_strict_and_correlated(change):
    async def source():
        yield b"x"

    with pytest.raises(ValueError):
        await App().upload_file(
            UploadContext(change=change),
            UploadParams(),
            FileInput(file_name="原样.bin", size_bytes=1, content=source()),
        )


def test_upload_parameters_do_not_accept_platform_material_or_remote_urls():
    for values in ({"artifact_id": "a"}, {"url": "https://other.test"}, {"file_name": "x"}):
        with pytest.raises(ValidationError):
            UploadParams.model_validate(values)
