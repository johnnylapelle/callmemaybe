from .io.parser import Parser
from .io.reader import Reader
import sys
from .generation.state_machine import test_constrained_decoding


def main() -> None:
    try:
        args = sys.argv
        parser = Parser(args)
        reader = Reader(parser.files)
        reader.validate_schema()
        test_constrained_decoding()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
