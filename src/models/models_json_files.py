from typing import Any, Literal

from pydantic import BaseModel

AllowedType = Literal["number", "string", "boolean", "integer", "array"]


class TypeDef(BaseModel):
    model_config = {"extra": "forbid"}
    type: AllowedType


class FunctionSchema(BaseModel):
    model_config = {"extra": "forbid"}
    name: str
    description: str
    parameters: dict[str, TypeDef]
    returns: TypeDef


class PromptSchema(BaseModel):
    model_config = {"extra": "forbid"}
    prompt: str


class OutputSchema(BaseModel):
    model_config = {"extra": "forbid"}
    prompt: str
    name: str
    parameters: dict[str, Any]
