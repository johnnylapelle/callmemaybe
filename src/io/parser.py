from pathlib import Path

from ..models.models_class import ParserModel


class Parser():
    """Parses CLI arguments and validates input/output file paths.

    Args:
        args: Raw CLI arguments from sys.argv.

    Raises:
        ValueError: If arguments are invalid, duplicated, or files are missing.
    """

    def __init__(self, args: list[str]) -> None:
        """Initialize Parser, parse arguments, and validate file paths.

        Args:
            args: Raw CLI arguments from sys.argv.
        """
        ParserModel(
            args=args
            )

        self.args = args

        self.files = {
            "--functions_definition": "data/input/functions_definition.json",
            "--input": "data/input/function_calling_tests.json",
            "--output": "data/output/function_calls.json"
        }
        self.parse_args()
        self.validates_files()

    def parse_args(self) -> None:
        """Parse CLI flags and update file paths accordingly.

        Raises:
            ValueError: If a flag is missing its value, duplicated, or unknown.
        """
        arguments = {"--functions_definition": 0,
                     "--input": 0,
                     "--output": 0}

        for i, arg in enumerate(self.args):
            if arg.startswith('--'):
                if arg in arguments and arguments[arg] == 0:
                    try:
                        self.files[arg] = self.args[i + 1]
                        arguments[arg] += 1
                    except IndexError:
                        raise ValueError("A file after an args in required.")
                elif arg in arguments and arguments[arg] > 0:
                    raise ValueError(f"arguments '{arg}' found twice.")
                elif arg not in arguments:
                    raise ValueError(f"'{arg}' not a valid argument.")

    def validates_files(self) -> None:
        """Validate that file paths have .json extension and exist on disk.

        Only ``--functions_definition`` and ``--input`` are checked for existence
        since the output file is created at runtime.

        Raises:
            ValueError: If a file is not .json or does not exist.
        """
        must_exist = ["--functions_definition", "--input"]

        for k, v in self.files.items():
            file_path = Path(v)
            if file_path.suffix != '.json':
                raise ValueError(f"'{v}' is not a .json file.")
            if k in must_exist and not file_path.is_file():
                    raise ValueError(f"'{v}' unknown file.")
