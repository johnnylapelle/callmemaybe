from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from llm_sdk.llm_sdk import Small_LLM_Model

from ..generation.vocabulary import Vocabulary
from .models_json_files import FunctionSchema, PromptSchema


class ReaderModel(BaseModel):
    files: dict[str, str]


class ParserModel(BaseModel):
    args: list[str]


class WriterModel(BaseModel):
    results: list[dict[str, Any]]
    output_path: str


class TypeParserModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    vocab: Vocabulary


class StateMachineModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    llm: Small_LLM_Model
    prompt: PromptSchema
    functions: list[FunctionSchema]


class VocabularyModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    llm: Small_LLM_Model


class GeneratorModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    llm: Small_LLM_Model
    functions: list[FunctionSchema]
    output: str
    token_count: int | None = Field(default=None)
