from __future__ import annotations

from typing import Any

from .types import BQType, TableFieldSchema, TableSchema

_bq_type_mapping: dict[str, BQType] = {
    "boolean": "BOOLEAN",
    "integer": "INTEGER",
    "number": "FLOAT",
    "string": "STRING",
}
_bq_format_mapping: dict[str, BQType] = {
    "date": "DATE",
    "date-time": "TIMESTAMP",
    "time": "TIME",
}


def json_type_to_bq_type(
    key: str,
    current: dict[str, Any],
    schema: dict[str, dict[str, Any]],
) -> TableFieldSchema:
    # FIXME: Non-optional nullable fields parsing
    match current:
        case {"$ref": ref}:
            path: list[str] = ref.replace("#/", "").split("/")
            sub_schema = schema
            for segment in path:
                next_schema = sub_schema.get(segment)
                if not next_schema:
                    raise NotImplementedError(f"JSON reference unresolvable: {ref}")
                sub_schema = next_schema

            field_schema = json_type_to_bq_type(key, sub_schema, schema)
        case {"anyOf": [*any_of]}:
            null_schemas = [s for s in any_of if s == {"type": "null"}]
            non_null_schemas = [s for s in any_of if s != {"type": "null"}]
            if len(non_null_schemas) > 1:
                raise NotImplementedError(f"JSON schema union too complex: {any_of!s}")
            field_schema = json_type_to_bq_type(key, non_null_schemas[0], schema)
            if null_schemas and field_schema.mode != "REPEATED":
                field_schema.mode = "NULLABLE"
        case {"type": "array", "items": items}:
            field_schema = json_type_to_bq_type(key, items, schema)
            field_schema.mode = "REPEATED"
        case {"type": "object", "properties": properties} as obj_schema:
            required: list[str] = (
                obj_schema["required"] if "required" in obj_schema else []
            )
            fields: list[TableFieldSchema] = []
            for prop, type_schema in properties.items():
                sub_schema = json_type_to_bq_type(prop, type_schema, schema)
                if prop in required and sub_schema.mode != "REPEATED":
                    if sub_schema.mode == "NULLABLE":
                        raise NotImplementedError(
                            f"JSON schema nullable required behaviour not supported: {obj_schema['title']} -> {prop}"
                        )
                    sub_schema.mode = "REQUIRED"
                fields.append(sub_schema)

            field_schema = TableFieldSchema(
                name=key,
                fields=fields,
                type="RECORD",
                mode="REQUIRED",
            )
        case {"type": "string", "format": format}:
            type_name = _bq_format_mapping.get(format)
            if not type_name:
                raise NotImplementedError(f"JSON schema format unsupported: {format}")
            field_schema = TableFieldSchema(
                name=key,
                type=type_name,
                mode="REQUIRED",
            )
        case {"type": schema_type}:
            type_name = _bq_type_mapping.get(schema_type)
            if not type_name:
                raise NotImplementedError(
                    f"JSON schema type unsupported: {schema_type}"
                )
            field_schema = TableFieldSchema(
                name=key,
                type=type_name,
                mode="REQUIRED",
            )
        case _ as unsupported:
            raise NotImplementedError(
                f"JSON schema expression unsupported: {unsupported!s}"
            )
    return field_schema


def json_schema_to_bq_schema(schema: dict[str, Any]) -> TableSchema:
    return TableSchema(
        fields=[
            json_type_to_bq_type(key, type_schema, schema)
            for key, type_schema in schema["properties"].items()
        ]
    )
