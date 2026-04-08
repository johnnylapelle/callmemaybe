from llm_sdk.llm_sdk import Small_LLM_Model
from .state import State
from .vocabulary import Vocabulary
from ..models.models_json_files import FunctionSchema
from typing import Any


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
        self.fn_token = self.tokenized_fn()
        self.candidates = self.functions
        self.fn_pos = 0
        self.chosen_fn: FunctionSchema = self.functions[0]
        self.params_todo: list = []
        self.parameters_done: list = []
        self.token_count = 0
        self.force_close = False

    def force_tokens(self, tokens_to_force: str) -> list[int]:
        return self.llm.encode(tokens_to_force).tolist()[0]

    def transition(self, token: str) -> None:
        if self.state == State.START:
            self.token_to_force = self.force_tokens('"prompt":')
            self.state = State.KEY_PROMPT

        elif self.state == State.KEY_PROMPT:
            self.token_to_force.pop(0)
            if len(self.token_to_force) == 0:
                self.token_to_force = self.force_tokens(self.prompt)
                self.state = State.VALUE_PROMPT

        elif self.state == State.VALUE_PROMPT:
            self.token_to_force.pop(0)
            if len(self.token_to_force) == 0:
                self.token_to_force = self.force_tokens(',"name":"')
                self.state = State.KEY_FUNC_NAME

        elif self.state == State.KEY_FUNC_NAME:
            self.token_to_force.pop(0)
            if len(self.token_to_force) == 0:
                self.state = State.VALUE_FUNC_NAME

        elif self.state == State.VALUE_FUNC_NAME:
            self.candidates = [fn for fn in self.candidates
                               if self.fn_token[fn.name][self.fn_pos] == token]
            self.fn_pos += 1
            if len(self.candidates) == 1:
                if self.fn_pos == len(self.fn_token[self.candidates[0].name]):
                    self.chosen_fn = self.candidates[0]
                    self.params_todo = list(self.chosen_fn.parameters.keys())
                    self.token_to_force = self.force_tokens('","parameters":{')
                    self.state = State.KEY_PARAMETERS

        elif self.state == State.KEY_PARAMETERS:
            self.token_to_force.pop(0)
            if len(self.token_to_force) == 0:
                self.current_param = self.params_todo.pop(0)
                self.token_to_force = self.force_tokens(
                    f'"{self.current_param}":"')
                self.state = State.KEY_PARAM

        elif self.state == State.KEY_PARAM:
            self.token_to_force.pop(0)
            if len(self.token_to_force) == 0:
                param_type = self.chosen_fn.parameters[self.current_param].type
                if param_type == "number":
                    self.state = State.VALUE_PARAM_NUMBER
                elif param_type == "string":
                    self.state = State.VALUE_PARAM_STR

        elif self.state == State.VALUE_PARAM_NUMBER:
            self.token_count += 1
            if token == '"':
                self.token_count = 0
                self.state = State.CLOSE_PARAMETERS
            if self.token_count > 20:
                self.force_close = True
                self.token_count = 0
                self.state = State.CLOSE_PARAMETERS

        elif self.state == State.VALUE_PARAM_STR:
            self.token_count += 1
            if token == '"':
                self.token_count = 0
                self.state = State.CLOSE_PARAMETERS
            if self.token_count > 20:
                self.force_close = True
                self.token_count = 0
                self.state = State.CLOSE_PARAMETERS

        elif self.state == State.CLOSE_PARAMETERS:
            if len(self.params_todo) > 0:
                self.current_param = self.params_todo.pop(0)
                self.token_to_force = self.force_tokens(
                    f'"{self.current_param}":"')
                self.state = State.KEY_PARAM
            else:
                self.state = State.END

        elif self.state == State.END:
            self.state = State.DONE

    def get_valid_ids(self) -> list[int]:
        if self.state == State.START:
            return [self.vocab.get_id('{')]

        elif self.state == State.KEY_PROMPT:
            return [self.token_to_force[0]]

        elif self.state == State.VALUE_PROMPT:
            return [self.token_to_force[0]]

        elif self.state == State.KEY_FUNC_NAME:
            return [self.token_to_force[0]]

        elif self.state == State.VALUE_FUNC_NAME:
            valid_tokens = set(
                self.fn_token[fn.name][self.fn_pos]
                for fn in self.candidates
            )
            return self.vocab.get_ids_for(list(valid_tokens))

        elif self.state == State.KEY_PARAMETERS:
            return [self.token_to_force[0]]

        elif self.state == State.KEY_PARAM:
            return [self.token_to_force[0]]

        elif self.state == State.VALUE_PARAM_NUMBER:
            return self.vocab.get_ids_for(["1", "2", "3",
                                           "4", "5", "6",
                                           "7", "8", "9", "0",
                                           "-", ".", '"'])

        elif self.state == State.VALUE_PARAM_STR:
            valid_tokens_2: list[Any] = [
                id for token, id in self.vocab.vocab.items()
                if '"' not in token or token == '"']
            return valid_tokens_2

        elif self.state == State.CLOSE_PARAMETERS:
            if len(self.params_todo) > 0:
                return [self.vocab.get_id(',')]
            return [self.vocab.get_id('}')]

        else:
            return [self.vocab.get_id('}')]

    def is_done(self) -> bool:
        if self.state == State.DONE:
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
