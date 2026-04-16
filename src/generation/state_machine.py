import ast
from typing import Any

from llm_sdk.llm_sdk import Small_LLM_Model

from ..models.models_class import StateMachineModel
from ..models.models_json_files import FunctionSchema, PromptSchema
from .array_parser import ArrayParser
from .number_parser import NumberParser
from .state import State
from .string_parser import StringParser
from .vocabulary import Vocabulary


class StateMachine():
    def __init__(self, llm: Small_LLM_Model,
                 prompt: PromptSchema,
                 functions: list[FunctionSchema]):

        StateMachineModel(
            llm=llm,
            prompt=prompt,
            functions=functions
        )

        self.llm: Small_LLM_Model = llm
        self.state: State = State.START
        self.vocab: Vocabulary = Vocabulary(self.llm)
        self.num_parser: NumberParser = NumberParser(self.vocab)
        self.str_parser: StringParser = StringParser(self.vocab)
        self.array_parser: ArrayParser = ArrayParser(self.vocab)
        self.token_to_force: list[int] = []
        self.prompt: PromptSchema = prompt
        self.functions: list[FunctionSchema] = functions

        self.result: dict[str, Any] = {
            "prompt": self.prompt.prompt,
            "name": "",
            "parameters": {}
        }

        self.fn_token: dict[str, list[str]] = self._tokenized_fn()
        print(self.fn_token)
        self.candidates: list[FunctionSchema] = self.functions
        self.fn_pos: int = 0
        self.chosen_fn: FunctionSchema = self.functions[0]

        self.param_type: str = ""
        self.curr_param: str = ""
        self.params_todo: list[str] = []
        self.params_done: dict[str, str] = {}

    def transition(self, token: str) -> None:
        if self.state == State.START:
            self.state = State.VALUE_FUNC_NAME

        elif self.state == State.VALUE_FUNC_NAME:
            self._state_value_func_name(token)

        elif self.state == State.VALUE_PARAM_NUMBER:
            done = self.num_parser.transition(token)
            if done:
                self._setup_next_param_or_end()

        elif self.state == State.VALUE_PARAM_STR:
            done = self.str_parser.transition(token)
            if done:
                self._setup_next_param_or_end()

        elif self.state == State.VALUE_PARAM_ARRAY:
            done = self.array_parser.transition(token)
            if done:
                self._setup_next_param_or_end()

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

        elif self.state == State.VALUE_PARAM_STR:
            return self.str_parser.get_valid_ids()

        elif self.state == State.VALUE_PARAM_ARRAY:
            return self.array_parser.get_valid_ids()

        return None

    def is_it_the_end(self) -> bool:
        if self.state == State.END:
            return True
        else:
            return False

    def _tokenized_fn(self) -> dict[str, list[str]]:
        tokenized: dict[str, list[str]] = {}
        for fn in self.functions:
            ids = self.llm.encode(fn.name).tolist()[0]
            tokenized[fn.name] = []
            for id in ids:
                tokenized[fn.name].append(self.llm.decode(id))
        return tokenized

    def _get_state_for_types(self) -> None:
        match self.param_type:
            case "number":
                self.state = State.VALUE_PARAM_NUMBER
            case "integer":
                self.state = State.VALUE_PARAM_NUMBER
            case "string":
                self.state = State.VALUE_PARAM_STR
            case "boolean":
                self.state = State.VALUE_PARAM_STR
            case "array":
                self.state = State.VALUE_PARAM_ARRAY

    def _state_value_func_name(self, token: str) -> None:
        self.candidates = [
            fn for fn in self.candidates
            if self.fn_token[fn.name][self.fn_pos] == token]
        self.fn_pos += 1

        if len(self.candidates) == 1:
            if self.fn_pos == len(self.fn_token[self.candidates[0].name]):
                self.chosen_fn = self.candidates[0]
                self.result["name"] = self.chosen_fn.name
                self.params_todo = list(self.chosen_fn.parameters.keys())
                self.curr_param = self.params_todo.pop(0)
                self.param_type = self.chosen_fn.parameters[
                    self.curr_param].type
                self._get_state_for_types()

    def _setup_next_param_or_end(self) -> None:
        match self.param_type:
            case "number":
                result = self.num_parser.result
                self.result["parameters"][self.curr_param] = float(result)
            case "integer":
                result = self.num_parser.result
                self.result["parameters"][self.curr_param] = int(float(
                    result))
            case "string":
                result = self.str_parser.result
                self.result["parameters"][self.curr_param] = (
                    result.strip())
            case "array":
                result = self.array_parser.result
                self.result["parameters"][self.curr_param] = ast.literal_eval(
                    result)
            case "boolean":
                result = self.str_parser.result
                self.result["parameters"][self.curr_param] = (
                    result.strip())

        # print(self.result)
        self.params_done[self.curr_param] = result

        if len(self.params_todo) > 0:
            self.num_parser.reset()
            self.str_parser.reset()
            self.array_parser.reset()

            self.curr_param = self.params_todo.pop(0)
            self.param_type = self.chosen_fn.parameters[
                self.curr_param].type
            self._get_state_for_types()

        else:
            self.state = State.END
