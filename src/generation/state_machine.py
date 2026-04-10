from llm_sdk.llm_sdk import Small_LLM_Model
from .state import State
from .vocabulary import Vocabulary
from ..models.models_json_files import FunctionSchema, PromptSchema
from .number_parser import NumberParser
from .string_parser import StringParser
from typing import Any


class StateMachine():
    def __init__(self, llm: Small_LLM_Model,
                 prompt: PromptSchema,
                 functions: list[FunctionSchema]):
        self.llm = llm
        self.state = State.START
        self.vocab = Vocabulary(self.llm)
        self.num_parser = NumberParser(self.vocab)
        self.str_parser = StringParser(self.vocab)
        self.token_to_force: list[int] = []
        self.prompt = prompt
        self.functions = functions

        self.result: dict[str, Any] = {
            "prompt": self.prompt.prompt,
            "name": "",
            "parameters": {}
        }

        # tokenise the functions
        self.fn_token = self.tokenized_fn()
        # all the fn are candidates by default
        self.candidates = self.functions
        self.fn_pos = 0
        self.chosen_fn: FunctionSchema = self.functions[0]

        self.param_type: str = ""
        self.current_param: str = ""
        self.params_todo: list = []
        self.parameters_done: list = []

    def force_tokens(self, tokens_to_force: str) -> list[int]:
        return self.llm.encode(tokens_to_force).tolist()[0]

    def transition(self, token: str) -> None:
        if self.state == State.START:
            self.state = State.VALUE_FUNC_NAME

        elif self.state == State.VALUE_FUNC_NAME:
            self.state_value_func_name(token)

        elif self.state == State.PARAMETERS:
            self.param_type = self.chosen_fn.parameters[
                self.current_param].type
            self.state = self.get_state_for_types()

        elif self.state == State.VALUE_PARAM_NUMBER:
            done = self.num_parser.transition(token)
            if done:
                self.setup_next_param_or_end()

        elif self.state == State.VALUE_PARAM_STR:
            done = self.str_parser.transition(token)
            if done:
                self.setup_next_param_or_end()

        else:
            pass

    def get_valid_ids(self) -> list[int] | None:
        if self.state == State.VALUE_FUNC_NAME:
            valid_ids = set()
            for fn in self.candidates:
                valid_ids.add(self.fn_token[fn.name][self.fn_pos])
            return self.vocab.get_ids_for(list(valid_ids))

        elif self.state == State.VALUE_PARAM_NUMBER:
            return self.num_parser.get_valid_ids()

        return None

    def is_it_the_end(self) -> bool:
        if self.state == State.END:
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

    def get_state_for_types(self) -> State:
        match self.param_type:
            case "number":
                return State.VALUE_PARAM_NUMBER
            case "string":
                return State.VALUE_PARAM_STR
            case "boolean":
                return State.VALUE_PARAM_BOOL
            case "integer":
                return State.VALUE_PARAM_NUMBER
        return State.VALUE_PARAM_STR

    def state_value_func_name(self, token: str) -> None:
        self.candidates = [
            fn for fn in self.candidates
            if self.fn_token[fn.name][self.fn_pos] == token]
        self.fn_pos += 1

        if len(self.candidates) == 1:
            if self.fn_pos == len(self.fn_token[self.candidates[0].name]):
                self.chosen_fn = self.candidates[0]
                self.result["name"] = self.chosen_fn.name
                self.params_todo = list(self.chosen_fn.parameters.keys())
                self.current_param = self.params_todo.pop(0)
                self.state = State.PARAMETERS

    def setup_next_param_or_end(self) -> None:
        match self.param_type:
            case "number":
                self.result["parameters"][self.current_param] = float(
                    self.num_parser.result)
            case "integer":
                self.result["parameters"][self.current_param] = int(float(
                    self.num_parser.result))
            case "string":
                self.result["parameters"][self.current_param] = (
                    self.str_parser.result)

        self.num_parser.result = ""

        if len(self.params_todo) > 0:
            self.num_parser.reset()
            self.str_parser.reset()
            self.current_param = self.params_todo.pop(0)
            self.param_type = self.chosen_fn.parameters[
                self.current_param].type
            self.state = self.get_state_for_types()

        else:
            self.state = State.END
