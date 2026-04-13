from pydantic import BaseModel, ConfigDict
from ..generation.vocabulary import Vocabulary
from llm_sdk.llm_sdk import Small_LLM_Model
from .models_json_files import PromptSchema, FunctionSchema


class ReaderModel(BaseModel):
    files: dict[str, str]


class ParserModel(BaseModel):
    args: list[str]


class TypeParserModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    # vocab: Vocabulary


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
