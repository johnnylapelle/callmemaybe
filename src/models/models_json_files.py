from typing import Any, Literal

from pydantic import BaseModel

AllowedType = Literal["number", "string", "boolean", "integer", "array"]


class TypeDef(BaseModel):
    """Represents a type definition for a function parameter or return value.

    Attributes:
        type: The allowed type, restricted to number,
          string, boolean, integer, or array.
    """
    model_config = {"extra": "forbid"}
    type: AllowedType


class FunctionSchema(BaseModel):
    """Schema for a function definition
      loaded from the functions definition file.

    Attributes:
        name: The function identifier used during generation.
        description: Human-readable description of the function's purpose.
        parameters: Dict mapping parameter names to their type definitions.
        returns: The return type definition of the function.
    """
    model_config = {"extra": "forbid"}
    name: str
    description: str
    parameters: dict[str, TypeDef]
    returns: TypeDef


class PromptSchema(BaseModel):
    """Schema for a single user prompt loaded from the input file.

    Attributes:
        prompt: The natural language request to process.
    """
    model_config = {"extra": "forbid"}
    prompt: str


class OutputSchema(BaseModel):
    """Schema for a single generation result written to the output file.

    Attributes:
        prompt: The original user prompt.
        name: The function name selected by the generation pipeline.
        parameters: Dict mapping parameter names to their generated values.
    """
    model_config = {"extra": "forbid"}
    prompt: str
    name: str
    parameters: dict[str, Any]
