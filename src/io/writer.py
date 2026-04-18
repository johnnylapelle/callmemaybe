import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from ..models.models_class import WriterModel
from ..models.models_json_files import OutputSchema


class Writer:
    """Validates and writes generation results to a JSON output file.

    Args:
        results: List of raw result dicts from the generation pipeline.
        output_path: Path to the output JSON file.
    """
    def __init__(self, results: list[dict[str, Any]],
                 output_path: str):
        """Initialize Writer and create output directory if needed.

        Args:
            results: List of raw result dicts from the generation pipeline.
            output_path: Path to the output JSON file.
        """
        WriterModel(
            results=results,
            output_path=output_path
        )

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        self.results = results
        self.output_path = output_path

    def write(self) -> None:
        """Validate each result against OutputSchema and write to JSON file.

        Invalid results are skipped with an error message.
        """
        validated: list[dict[str, Any]] = []

        for result in self.results:
            try:
                data = OutputSchema.model_validate(result).model_dump()
                validated.append(data)

            except ValidationError as e:
                raise ValueError(f"Invalid result {e}")
            except Exception as e:
                raise ValueError(f"Invalid result {e}")

        with open(self.output_path, 'w') as f:
            json.dump(validated, f, indent=4)
