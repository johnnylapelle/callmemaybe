from .io.parser import Parser
from .io.reader import Reader
import sys
from .generation.generator import Generator
from llm_sdk.llm_sdk import Small_LLM_Model
# from .generation.state_machine import StateMachine


def main() -> None:
    try:
        args = sys.argv
        llm = Small_LLM_Model()
        parser = Parser(args)
        reader = Reader(parser.files)
        prompts = reader.get_prompts()
        functions = reader.get_functions()
        prompts = reader.get_prompts()
        generator = Generator(llm, functions)
        for prompt in prompts:
            generator.generate(prompt)
            print()
        # generator.generate(prompts[8])
        # print()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
