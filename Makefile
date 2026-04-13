F_DEF = --functions_definition data/input/functions_definition.json
INPUT = --input data/input/function_calling_tests.json
OUTPUT = --output data/output/test.json
ARGS = $(F_DEF) $(INPUT) $(OUTPUT)

FLAKE8 = flake8
MYPY = mypy

install:
	uv pip install pydandic
	uv pip install torch

run:
	uv run --env-file .env python -m src

lint:
	$(FLAKE8) src/
	$(MYPY) src/ --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(FLAKE8) src/
	$(MYPY) --strict src/

clean:
	rm -rf .mypy_cache
	rm -rf .vscode
	find . -type d -name "__pycache__" -exec rm -rf {} +
