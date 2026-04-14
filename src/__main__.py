import sys

from pydantic import ValidationError

from llm_sdk.llm_sdk import Small_LLM_Model

from .generation.generator import Generator
from .io.parser import Parser
from .io.reader import Reader
from .io.writer import Writer


def main() -> None:
    try:
        args = sys.argv

        llm = Small_LLM_Model()
        parser = Parser(args)
        reader = Reader(parser.files)

        prompts = reader.get_prompts()
        functions = reader.get_functions()
        prompts = reader.get_prompts()
        output_path = reader.get_output_path()

        generator = Generator(llm, functions, output_path)
        results = generator.final_result

        for prompt in prompts:
            generator.generate(prompt)

        # generator.generate(prompts[8])
        # generator.generate(prompts[9])
        # generator.generate(prompts[10])

        # Valid the results and write them
        writer = Writer(results, output_path)
        writer.write()

    except ValidationError as e:
        print(f"ValidationError: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
