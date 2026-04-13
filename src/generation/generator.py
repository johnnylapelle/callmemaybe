from llm_sdk.llm_sdk import Small_LLM_Model
from ..models.models_json_files import FunctionSchema, PromptSchema
from ..models.models_class import GeneratorModel
from .state_machine import StateMachine
import numpy as np
from numpy.typing import NDArray
from .vocabulary import Vocabulary
from typing import Any
from .state import State


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
        self.result: list[dict[str, Any]] = []

    def _build_prompt(self, user_request: PromptSchema) -> str:
        fn_list = "\n".join([
            f"- {fn.name}"
            for fn in self.functions
        ])
        return (
            "<|im_start|>system\n"
            "Select function. Match request.\n"
            f"\n{fn_list}\n"
            "<|im_end|>\n"

            "<|im_start|>user\n"
            f"{user_request.prompt}\n"
            "<|im_end|>\n"

            "<|im_start|>assistant\n"
        )

    def _filter_logits(self, logits: list[float],
                       valid_ids: list[int]) -> NDArray:
        np_logits = np.array(logits)
        mask = np.full(len(np_logits), float("-inf"))
        mask[valid_ids] = np_logits[valid_ids]
        return mask

    def generate(self, prompt: PromptSchema) -> None:
        self.state_machine = StateMachine(self.llm,
                                          prompt,
                                          self.functions)

        self.state_machine.tokenized_fn()

        answer = ""

        print(prompt)
        full_prompt = self._build_prompt(prompt)
        input_ids = self.llm.encode(full_prompt).tolist()[0]

        while not self.state_machine.is_it_the_end():
            logits = self.llm.get_logits_from_input_ids(input_ids)

            valid_ids = self.state_machine.get_valid_ids()

            if valid_ids is None:
                self.state_machine.transition("")
                continue

            np_logits = self._filter_logits(logits, valid_ids)

            next_token = int(np.argmax(np_logits))
            token_decoded = self.llm.decode([next_token])

            self.state_machine.transition(token_decoded)
            answer += token_decoded
            print(token_decoded, end="", flush=True)

            if self.state_machine.state == State.VALUE_PARAM_STR:
                fn = self.state_machine.chosen_fn
                param = self.state_machine.curr_param
                new_input = (full_prompt + f"{fn.name} ({param}=\"" +
                             self.state_machine.str_parser.result)
                input_ids = self.llm.encode(new_input).tolist()[0]
            else:
                new_input = full_prompt + answer
                input_ids = self.llm.encode(new_input).tolist()[0]

        print()
        print(self.state_machine.result)
        print()

        self.result.append(self.state_machine.result)
