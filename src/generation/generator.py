from typing import Any

import numpy as np
from numpy.typing import NDArray

from llm_sdk.llm_sdk import Small_LLM_Model

from ..models.models_class import GeneratorModel
from ..models.models_json_files import FunctionSchema, PromptSchema
from .state import State
from .state_machine import StateMachine
from .vocabulary import Vocabulary


class Generator:
    """Orchestrates the constrained decoding loop
      for function-calling generation.

    Manages prompt construction, logit filtering, and state machine transitions
    to produce structured JSON output token by token.

    Attributes:
        token_count: Running total of tokens generated,
          used for performance tracking.
        llm: The language model instance.
        functions: List of available function schemas.
        vocab: Vocabulary instance for token filtering.
        output: Path to the output file.
        final_result: Accumulated list of generation
          results across all prompts.
        fn_list: Formatted string listing available
          function names for the prompt.
    """

    def __init__(self, llm: Small_LLM_Model,
                 functions: list[FunctionSchema],
                 output: str, token_count: int | None):
        """Initialize Generator and validate inputs.

        Args:
            llm: The language model instance.
            functions: List of available function schemas.
            output: Path to the output file.
            token_count: Optional initial token count for performance tracking.
        """
        GeneratorModel(
            llm=llm,
            functions=functions,
            output=output,
            token_count=token_count)

        self.token_count = token_count
        self.llm = llm
        self.functions = functions
        self.vocab = Vocabulary(self.llm)
        self.output = output
        self.final_result: list[dict[str, Any]] = []
        self.fn_list = "\n".join([
            f"- {fn.name}"
            for fn in self.functions
        ])

    def _build_function_prompt(self, user_request: PromptSchema) -> str:
        """Build the prompt used during function name generation.

        Args:
            user_request: The user prompt being processed.

        Returns:
            Formatted prompt string with system context and function list.
        """
        return (
            "<|im_start|>system\n"
            "Function calling-assistant.\n"
            f"{self.fn_list}.\n"
            "<|im_end|>\n"

            "<|im_start|>user\n"
            f"{user_request}\n"
            "<|im_end|>\n"

            "<|im_start|>assistant\n"
        )

    def _build_parameters_prompt(self, user_request: PromptSchema) -> str:
        """Build the prompt used during string parameter generation.

        Provides the LLM with the chosen function
          signature and already-generated
        parameters to guide the generation
          of the current parameter value.

        Args:
            user_request: The user prompt being processed.

        Returns:
            Formatted prompt string with function
              context and partial parameters.
        """
        fn = self.state_machine.chosen_fn
        param = self.state_machine.curr_param
        param_done_str = ", ".join([
            f'{k}="{v}"' for k, v in self.state_machine.params_done.items()
        ])
        arg_context = ""
        for k, v in fn.parameters.items():
            arg_context += f"argument_name={k} type={v.type}"
        return (
            "<|im_start|>system\n"
            "Extract intact argument from request\n"
            f"Function name={fn.name}\n"
            f"Request={user_request}\n"
            f"Arguments={arg_context}\n"
            "<|im_end|>"

            "<|im_start|>assistant\n" \
            f"{param}={self.state_machine.str_parser.result}"
        )

    def _filter_logits(self, logits: list[float],
                       valid_ids: list[int]) -> NDArray[np.float64]:
        """Apply a mask to logits, setting invalid token scores to -inf.

        Args:
            logits: Raw logit scores for the full vocabulary.
            valid_ids: List of token ids that are allowed in the current state.

        Returns:
            Masked logit array where invalid tokens are set to -inf.
        """
        np_logits = np.array(logits)
        mask = np.full(len(np_logits), float("-inf"))
        mask[valid_ids] = np_logits[valid_ids]
        return mask

    def _get_prompt(self, answer: str, user_request: PromptSchema) -> Any:
        """Re-encode the full prompt and answer into input ids.

        Uses a specialized parameters prompt during string generation,
        and the standard function prompt otherwise.

        Args:
            answer: The tokens generated so far in the current generation loop.
            user_request: The user prompt being processed.

        Returns:
            List of token ids to pass to the LLM on the next step.
        """
        if self.state_machine.state == State.VALUE_PARAM_STR:
            new_input = self._build_parameters_prompt(user_request)
            input_ids = self.llm.encode(new_input).tolist()[0]
        else:
            new_input = self._build_function_prompt(user_request) + answer
            input_ids = self.llm.encode(new_input).tolist()[0]

        print(new_input)
        return input_ids

    def generate(self, prompt: PromptSchema) -> int | None:
        """Run the constrained decoding loop for a single prompt.

        Iterates token by token, applying FSM constraints at each step.
        Skips the LLM forward pass when only
          one valid token exists (jump-forward).
        Appends the result to final_result upon completion.

        Args:
            prompt: The user prompt to process.

        Returns:
            Updated token count after generation,
              or None if token_count was None.
        """
        self.state_machine = StateMachine(self.llm,
                                          prompt,
                                          self.functions)

        answer = ""

        print(prompt.prompt, "\n")
        full_prompt = self._build_function_prompt(prompt)
        input_ids = self.llm.encode(full_prompt).tolist()[0]

        while not self.state_machine.is_it_the_end():
            # get the valid_ids
            valid_ids = self.state_machine.get_valid_ids()

            if valid_ids is None:
                self.state_machine.transition("")
                continue
            elif len(valid_ids) == 1:
                next_token = valid_ids[0]
            else:
                # get the logits from the input_ids
                logits = self.llm.get_logits_from_input_ids(input_ids)
                # filter the logits to -inf
                np_logits = self._filter_logits(logits, valid_ids)
                # get the next token and decode it
                next_token = int(np.argmax(np_logits))

            # decode the next_token
            token_decoded = (self.vocab.vocab_inv.get(next_token)
                             or self.llm.decode([next_token]))

            if isinstance(self.token_count, int):
                self.token_count += 1

            # transition the state_machine and print the token
            self.state_machine.transition(token_decoded)
            print(token_decoded, end="", flush=True)

            # add the token to the answer and get the next prompt
            answer += token_decoded
            input_ids = self._get_prompt(answer, prompt)

        print("\n\nGenerated JSON:\n", self.state_machine.result, "\n\n\n")

        # append the result of the current prompt to the final result
        self.final_result.append(self.state_machine.result)
        return self.token_count
