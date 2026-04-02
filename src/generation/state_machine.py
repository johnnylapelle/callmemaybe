from llm_sdk.llm_sdk import Small_LLM_Model
from .state import State
from .vocabulary import Vocabulary
from ..models.models_json_files import FunctionSchema


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
        # print(self.fn_token)
        self.candidates = self.functions
        self.fn_pos = 0

    def transition(self, token: str):
        if self.state == State.START:
            self.token_to_force = self.llm.encode('"prompt":').tolist()[0]
            self.state = State.KEY_PROMPT

        elif self.state == State.KEY_PROMPT:
            self.token_to_force.pop(0)
            if len(self.token_to_force) == 0:
                self.token_to_force = self.llm.encode(self.prompt).tolist()[0]
                self.state = State.VALUE_PROMPT

        elif self.state == State.VALUE_PROMPT:
            self.token_to_force.pop(0)
            if len(self.token_to_force) == 0:
                self.token_to_force = self.llm.encode(',"name":"').tolist()[0]
                self.state = State.KEY_FUNC_NAME

        elif self.state == State.KEY_FUNC_NAME:
            self.token_to_force.pop(0)
            if len(self.token_to_force) == 0:
                self.state = State.VALUE_FUNC_NAME

        elif self.state == State.VALUE_FUNC_NAME:
            self.candidates = [fn for fn in self.candidates
                               if self.fn_token[fn.name][self.fn_pos] == token]
            self.fn_pos += 1
            if self.fn_pos == len(self.fn_token[self.candidates[0].name]):
                self.token_to_force = self.llm.encode('","parameters":').tolist()[0]
                self.state = State.KEY_PARAMETERS

        elif self.state == State.KEY_PARAMETERS:
            self.token_to_force.pop(0)
            if len(self.token_to_force) == 0:
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
