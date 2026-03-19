import json
import sys
from pathlib import Path

class Parser():
	def __init__(self, args: list[str]) -> None:
		self.args = args
		self.files: dict[str, str] = {
			"--functions_definition": "data/input/functions_definition.json",
			"--input": "data/input/function_calling_tests.json",
			"--output": "data/output/function_calls.json"}

		self.parse_arguments()
		self.validate_files()

	def parse_arguments(self) -> None:
		known_arguments: list[str] = ["--functions_definition", "--input", "--output"]

		for i, arg in enumerate(self.args):
			if arg.startswith("--"):
				if arg not in known_arguments:
					raise ValueError(f"Unknown argument: '{arg}'")
				if i + 1 < len(self.args) and not self.args[i + 1].startswith("--"):
					self.files[arg] = self.args[i + 1]
				else:
					raise ValueError(f"Missing value for argument: '{arg}'")

		print(self.files)

	def validate_files(self) -> None:
		for value in self.files.values():
			file_path = Path(value)
			if file_path.suffix != '.json':
				raise ValueError(f"'{value}' is not a .json file")

		fn_def_path = Path(self.files['--functions_definition'])
		input_path = Path(self.files['--input'])
		if not fn_def_path.is_file() or not input_path.is_file():
				raise ValueError(f"{fn_def_path} doesn't exist.")
		if not input_path.is_file():
				raise ValueError(f"{input_path} doesn't exist.")


def main() -> None:
	try:
		args = sys.argv
		parser = Parser(args)
		print(parser.files)
	except Exception as e:
		print(f"Error: {e}", file=sys.stderr)
		sys.exit()


if __name__ == "__main__":
	main()
