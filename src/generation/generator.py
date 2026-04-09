from llm_sdk.llm_sdk import Small_LLM_Model
from ..models.models_json_files import FunctionSchema, PromptSchema
from .state_machine import StateMachine
import numpy as np
from numpy.typing import NDArray
from .vocabulary import Vocabulary
# import json


class Generator:
    def __init__(self, llm: Small_LLM_Model,
                 functions: list[FunctionSchema]):
        self.llm = llm
        self.functions = functions
        self.vocab = Vocabulary(self.llm)

    def _build_prompt(self, user_request: PromptSchema) -> str:
        fn_list = "\n".join([
            f"- {fn.name}: {fn.description}"
            for fn in self.functions
        ])
        return (
            "<|im_start|>system\n"
            "Select function. Match request."
            f"\n{fn_list}\n"
            "<|im_end|>\n"
            "<|im_start|>user\n"
            f"{user_request}\n"
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
        clean_prompt = '"' + prompt.prompt + '"'

        self.state_machine = StateMachine(self.llm,
                                          clean_prompt,
                                          self.functions)

        self.state_machine.tokenized_fn()

        answer = ""
        print(prompt)
        full_prompt = self._build_prompt(prompt)
        input_ids = self.llm.encode(full_prompt).tolist()[0]

        while not self.state_machine.is_it_the_end():
            # print(f"GenState = {self.state_machine.state}")
            logits = self.llm.get_logits_from_input_ids(input_ids)

            valid_ids = self.state_machine.get_valid_ids()

            if valid_ids is None:
                self.state_machine.transition("")
                continue

            np_logits = self._filter_logits(logits, valid_ids)

            next_token = int(np.argmax(np_logits))
            next_token_decoded = self.llm.decode([next_token])

            self.state_machine.transition(next_token_decoded)
            answer += next_token_decoded
            print(next_token_decoded, end="", flush=True)

            new_input = full_prompt + answer
            input_ids = self.llm.encode(new_input).tolist()[0]

        # 10. Reconstruit le JSON généré
        print()
        print(self.state_machine.result)
        # print("ANSWER:", self.llm.decode(answer), "\n")
        # print(json.loads(self.llm.decode(answer)))
