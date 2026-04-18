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
    """Monitors and controls the full constrained generation process.

    Manages the function name resolution and delegates parameter generation
    to specialized sub-parsers (NumberParser, StringParser, ArrayParser).

    Attributes:
        llm: The language model instance.
        state: Current FSM state.
        vocab: Vocabulary instance shared across sub-parsers.
        num_parser: Parser for number and integer parameters.
        str_parser: Parser for string and boolean parameters.
        array_parser: Parser for array parameters.
        prompt: The user prompt being processed.
        functions: List of available function schemas.
        result: Dict accumulating the final generation output.
        fn_token: Pre-computed tokenization of each function name.
        candidates: Remaining function candidates during name resolution.
        fn_pos: Current token position in the function name resolution.
        chosen_fn: The resolved function schema after name generation.
        param_type: Type of the parameter currently being generated.
        curr_param: Name of the parameter currently being generated.
        params_todo: Remaining parameters to generate.
        params_done: Already generated parameters and their raw values.
    """
    def __init__(self, llm: Small_LLM_Model,
                 prompt: PromptSchema,
                 functions: list[FunctionSchema]):
        """Initialize StateMachine and validate inputs.

        Pre-computes function name tokenizations for efficient candidate filtering.

        Args:
            llm: The language model instance.
            prompt: The user prompt being processed.
            functions: List of available function schemas.
        """
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
        self.candidates: list[FunctionSchema] = self.functions
        self.fn_pos: int = 0
        self.chosen_fn: FunctionSchema = self.functions[0]

        self.param_type: str = ""
        self.curr_param: str = ""
        self.params_todo: list[str] = []
        self.params_done: dict[str, str] = {}

    def transition(self, token: str) -> None:
        """Process a token and advance the FSM state.

        Delegates to the appropriate sub-parser based on the current state.

        Args:
            token: The decoded token string to process.
        """
        if self.state == State.START:
            self.state = State.VALUE_FUNC_NAME

        elif self.state == State.VALUE_FUNC_NAME:
            self._state_value_func_name(token)

        elif self.state == State.VALUE_PARAM_NUMBER:
            done = self.num_parser.transition(token)
            if done:
                self._setup_next_param_or_end()

        elif self.state == State.VALUE_PARAM_STR:
            done = self.str_parser.transition(token, self.curr_param)
            if done:
                self._setup_next_param_or_end()

        elif self.state == State.VALUE_PARAM_ARRAY:
            done = self.array_parser.transition(token)
            if done:
                self._setup_next_param_or_end()

    def get_valid_ids(self) -> list[int] | None:
        """Return valid token ids for the current FSM state.

        Returns:
            List of valid token ids, or None if the current state
            requires no constraint (e.g. START).
        """
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
        """Check whether generation is complete.

        Returns:
            True if the FSM has reached the END state, False otherwise.
        """
        if self.state == State.END:
            return True
        else:
            return False

    def _tokenized_fn(self) -> dict[str, list[str]]:
        """Pre-compute the token-by-token decomposition of each function name.

        Called once at initialization to build an index used during
        candidate filtering in the VALUE_FUNC_NAME state.

        Returns:
            Dict mapping each function name to its list of decoded tokens.
        """
        tokenized: dict[str, list[str]] = {}
        for fn in self.functions:
            ids = self.llm.encode(fn.name).tolist()[0]
            tokenized[fn.name] = []
            for id in ids:
                tokenized[fn.name].append(self.llm.decode(id))
        return tokenized

    def _get_state_for_types(self) -> None:
        """Transition to the appropriate parameter state based on param_type."""
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
        """Narrow the function candidates based on the current token.

        Filters out functions whose tokenized name does not match the
        generated prefix, and transitions to parameter generation once
        a single candidate is fully resolved.

        Args:
            token: The decoded token string to match against candidates.
        """
        self.candidates = [
            fn for fn in self.candidates
            if self.fn_token[fn.name][self.fn_pos] == token]
        self.fn_pos += 1

        if len(self.candidates) == 1:
            if self.fn_pos == len(self.fn_token[self.candidates[0].name]):
                self.chosen_fn = self.candidates[0]
                self.result["name"] = self.chosen_fn.name
                self.params_todo = list(self.chosen_fn.parameters.keys())
                if self.params_todo:
                    self.curr_param = self.params_todo.pop(0)
                    self.param_type = self.chosen_fn.parameters[
                        self.curr_param].type
                    self._get_state_for_types()
                else:
                    self.state = State.END

    def _setup_next_param_or_end(self) -> None:
        """Store the current parameter result and set up the next one or end.

        Reads the result from the appropriate sub-parser, stores it in the
        result dict, then either transitions to the next parameter or moves
        to the END state.
        """
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
