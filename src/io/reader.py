import json
from ..models.models_class import ReaderModel
from pydantic import TypeAdapter
from ..models.models_json_files import FunctionSchema, PromptSchema


class Reader():
    def __init__(self, files: dict[str, str]) -> None:
        try:
            ReaderModel(files=files)
            self.files = files
        except Exception as e:
            print(f"Error: {e}")

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
