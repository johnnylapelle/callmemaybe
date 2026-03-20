import json
from pydantic import BaseModel, TypeAdapter
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


class Reader():
    def __init__(self, files: dict[str, str]) -> None:
        self.files = files
        self.arguments = ["--functions_definition",
                          "--input"]

    def validate_schema(self) -> None:
        for name, file in self.files.items():
            if name in self.arguments:
                with open(file, 'r') as f:
                    try:
                        if name == "--functions_definition":
                            data = json.load(f)
                            adapter = TypeAdapter(list[FunctionSchema])
                            adapter.validate_python(data)

                        if name == "--input":
                            data = json.load(f)
                            adapter = TypeAdapter(list[PromptSchema])
                            adapter.validate_python(data)
                    except Exception as e:
                        print(f"Invalid schema in '{file}':\n{e}.")
