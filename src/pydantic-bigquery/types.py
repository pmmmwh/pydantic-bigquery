from __future__ import annotations

from collections.abc import Sequence
from pydantic import BaseModel
from typing import Literal

BQType = Literal[
    "STRING",
    "BYTES",
    "INTEGER",
    "INT64",
    "FLOAT",
    "FLOAT64",
    "BOOLEAN",
    "BOOL",
    "TIMESTAMP",
    "DATE",
    "TIME",
    "DATETIME",
    "GEOGRAPHY",
    "NUMERIC",
    "BIGNUMERIC",
    "JSON",
    "RECORD",
    "STRUCT",
    "RANGE",
]


class TableFieldSchema(BaseModel):
    description: str | None = None
    fields: Sequence[TableFieldSchema] | None = None
    mode: Literal["NULLABLE", "REPEATED", "REQUIRED"] = "NULLABLE"
    name: str
    type: BQType


class TableSchema(BaseModel):
    fields: Sequence[TableFieldSchema] | None = None
