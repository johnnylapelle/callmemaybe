import sys
import time
import traceback

from pydantic import ValidationError

from llm_sdk.llm_sdk import Small_LLM_Model

from .generation.generator import Generator
from .io.parser import Parser
from .io.reader import Reader
from .io.writer import Writer


def performance(start_time: float, token_count: int, nb_prompt: int) -> None:
    """Print performance metrics for the generation run.

    Args:
        start_time: Timestamp from time.perf_counter()
          at the start of execution.
        token_count: Total number of tokens generated.
    """
    end_time = time.perf_counter()
    duration = end_time - start_time
    tps = token_count / duration if duration > 0 else 0
    avg_time = duration / nb_prompt if nb_prompt > 0 else 0

    print("\nPerformance:")
    print(f"Total time: {duration:.2f}s")
    print(f"Token generated: {token_count}")
    print(f"Speed: {tps:.2f} tokens/sec")
    print(f"Average time per prompt: {avg_time:.2f}sec")


def main() -> None:
    """Entry point for the call-me-maybe constrained decoding pipeline.

    Parses CLI arguments, loads prompts
      and function schemas, runs the
    constrained generation loop, writes results,
      and prints performance metrics.

    Raises:
        ValidationError: If any input data fails Pydantic schema validation.
        ValueError: If input files are invalid or missing required fields.
        Exception: For any other unexpected runtime error.
    """
    try:
        start_time = time.perf_counter()
        token_count = 0

        args = sys.argv

        # llm = Small_LLM_Model(model_name="Qwen/Qwen3-1.7B")
        parser = Parser(args)
        reader = Reader(parser.parameters)
        llm = Small_LLM_Model(model_name=parser.parameters["--model"])

        functions = reader.get_functions()
        prompts = reader.get_prompts()
        output_path = reader.get_output_path()

        generator = Generator(llm, functions, output_path)
        results = generator.final_result

        for i, prompt in enumerate(prompts):
            print(f"- PROMPT {i + 1}:")
            token_count += generator.generate(prompt)

        # valid the results and write them
        writer = Writer(results, output_path)
        writer.write()

        performance(start_time, token_count, i)

        print("\nGeneration done !")

    except ValidationError as e:
        tb = traceback.extract_tb(e.__traceback__)[-1]
        print(f"ValidationError: {e}")
        print(f"in {tb.filename}, line {tb.lineno} in {tb.name}")
    except ValueError as e:
        tb = traceback.extract_tb(e.__traceback__)[-1]
        print(f"ValueError: {e}")
        print(f"in {tb.filename}, line {tb.lineno} in {tb.name}")
    except OSError as e:
        print(f"OsError: {e}")
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)[-1]
        print(f"\nError: {e}")
        print(f"in {tb.filename}, line {tb.lineno} in {tb.name}")
        sys.exit(1)


if __name__ == "__main__":
    main()
