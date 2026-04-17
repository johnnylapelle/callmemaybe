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
    def __init__(self, llm: Small_LLM_Model,
                 functions: list[FunctionSchema],
                 output: str):

        GeneratorModel(
            llm=llm,
            functions=functions,
            output=output)

        self.llm = llm
        self.functions = functions
        self.vocab = Vocabulary(self.llm)
        self.output = output
        self.final_result: list[dict[str, Any]] = []

    def _build_function_prompt(self, user_request: PromptSchema) -> str:
        fn_list = "\n".join([
            f"- {fn.name}: {fn.description}"
            for fn in self.functions
        ])
        return (
           "<|im_start|>system"
            "You are function-calling assistant.\n"
            "You must choose the right function and extract"
            " its parameters from the user request.\n"
            "List of the functions and their description:\n"
            f"{fn_list}.\n"
           "<|im_end|>system"

           "<|im_start|>assistant"
        )

    def _build_parameters_prompt(self, user_request: PromptSchema) -> str:
        fn = self.state_machine.chosen_fn
        param = self.state_machine.curr_param
        param_done_str = ", ".join([
            f'{k}="{v}"' for k, v in self.state_machine.params_done.items()
        ])
        fn_list = "\n".join([
            f"- {fn.name}: {fn.description}"
            for fn in self.functions
        ])
        return (
            "You are function-calling assistant.\n"
            "You must choose the rigth function and extract"
            " its parameters from the user request."
            "List of the functions and their description:\n"
            f"{fn_list}.\n"
            f"{fn.name} ({param_done_str} {param}=\""
            f"{self.state_machine.str_parser.result}"
        )

    def _filter_logits(self, logits: list[float],
                       valid_ids: list[int]) -> NDArray[np.float64]:

        np_logits = np.array(logits)
        mask = np.full(len(np_logits), float("-inf"))
        mask[valid_ids] = np_logits[valid_ids]
        return mask

    def _get_prompt(self, answer: str, user_request: PromptSchema) -> Any:
        if self.state_machine.state == State.VALUE_PARAM_STR:
            new_input = self._build_parameters_prompt(user_request)
            input_ids = self.llm.encode(new_input).tolist()[0]
        else:
            new_input = self._build_function_prompt(user_request) + answer
            input_ids = self.llm.encode(new_input).tolist()[0]

        print(f"\n{new_input}")
        return input_ids

    def generate(self, prompt: PromptSchema) -> None:
        self.state_machine = StateMachine(self.llm,
                                          prompt,
                                          self.functions)

        answer = ""

        print(prompt.prompt, "\n")
        full_prompt = self._build_function_prompt(prompt)
        input_ids = self.llm.encode(full_prompt).tolist()[0]

        while not self.state_machine.is_it_the_end():
            # get the logits from the input_ids
            logits = self.llm.get_logits_from_input_ids(input_ids)

            # get the valid_ids
            valid_ids = self.state_machine.get_valid_ids()

            if valid_ids is None:
                self.state_machine.transition("")
                continue

            # filter the logits to -inf
            np_logits = self._filter_logits(logits, valid_ids)

            # get the next token and decode it
            next_token = int(np.argmax(np_logits))
            token_decoded = self.llm.decode([next_token])

            # transition the state_machine and print the token
            self.state_machine.transition(token_decoded)
            print(token_decoded, end="", flush=True)

            # add the token to the answer and get the next prompt
            answer += token_decoded
            input_ids = self._get_prompt(answer, prompt)

        print("\n\nGenerated JSON:\n", self.state_machine.result, "\n\n\n")

        # append the result of the current prompt to the final result
        self.final_result.append(self.state_machine.result)
