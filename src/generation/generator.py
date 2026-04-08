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
        result = ""
        for fn in self.functions:
            params_info = ", ".join([
                    f"{name} ({param.type})"
                    for name, param in fn.parameters.items()])
            result += f"- {fn.name}: {fn.description}, {params_info}\n"
        return f"""You are a function calling assistant.
        Given a user request, select the correct function name.
        Available functions:
        {result}

        User requests: {user_request}
        Function name:"""

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
        full_prompt = self._build_prompt(prompt)
        # print(full_prompt)
        input_ids = self.llm.encode(full_prompt).tolist()[0]

        while not self.state_machine.is_done():
            # 4. Récupère les logits pour le prochain token
            logits = self.llm.get_logits_from_input_ids(input_ids)

            # 5. Demande à la machine quels tokens sont valides
            valid_ids = self.state_machine.get_valid_ids()

            # 6. Filtre les logits
            np_logits = self._filter_logits(logits, valid_ids)

            # 7. Choisit le meilleur token
            next_token = int(np.argmax(np_logits))
            # next_token = logits.index(max(np_logits))
            next_token_decoded = self.llm.decode([next_token])

            # 8. Dis à la machine quel token a été généré
            self.state_machine.transition(next_token_decoded)
            if self.state_machine.force_close:
                answer += next_token_decoded + '"'
                self.state_machine.force_close = False
                print(next_token_decoded + '"', end="", flush=True)
            else:
                answer += next_token_decoded
                print(next_token_decoded, end="", flush=True)

            # 9. Retokenise prompt + answer et ajoute le token à la séquence
            new_input = full_prompt + answer
            input_ids = self.llm.encode(new_input).tolist()[0]

        # 10. Reconstruit le JSON généré
        # print("ANSWER:", self.llm.decode(answer), "\n")
        # print(json.loads(self.llm.decode(answer)))
