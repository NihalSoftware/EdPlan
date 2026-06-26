from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel

SchemaT = TypeVar("SchemaT", bound=BaseModel)


def coerce_payload(schema: type[SchemaT], payload: SchemaT | dict[str, Any] | None) -> SchemaT:
    if isinstance(payload, schema):
        return payload
    return schema.model_validate(payload or {})
