from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from llm_sdk.llm_sdk import Small_LLM_Model

from ..generation.vocabulary import Vocabulary
from .models_json_files import FunctionSchema, PromptSchema


class ReaderModel(BaseModel):
    """Validation model for Reader inputs.

    Attributes:
        files: Dict mapping CLI flags to file paths.
    """

    files: dict[str, str]


class ParserModel(BaseModel):
    """Validation model for Parser inputs.

    Attributes:
        args: Raw CLI arguments from sys.argv.
    """

    args: list[str]


class WriterModel(BaseModel):
    """Validation model for Writer inputs.

    Attributes:
        results: List of raw result dicts to write.
        output_path: Path to the output JSON file.
    """

    results: list[dict[str, Any]]
    output_path: str


class TypeParserModel(BaseModel):
    """Validation model for type parser inputs
      (NumberParser, StringParser, ArrayParser).

    Attributes:
        vocab: The Vocabulary instance used for token filtering.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    vocab: Vocabulary


class StateMachineModel(BaseModel):
    """Validation model for StateMachine inputs.

    Attributes:
        llm: The language model instance.
        prompt: The user prompt being processed.
        functions: List of available function schemas.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    llm: Small_LLM_Model
    prompt: PromptSchema
    functions: list[FunctionSchema]


class VocabularyModel(BaseModel):
    """Validation model for Vocabulary inputs.

    Attributes:
        llm: The language model instance used to access the token vocabulary.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    llm: Small_LLM_Model


class GeneratorModel(BaseModel):
    """Validation model for Generator inputs.

    Attributes:
        llm: The language model instance.
        functions: List of available function schemas.
        output: Path to the output file.
        token_count: Optional initial token count for performance tracking.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    llm: Small_LLM_Model
    functions: list[FunctionSchema]
    output: str
    token_count: int | None = Field(default=None)
