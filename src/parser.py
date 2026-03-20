from pathlib import Path


class Parser():
    def __init__(self, args: list[str]) -> None:
        self.args = args
        self.files = {
            "--functions_definition": "data/input/functions_definition.json",
            "--input": "data/input/function_calling_tests.json",
            "--output": "data/output/function_calls.json"
        }
        self.parse_args()
        self.validates_files()

    def parse_args(self) -> None:
        arguments = {"--functions_definition": 0,
                     "--input": 0,
                     "--output": 0}

        for i, arg in enumerate(self.args):
            if arg.startswith('--'):
                if arg in arguments and arguments[arg] == 0:
                    self.files[arg] = self.args[i + 1]
                    arguments[arg] += 1
                elif arg in arguments and arguments[arg] > 0:
                    raise ValueError(f"arguments '{arg}' found twice.")
                elif arg not in arguments:
                    raise ValueError(f"'{arg}' not a valid argument.")

        print("\n", self.files)

    def validates_files(self) -> None:
        arguments = ["--functions_definition", "--input"]

        for k, v in self.files.items():
            file_path = Path(v)
            if file_path.suffix != '.json':
                raise ValueError(f"'{v}' is not a .json file.")
            if k in arguments:
                if not file_path.is_file():
                    raise ValueError(f"'{v}' unknown file.")
