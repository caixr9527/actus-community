"""Generate static declarations offline and emit an apply_patch document."""

import argparse
import json
import keyword
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUPPORTED = {"type", "properties", "required", "description", "title", "enum", "items"}


def class_name(value):
    return "".join(x.capitalize() for x in re.split(r"[^a-zA-Z0-9]", value))


def generate(group, contracts):
    definitions = []
    methods = []

    def annotation(schema, name):
        if set(schema) - SUPPORTED:
            raise ValueError(f"unsupported schema at {name}")
        kind = schema["type"]
        if "enum" in schema:
            return "Literal[" + ", ".join(repr(x) for x in schema["enum"]) + "]"
        if kind == "object":
            if not schema.get("properties"):
                return "dict[str, JsonValue]"
            fields = []
            for field, child in schema["properties"].items():
                pyname = (
                    field if field.isidentifier() and not keyword.iskeyword(field) else field + "_"
                )
                if not pyname.isidentifier() or pyname.startswith("_"):
                    raise ValueError("unsupported field name")
                type_name = annotation(child, name + class_name(field))
                args = []
                if field not in schema.get("required", []):
                    # Omission is allowed; explicit null still fails type validation.
                    args.append("default=None")
                if field != pyname:
                    args.append(f"alias={field!r}")
                if child.get("description"):
                    args.append(f"description={child['description']!r}")
                if child["type"] == "string" and "enum" not in child:
                    args.append("max_length=100000")
                if child["type"] == "array":
                    args.append("max_length=100")
                fields.append(f"    {pyname}: {type_name} = Field({', '.join(args)})")
            definitions.append(f"class {name}(Input):\n" + "\n".join(fields))
            return name
        if kind == "array":
            return f"list[{annotation(schema['items'], name + 'Item')}]"
        return {"string": "str", "integer": "int", "number": "float", "boolean": "bool"}[kind]

    for tool in contracts:
        local = tool["local_name"]
        name = class_name(local) + "Input"
        schema = tool["inputSchema"]
        if schema.get("properties"):
            annotation(schema, name)
        else:
            definitions.append(f"class {name}(Input):\n    pass")
        description = tool["description"].split(" if both tencent-docs", 1)[0]
        methods.append(
            f"    @operation(name={local!r}, description={description!r}, effects={tool['effects']!r})\n"
            f"    async def {local}(self, ctx, params: {name}) -> Result:\n"
            f"        return await call(ctx, {tool['name']!r}, params.model_dump(mode='json', by_alias=True, exclude_unset=True))"
        )
    return (
        '"""Generated from reviewed contracts; regenerate with tools/generate.py."""\n\n'
        "from typing import Literal\n\nfrom pydantic import Field\n"
        "from connector_sdk import operation\nfrom .models import Input, Result, JsonValue\n"
        "from .mcp import call\n\n\n"
        + "\n\n\n".join(definitions)
        + f"\n\n\nclass {class_name(group)}Operations:\n"
        + "\n\n".join(methods)
        + "\n"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("group")
    args = parser.parse_args()
    tools = json.loads((ROOT / "contracts" / f"{args.group}.json").read_text())
    output = generate(args.group, tools)
    path = ROOT / "src" / "tencent_docs" / f"{args.group}.py"
    print("*** Begin Patch")
    if path.exists():
        print(f"*** Update File: {path}")
        print("@@")
        for line in path.read_text().splitlines():
            print("-" + line)
    else:
        print(f"*** Add File: {path}")
    for line in output.splitlines():
        print("+" + line)
    print("*** End Patch")


if __name__ == "__main__":
    main()
