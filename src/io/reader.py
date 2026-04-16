import json

from ..models.models_class import ReaderModel
from ..models.models_json_files import FunctionSchema, PromptSchema


class Reader():
    def __init__(self, files: dict[str, str]) -> None:

        ReaderModel(
            files=files
            )

        self.files = files

    def get_functions(self) -> list[FunctionSchema]:
        file = self.files["--functions_definition"]
        # try:
        with open(file, 'r') as f:
            data = json.load(f)
        return [FunctionSchema.model_validate(fn) for fn in data]

    def get_prompts(self) -> list[PromptSchema]:
        file = self.files["--input"]
        # try:
        with open(file, 'r') as f:
            data = json.load(f)
        return [PromptSchema.model_validate(prompt) for prompt in data]

    def get_output_path(self) -> str:
        return self.files["--output"]
