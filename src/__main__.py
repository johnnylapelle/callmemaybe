from .io.parser import Parser
from .io.reader import Reader
import sys


def main() -> None:
    try:
        args = sys.argv
        parser = Parser(args)
        reader = Reader(parser.files)
        reader.validate_schema()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
