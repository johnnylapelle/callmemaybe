import json

from pydantic import ValidationError

from ..models.models_class import ReaderModel
from ..models.models_json_files import FunctionSchema, PromptSchema


class Reader():
    """Reads and validates input files for the generation pipeline.

    Args:
        files: Dict mapping CLI flags to file paths.
            Expected keys: ``--functions_definition``,
              ``--input``, ``--output``.
    """

    def __init__(self, files: dict[str, str]) -> None:
        """Initialize Reader and validate the files dict.

        Args:
            files: Dict mapping CLI flags to file paths.
        """
        ReaderModel(
            files=files
            )

        self.files = files

    def get_functions(self) -> list[FunctionSchema]:
        """Load and validate function schemas from
          the functions definition file.

        Returns:
            List of validated FunctionSchema objects.

        Raises:
            ValueError: If the file contains invalid or missing fields.
        """
        file = self.files["--functions_definition"]
        try:
            with open(file, 'r') as f:
                data = json.load(f)

            if not data:
                raise ValueError(f"File {file} is empty.")

            return [FunctionSchema.model_validate(fn) for fn in data]

        except ValidationError as e:
            errors = "\n".join(
                f"  - {' -> '.join(str(x) for x in err['loc'])}: {err['msg']}"
                for err in e.errors()
            )
            raise ValueError(f"Invalid File {file}:\n{errors}")
        except FileNotFoundError:
            raise ValueError(f"File not found: {file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {file}: {e}")

    def get_prompts(self) -> list[PromptSchema]:
        """Load and validate prompts from the input file.

        Returns:
            List of validated PromptSchema objects.

        Raises:
            ValueError: If the file contains invalid or missing fields.
        """
        file = self.files["--input"]
        try:
            with open(file, 'r') as f:
                data = json.load(f)

            if not data:
                raise ValueError(f"File {file} is empty.")

            return [PromptSchema.model_validate(prompt) for prompt in data]

        except ValidationError as e:
            errors = "\n".join(
                f"  - {' -> '.join(str(x) for x in err['loc'])}: {err['msg']}"
                for err in e.errors()
            )
            raise ValueError(f"Invalid File {file}:\n{errors}")
        except FileNotFoundError:
            raise ValueError(f"File not found: {file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {file}: {e}")

    def get_output_path(self) -> str:
        """Return the output file path.

        Returns:
            Path string for the output file.
        """
        return self.files["--output"]
