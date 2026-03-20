from .io.parser import Parser
from .io.reader import Reader
import sys
from llm_sdk.llm_sdk import Small_LLM_Model


def main() -> None:
    try:
        # args = sys.argv
        # parser = Parser(args)
        # reader = Reader(parser.files)
        # reader.validate_schema()
        llm = Small_LLM_Model()
        print(llm.get_path_to_vocab_file())
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
