from llm_sdk.llm_sdk import Small_LLM_Model
from ..models.models_json_files import FunctionSchema, PromptSchema
from .state_machine import StateMachine
# import json


class Generator:
    def __init__(self, llm: Small_LLM_Model,
                 functions: list[FunctionSchema]):
        self.llm = llm
        self.functions = functions

    def _build_prompt(self, user_request: PromptSchema) -> str:
        result = ""
        for fn in self.functions:
            result += f"-{fn.name}: {fn.description}"
        # print(result)
        return f"""You are a function calling assistant.
        Given a user request, select the correct function name.
        Available functions:
        {result}

        User requests: {user_request}
        Function name:"""

    def _filter_logits(self, logits: list[float],
                       valid_ids: list[int]) -> list[float]:
        for i in range(len(logits)):
            if i not in valid_ids:
                logits[i] = float("-inf")

        return logits

    def generate(self, prompt: PromptSchema) -> None:
        clean_prompt = '"' + prompt.prompt + '"'

        self.state_machine = StateMachine(self.llm,
                                          clean_prompt,
                                          self.functions)

        self.state_machine.tokenized_fn()

        answer = []
        full_prompt = self._build_prompt(prompt)
        prompt_ids = self.llm.encode(full_prompt).tolist()[0]

        while not self.state_machine.is_done():
            # 4. Récupère les logits pour le prochain token
            logits = self.llm.get_logits_from_input_ids(prompt_ids)

            # 5. Demande à la machine quels tokens sont valides
            valid_ids = self.state_machine.get_valid_ids()

            # 6. Filtre les logits
            logits = self._filter_logits(logits, valid_ids)

            # 7. Choisit le meilleur token
            next_token = logits.index(max(logits))

            # 8. Ajoute le token à la séquence
            prompt_ids.append(next_token)
            answer.append(next_token)

            # 9. Dis à la machine quel token a été généré
            print(self.llm.decode([next_token]), end="", flush=True)
            self.state_machine.transition(self.llm.decode([next_token]))

        # 10. Reconstruit le JSON généré
        # print("ANSWER:", self.llm.decode(answer), "\n")
        # print(json.loads(self.llm.decode(answer)))
