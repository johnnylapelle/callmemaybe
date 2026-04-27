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
	$(FLAKE8) src/
	$(MYPY) $(FLAGS) src/

lint-strict:
	$(FLAKE8) src/
	$(MYPY) --strict src/

clean:
	rm -rf .mypy_cache
	rm -rf .vscode
	find . -type d -name "__pycache__" -exec rm -rf {} +
