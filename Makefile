EXE = uv run python src/
FILE = parser.py

F_DEF = --functions_definition data/input/functions_definition.json
INPUT = --input data/input/function_calling_tests.json
OUTPUT = --output data/output/test.json
ARGS = $(F_DEF) $(INPUT) $(OUTPUT)

run:
	$(EXE)$(FILE) $(ARGS)
