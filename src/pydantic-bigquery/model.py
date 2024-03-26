from __future__ import annotations

from typing import Literal

from pydantic import BaseModel
from pydantic.json_schema import DEFAULT_REF_TEMPLATE, GenerateJsonSchema

from .schema import json_schema_to_bq_schema
from .types import TableSchema


class BQBaseModel(BaseModel):
    @classmethod
    def model_bq_schema(
        cls,
        by_alias: bool = True,
        ref_template: str = DEFAULT_REF_TEMPLATE,
        schema_generator: type[GenerateJsonSchema] = GenerateJsonSchema,
        mode: Literal["validation", "serialization"] = "validation",
    ) -> TableSchema:
        json_schema = super().model_json_schema(
            by_alias,
            ref_template,
            schema_generator,
            mode,
        )
        return json_schema_to_bq_schema(json_schema)
