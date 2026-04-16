import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from ..models.models_class import WriterModel
from ..models.models_json_files import OutputSchema


class Writer:
    def __init__(self, results: list[dict[str, Any]],
                 output_path: str):

        WriterModel(
            results=results,
            output_path=output_path
        )

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        self.results = results
        self.output_path = output_path

    def write(self) -> None:
        validated: list[dict[str, Any]] = []

        for result in self.results:
            try:
                data = OutputSchema.model_validate(result).model_dump()
                data["parameters"]["replacement"] = data[
                    "parameters"]["replacement"].replace("\\\\", "\\")
                validated.append(data)

            except ValidationError as e:
                print(f"ValidationError: Invalid result {e}")

        with open(self.output_path, 'w') as f:
            json.dump(validated, f, indent=4)
