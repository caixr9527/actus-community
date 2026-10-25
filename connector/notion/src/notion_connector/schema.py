"""Conservative validation of the advertised input schema before tools/call."""

from connector_sdk import OperationRejected


class UnsupportedSchema(OperationRejected):
    """Cannot safely infer whether an unsupported alternative would also match."""


def validate(value, schema, *, root=None, depth=0):
    if depth > 24 or not isinstance(schema, (dict, bool)):
        raise UnsupportedSchema()
    root = schema if root is None else root
    if schema is True:
        return
    if schema is False:
        raise OperationRejected()
    supported = {
        "$schema", "$id", "$defs", "definitions", "$ref", "title", "description", "default",
        "examples", "deprecated", "readOnly", "writeOnly", "format", "type", "properties",
        "required", "additionalProperties", "items", "enum", "const", "anyOf", "oneOf", "allOf",
        "minLength", "maxLength", "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
        "minItems", "maxItems", "uniqueItems", "minProperties", "maxProperties",
    }
    if set(schema) - supported:
        raise UnsupportedSchema()

    def check(item, definition):
        validate(item, definition, root=root, depth=depth + 1)

    if "$ref" in schema:
        ref = schema["$ref"]
        if not isinstance(ref, str) or not ref.startswith("#/"):
            raise UnsupportedSchema()
        target = root
        try:
            for part in ref[2:].split("/"):
                target = target[part.replace("~1", "/").replace("~0", "~")]
        except (KeyError, TypeError):
            raise OperationRejected() from None
        check(value, target)
    for kind in ("anyOf", "oneOf", "allOf"):
        if kind not in schema:
            continue
        choices = schema[kind]
        if not isinstance(choices, list) or not 1 <= len(choices) <= 64:
            raise UnsupportedSchema()
        matched = 0
        for choice in choices:
            try:
                check(value, choice)
                matched += 1
            except UnsupportedSchema:
                raise
            except OperationRejected:
                pass
        if not (matched == len(choices) if kind == "allOf" else
                matched == 1 if kind == "oneOf" else matched > 0):
            raise OperationRejected()
    kinds = {
        "object": isinstance(value, dict), "array": isinstance(value, list),
        "string": isinstance(value, str), "boolean": type(value) is bool,
        "integer": type(value) is int, "number": type(value) in (int, float),
        "null": value is None,
    }
    declared = schema.get("type", list(kinds))
    declared = [declared] if isinstance(declared, str) else declared
    if (not isinstance(declared, list) or not declared
            or any(not isinstance(t, str) or t not in kinds for t in declared)):
        raise UnsupportedSchema()
    if not any(kinds[t] for t in declared):
        raise OperationRejected()
    if "enum" in schema and (not isinstance(schema["enum"], list) or not schema["enum"]
                             or any(isinstance(v, (dict, list)) for v in schema["enum"])):
        raise UnsupportedSchema()
    if isinstance(schema.get("const"), (dict, list)):
        raise UnsupportedSchema()
    if "enum" in schema and not any(type(value) is type(v) and value == v for v in schema["enum"]):
        raise OperationRejected()
    if ("const" in schema
            and not (type(value) is type(schema["const"]) and value == schema["const"])):
        raise OperationRejected()
    constraints = []
    if isinstance(value, dict):
        properties, required = schema.get("properties", {}), schema.get("required", [])
        if not isinstance(properties, dict) or not isinstance(required, list):
            raise UnsupportedSchema()
        if any(not isinstance(key, str) for key in required):
            raise UnsupportedSchema()
        if any(key not in value for key in required):
            raise OperationRejected()
        for key, item in value.items():
            check(item, properties.get(key, schema.get("additionalProperties", True)))
        constraints = [("minProperties", len(value), "min"), ("maxProperties", len(value), "max")]
    elif isinstance(value, list):
        for item in value:
            check(item, schema.get("items", True))
        if schema.get("uniqueItems") and any(item in value[:i] for i, item in enumerate(value)):
            raise OperationRejected()
        constraints = [("minItems", len(value), "min"), ("maxItems", len(value), "max")]
    elif isinstance(value, str):
        constraints = [("minLength", len(value), "min"), ("maxLength", len(value), "max")]
    elif type(value) in (int, float):
        constraints = [("minimum", value, "min"), ("maximum", value, "max"),
                       ("exclusiveMinimum", value, "exclusive_min"),
                       ("exclusiveMaximum", value, "exclusive_max")]
    for key, actual, comparison in constraints:
        if key not in schema:
            continue
        limit = schema[key]
        if type(limit) not in (int, float):
            raise OperationRejected()
        if ((comparison == "min" and actual < limit)
                or (comparison == "max" and actual > limit)
                or (comparison == "exclusive_min" and actual <= limit)
                or (comparison == "exclusive_max" and actual >= limit)):
            raise OperationRejected()


def arguments(name, params, schema):
    """Only these mappings can reach the remote endpoint, including both view layouts."""
    value = dict(params)
    if name == "query_database_view":
        value = {"mode": "view", "view_url": params["view_url"]}
        value.update({k: params[k] for k in ("start_cursor", "page_size") if k in params})
        if "include_archived" in params:
            value["is_archived"] = params["include_archived"]
        if "data" in schema.get("properties", {}):
            value = {"data": value}
    elif name == "create_page":
        value = {"pages": [{"properties": {"title": params["title"]},
                            "content": params["content"]}],
                 "parent": {"page_id": params["parent_id"]}}
        if "allow_async" in params:
            value["allow_async"] = params["allow_async"]
    elif name == "update_page":
        value = {"page_id": params["page_id"], "command": "replace_content",
                 "new_str": params["content"]}
        if "allow_async" in params:
            value["allow_async"] = params["allow_async"]
    elif name == "move_pages":
        parent = {"type": params["parent_type"]}
        if params["parent_type"] != "workspace":
            parent[params["parent_type"]] = params["parent_id"]
        value = {"page_or_database_ids": params["page_or_database_ids"], "new_parent": parent}
    validate(value, schema)
    return value
