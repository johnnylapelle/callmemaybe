FLAKE8 = flake8
MYPY = uv run python -m mypy
FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

install:
	uv sync

run: install
	uv run python -m src $(ARG)

debug: install
	uv run python -m pdb src/__main__.py

lint: install
	uv run python -m $(FLAKE8) src/
	uv run python -m $(MYPY) $(FLAGS) src/

lint-strict:
	uv run python -m $(FLAKE8) src/
	uv run python -m $(MYPY) --strict src/

clean:
	rm -rf .mypy_cache
	rm -rf .vscode
	find . -type d -name "__pycache__" -exec rm -rf {} +

.PHONY: install run debug clean lint lint-strict
