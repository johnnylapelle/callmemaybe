import json
from ..models.models_class import ReaderModel
from pydantic import ValidationError
from ..models.models_json_files import FunctionSchema, PromptSchema
import sys


class Reader():
    def __init__(self, files: dict[str, str]) -> None:
        try:
            ReaderModel(files=files)
            self.files = files
        except Exception as e:
            print(f"Error: {e}")

    def get_functions(self):
        file = self.files["--functions_definition"]
        try:
            with open(file, 'r') as f:
                data = json.load(f)
            return [FunctionSchema.model_validate(fn) for fn in data]
        except json.JSONDecodeError as e:
            print(f"Error: {e}")
            sys.exit()
        except ValidationError as e:
            print(f"Error: {e}")
            sys.exit()

    def get_prompts(self):
        file = self.files["--input"]
        try:
            with open(file, 'r') as f:
                data = json.load(f)
            return [PromptSchema.model_validate(prompt) for prompt in data]
        except json.JSONDecodeError as e:
            print(f"Error: {e}")
            sys.exit()
        except ValidationError as e:
            print(f"Error: {e}")
            sys.exit()

    def get_output_path(self) -> str:
        return self.files["--output"]
