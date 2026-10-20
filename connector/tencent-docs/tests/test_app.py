import ast
import base64
import importlib.util
import json
from pathlib import Path

import pytest
from connector_sdk import AuthorizationRejected, HttpError, OperationRejected, load_project
from pydantic import ValidationError

from tencent_docs.app import App, Auth
from tencent_docs.mcp import Session, call, payload
from tencent_docs.models import CreateDocument, ListFiles

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = [
    tool
    for path in sorted((ROOT / "contracts").glob("*.json"))
    for tool in json.loads(path.read_text())
]
DECLARED = load_project(ROOT / "pyproject.toml")


class Response:
    def __init__(self, status=200, data=None, headers=None, chunks=None):
        self.status_code = status
        self.headers = {"content-type": "application/json", **(headers or {})}
        self.chunks = chunks if chunks is not None else [json.dumps(data).encode()]

    async def read(self):
        return b"".join(self.chunks)

    async def iter_bytes(self):
        for chunk in self.chunks:
            yield chunk


class Context:
    def __init__(self, result=None, responses=None):
        self.calls = []
        self.result = result or {"structuredContent": {"ok": True}}
        self.responses = list(responses) if responses is not None else None

    def http(self, name):
        assert name == "tencent"
        return self

    async def request(self, method, path, *, consume, headers, json=None):
        self.calls.append((method, path, headers, json))
        if self.responses is not None:
            response = self.responses.pop(0)
            if isinstance(response, Exception):
                raise response
            return await consume(response)
        if json["method"] == "notifications/initialized":
            return await consume(Response(202, chunks=[]))
        result = (
            {"protocolVersion": "2025-03-26"} if json["method"] == "initialize" else self.result
        )
        return await consume(Response(data={"jsonrpc": "2.0", "id": json["id"], "result": result}))


def minimal(schema):
    if "enum" in schema:
        return schema["enum"][0]
    kind = schema["type"]
    if kind == "object":
        return {k: minimal(schema["properties"][k]) for k in schema.get("required", [])}
    if kind == "array":
        return []
    return {"string": "fixture", "integer": 1, "number": 1.0, "boolean": True}[kind]


def test_static_catalog_and_size():
    declared = DECLARED
    assert len(declared.operations) == len(CONTRACTS) == 219
    assert set(declared.operations) == {t["local_name"] for t in CONTRACTS}
    assert len(declared.to_json().encode()) < 1024 * 1024
    for op in declared.manifest.operations:
        source = next(t for t in CONTRACTS if t["local_name"] == op.name)
        assert op.effects == source["effects"]
        assert op.transport == "json"
    assert declared.manifest.auth.type == "api_key"
    assert "flowchart_read" not in declared.operations


@pytest.mark.parametrize(
    "tool",
    [
        t
        for t in CONTRACTS
        if t["local_name"]
        not in {
            "list_files",
            "search_files",
            "list_spaces",
            "list_space_nodes",
            "read_document",
            "create_document",
        }
    ],
    ids=lambda t: t["local_name"],
)
async def test_every_extended_operation_routes_exact_frozen_contract(tool):
    declared = DECLARED
    op = declared.operations[tool["local_name"]]
    arguments = minimal(tool["inputSchema"])
    params = op.input_model.model_validate(arguments, strict=True)
    ctx = Context()
    result = await op.method(App(), ctx, params)
    assert result.data == {"ok": True}
    assert ctx.calls[-1][3]["params"] == {"name": tool["name"], "arguments": arguments}
    with pytest.raises(ValidationError):
        op.input_model.model_validate({**arguments, "unknown_argument": 1})


async def test_alias_defaults_and_markdown():
    ctx = Context()
    await App().list_files(ctx, ListFiles())
    assert ctx.calls[-1][3]["params"]["arguments"] == {"num": 1, "count": 20, "order_by": 0}
    await App().create_document(ctx, CreateDocument(title="test", markdown="中文 **test**"))
    args = ctx.calls[-1][3]["params"]["arguments"]
    assert base64.b64decode(args["base64_markdown"]).decode() == "中文 **test**"
    with pytest.raises(ValidationError):
        ListFiles(page_size=21)


@pytest.mark.parametrize(
    "name,params,external,expected",
    [
        ("search_files", {"keyword": "report"}, "manage.search_file", {"search_key": "report"}),
        (
            "list_spaces",
            {},
            "query_space_list",
            {"num": 0, "descending": True, "query_by": 0, "order_by": 1},
        ),
        (
            "list_space_nodes",
            {"space_id": "space"},
            "query_space_node",
            {"space_id": "space", "parent_id": "", "num": 0},
        ),
        ("read_document", {"file_id": "file"}, "get_content", {"file_id": "file"}),
    ],
)
async def test_remaining_aliases(name, params, external, expected):
    op = DECLARED.operations[name]
    ctx = Context()
    await op.method(App(), ctx, op.input_model.model_validate(params))
    assert ctx.calls[-1][3]["params"] == {"name": external, "arguments": expected}


async def test_identity_is_vendor_account_not_token():
    ctx = Context({"structuredContent": {"user_id": "12345", "nick": "Test"}})
    verified = await Auth().verify(ctx)
    assert verified.identity.account_id == "12345"
    assert verified.capabilities is None
    with pytest.raises(ValidationError):
        await Auth().verify(Context({"structuredContent": {"nick": "Missing ID"}}))


@pytest.mark.parametrize(
    "result",
    [
        {"isError": True, "content": [{"type": "text", "text": "private upstream error"}]},
        {"structuredContent": []},
        {"content": []},
        {"content": [{"type": "text", "text": "not JSON"}]},
        {"isError": "false", "structuredContent": {}},
    ],
)
def test_unknown_tool_failures_are_not_success_or_definite_rejection(result):
    with pytest.raises(HttpError) as error:
        payload(result)
    assert "private" not in str(error.value)


def test_text_json_fallback_preserves_empty_result():
    assert payload({"content": [{"type": "text", "text": "{}"}]}).data == {}


async def test_read_document_vendor_error_is_not_success():
    ctx = Context({"structuredContent": {"error": "vendor private error", "content": ""}})
    with pytest.raises(HttpError, match="tencent_tool_failed"):
        await call(ctx, "get_content", {"file_id": "test-only"})


async def test_sse_utf8_split_comments_multiline_and_session():
    body = 'data: {"jsonrpc":"2.0","id":1,\r\ndata: "result":{"protocolVersion":"2025-03-26","text":"中文"}}\r\n\r\n'.encode()
    ctx = Context(
        responses=[
            Response(
                headers={"content-type": "text/event-stream", "mcp-session-id": "session-1"},
                chunks=[b": ping\r\n\r\n", *[body[i : i + 1] for i in range(len(body))]],
            ),
            Response(202, chunks=[]),
            Response(204, chunks=[]),
        ]
    )
    session = Session(ctx)
    await session.initialize()
    await session.close()
    assert ctx.calls[1][2]["Mcp-Session-Id"] == "session-1"
    assert ctx.calls[-1][0] == "DELETE"


@pytest.mark.parametrize("separator", [b"\n", b"\r\n", b"\r"])
async def test_sse_standard_line_endings_and_bom(separator):
    event = (
        b'\xef\xbb\xbfdata: {"jsonrpc":"2.0","id":1,'
        b'"result":{"protocolVersion":"2025-03-26"}}' + separator + separator
    )
    ctx = Context(
        responses=[
            Response(
                headers={"content-type": "text/event-stream"},
                chunks=[event[i : i + 1] for i in range(len(event))],
            ),
            Response(202, chunks=[]),
        ]
    )
    await Session(ctx).initialize()


@pytest.mark.parametrize(
    "response",
    [
        Response(data={"jsonrpc": "2.0", "id": 99, "result": {}}),
        Response(headers={"content-type": "text/event-stream"}, chunks=[b"data: {}\n"]),
        Response(data={"jsonrpc": "2.0", "id": 1, "result": {}, "error": {}}),
    ],
)
async def test_malformed_protocol(response):
    with pytest.raises(HttpError):
        await Session(Context(responses=[response])).initialize()


async def test_auth_rejection_and_no_business_send_after_failed_handshake():
    ctx = Context(responses=[Response(401)])
    with pytest.raises(AuthorizationRejected):
        await Auth().verify(ctx)
    ctx = Context(responses=[HttpError("http_timeout")])
    with pytest.raises(OperationRejected):
        await call(ctx, "manage.delete_file", {"file_id": "new-test-only"})
    assert len(ctx.calls) == 1


async def test_no_retry_and_tool_error_is_unknown_after_send():
    ctx = Context({"isError": True})
    with pytest.raises(HttpError, match="tencent_tool_failed"):
        await call(ctx, "manage.delete_file", {"file_id": "new-test-only"})
    assert len(ctx.calls) == 3


async def test_tencent_negotiated_protocol():
    ctx = Context(
        responses=[
            Response(data={"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2025-03-26"}}),
            Response(202, chunks=[]),
        ]
    )
    await Session(ctx).initialize()
    assert ctx.calls[0][3]["params"]["protocolVersion"] == "2025-03-26"


def test_all_nested_input_fields_match_frozen_contracts():
    def resolve(schema, root):
        if "$ref" in schema:
            node = root
            for part in schema["$ref"][2:].split("/"):
                node = node[part.replace("~1", "/").replace("~0", "~")]
            return node
        return schema

    def compare(source, target, root):
        target = resolve(target, root)
        assert source["type"] == target["type"]
        if "enum" in source:
            assert source["enum"] == target.get("enum", [target.get("const")])
        if source["type"] == "object":
            assert set(source.get("properties", {})) == set(target.get("properties", {}))
            assert set(source.get("required", [])) == set(target.get("required", []))
            for name, value in source.get("properties", {}).items():
                compare(value, target["properties"][name], root)
        elif source["type"] == "array":
            compare(source["items"], target["items"], root)

    aliases = {
        "list_files",
        "search_files",
        "list_spaces",
        "list_space_nodes",
        "read_document",
        "create_document",
    }
    for tool in CONTRACTS:
        if tool["local_name"] in aliases:
            continue
        schema = DECLARED.operations[tool["local_name"]].input_model.model_json_schema()
        compare(tool["inputSchema"], schema, schema)


def test_generated_classes_are_reproducible_from_reviewed_snapshots():
    spec = importlib.util.spec_from_file_location("generate", ROOT / "tools/generate.py")
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    for group in ("common", "doc", "manage", "sheet", "slides", "smartsheet"):
        tools = json.loads((ROOT / "contracts" / f"{group}.json").read_text())
        expected = ast.parse(generator.generate(group, tools))
        actual = ast.parse((ROOT / "src/tencent_docs" / f"{group}.py").read_text())
        # Ruff may remove unused imports; every class, field, decorator and body is exact.
        expected_classes = [ast.dump(n) for n in expected.body if isinstance(n, ast.ClassDef)]
        actual_classes = [ast.dump(n) for n in actual.body if isinstance(n, ast.ClassDef)]
        assert actual_classes == expected_classes, group
