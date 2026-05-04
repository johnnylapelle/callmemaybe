UV = uv
FLAKE8 = flake8
MYPY = $(UV) run python -m mypy
FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
SRC = src

install:
	$(UV) sync

run: install
	$(UV) run python -m $(SRC) $(ARG)

debug: install
	$(UV) run python -m pdb $(SRC)/__main__.py

lint: install
	$(FLAKE8) $(SRC)
	$(MYPY) $(FLAGS) $(SRC)

lint-strict:
	$(FLAKE8) $(SRC)
	$(MYPY) --strict $(SRC)

clean:
	rm -rf .mypy_cache
	rm -rf .vscode
	find . -type d -name "__pycache__" -exec rm -rf {} +

.PHONY: install run debug clean lint lint-strict
