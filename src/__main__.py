import sys
import time

from pydantic import ValidationError

from llm_sdk.llm_sdk import Small_LLM_Model

from .generation.generator import Generator
from .io.parser import Parser
from .io.reader import Reader
from .io.writer import Writer


def performance(start_time: float, token_count: int) -> None:
    end_time = time.perf_counter()
    duration = end_time - start_time
    tps = token_count / duration if duration > 0 else 0

    print("Performance:")
    print(f"Total time: {duration:.2f}s")
    print(f"Token generated: {token_count}")
    print(f"Speed: {tps:2f} tokens/sec")


def main() -> None:
    try:
        start_time = time.perf_counter()
        token_count = 0

        args = sys.argv

        llm = Small_LLM_Model()
        parser = Parser(args)
        reader = Reader(parser.files)

        prompts = reader.get_prompts()
        functions = reader.get_functions()
        prompts = reader.get_prompts()
        output_path = reader.get_output_path()

        generator = Generator(llm, functions, output_path, token_count)
        results = generator.final_result

        for i, prompt in enumerate(prompts):
            print(f"- PROMPT {i + 1}:")
            result_token_count = generator.generate(prompt)

            if isinstance(result_token_count, int):
                token_count += result_token_count

        # valid the results and write them
        writer = Writer(results, output_path)
        writer.write()

        performance(start_time, token_count)

    except ValidationError as e:
        print(f"ValidationError: {e}")
    except ValueError as e:
        print(f"ValueError: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
