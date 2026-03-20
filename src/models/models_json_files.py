from pydantic import BaseModel
from typing import Literal


AllowedType = Literal["number", "string", "boolean", "integer"]


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
