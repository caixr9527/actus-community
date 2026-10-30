"""A typed generic adapter using the public SDK only."""

from pathlib import Path
from types import SimpleNamespace

import pytest
from connector_sdk import AuthorizationRejected, FileOutput, load_project
from pydantic import ValidationError

from file_demo.app import MAX_FILE_BYTES, App, Auth, DownloadFile


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


def test_manifest_has_one_generic_file_operation():
    declared = load_project(Path(__file__).resolve().parents[1] / "pyproject.toml")
    assert declared.manifest.id == "file-demo" and declared.manifest.auth.type == "api_key"
    assert tuple(declared.operations) == ("download_file",)
    op = declared.manifest.operations[0]
    assert op.transport == "file_output" and op.output_schema is None
    assert op.effects == "read" and op.max_file_bytes == MAX_FILE_BYTES
    assert set(op.input_schema["properties"]) == {"file_id"}
    assert "https://" not in declared.manifest.to_json()


@pytest.mark.parametrize("permissions", [None, [], ["files.read"]])
async def test_identity_and_unknown_permissions_are_preserved(permissions):
    value = await Auth().verify(Context(permissions=permissions))
    assert value.identity.account_id == " a " and value.identity.tenant_id is None
    assert value.capabilities == (
        None if permissions is None else {"files.read": "files.read" in permissions}
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
