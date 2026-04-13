from .io.parser import Parser
from .io.reader import Reader
import sys
from .generation.generator import Generator
from llm_sdk.llm_sdk import Small_LLM_Model
import json
from pydantic import ValidationError
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
        output = reader.get_output_path()
        generator = Generator(llm, functions, output)

        for prompt in prompts:
            generator.generate(prompt)

        # generator.generate(prompts[8])
        # generator.generate(prompts[9])
        # generator.generate(prompts[10])
        with open(output, 'w') as f:
            json.dump(generator.result, f, indent=4)

    except ValidationError as e:
        print(f"ValidationError: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
