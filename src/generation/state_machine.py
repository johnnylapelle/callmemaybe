from llm_sdk.llm_sdk import Small_LLM_Model
from .state import State
from .vocabulary import Vocabulary
from ..models.models_json_files import FunctionSchema
# from typing import Any


class StateMachine():
    def __init__(self, llm: Small_LLM_Model,
                 prompt: str,
                 functions: list[FunctionSchema]):
        self.llm = llm
        self.state = State.START
        self.vocab = Vocabulary(self.llm)
        self.token_to_force: list[int] = []
        self.prompt = prompt
        self.functions = functions

        self.result = {
            "name": "",
            "parameters": {}
        }

        self.fn_token = self.tokenized_fn()  # tokenise de functions
        # all the fn are candidates by default
        self.candidates = self.functions
        self.fn_pos = 0
        self.chosen_fn: FunctionSchema = self.functions[0]

        self.params_todo: list = []
        self.parameters_done: list = []

    def force_tokens(self, tokens_to_force: str) -> list[int]:
        return self.llm.encode(tokens_to_force).tolist()[0]

    def transition(self, token: str) -> None:
        if self.state == State.START:
            self.state = State.VALUE_FUNC_NAME
            # print(f"TransState = {self.state}")

        elif self.state == State.VALUE_FUNC_NAME:
            self.candidates = [
                fn for fn in self.candidates
                if self.fn_token[fn.name][self.fn_pos] == token]
            self.fn_pos += 1

            if len(self.candidates) == 1:
                if self.fn_pos == len(self.fn_token[self.candidates[0].name]):
                    self.chosen_fn = self.candidates[0]
                    self.result["name"] = self.chosen_fn.name
                    self.params_todo = list(self.chosen_fn.parameters.keys())
                    print(self.params_todo)
                    self.state = State.PARAMETERS

        elif self.state == State.PARAMETERS:
            self.sate = State.END

        elif self.state == State.VALUE_PARAM_NUMBER:
            pass

        elif self.state == State.VALUE_PARAM_STR:
            pass

        else:
            pass

    def get_valid_ids(self) -> list[int] | None:
        if self.state == State.VALUE_FUNC_NAME:
            valid_ids = set()
            for fn in self.candidates:
                valid_ids.add(self.fn_token[fn.name][self.fn_pos])
            # print("Returning  = State.VALUE_FUNC_NAME")
            return self.vocab.get_ids_for(list(valid_ids))

        # print("get_valid_ids = Returning None")
        return None

    def is_it_the_end(self) -> bool:
        if self.state == State.PARAMETERS:
            return True
        else:
            return False

    def tokenized_fn(self) -> dict[str, list[str]]:
        tokenized: dict[str, list[str]] = {}
        for fn in self.functions:
            ids = self.llm.encode(fn.name).tolist()[0]
            tokenized[fn.name] = []
            for id in ids:
                tokenized[fn.name].append(self.llm.decode(id))
        return tokenized
