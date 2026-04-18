from enum import Enum, auto


class State(Enum):
    """Top-level FSM states for the StateMachine.

    Tracks the global generation phase across function name
    resolution and parameter generation.
    """

    START = auto()
    VALUE_FUNC_NAME = auto()
    VALUE_PARAM_NUMBER = auto()
    VALUE_PARAM_STR = auto()
    VALUE_PARAM_ARRAY = auto()
    END = auto()


class StateNum(Enum):
    """FSM states for NumberParser.

    Follows the JSON number specification, handling integers,
    floats, and scientific notation.
    """

    QUOTE = auto()
    START = auto()
    DIGITS = auto()
    AFTER_INT = auto()
    DECIMAL = auto()
    DECIMAL_DIGITS = auto()
    EXPONENT = auto()
    EXP_DIGITS = auto()
    EXP_SIGN = auto()
    END = auto()


class StateStr(Enum):
    """FSM states for StringParser.

    Handles free string generation, regex patterns, and escape sequences.
    """

    QUOTE = auto()
    CHARACTERS = auto()
    REGEX = auto()
    ESCAPE = auto()
    END = auto()


class StateArray(Enum):
    """FSM states for ArrayParser.

    Handles array generation from opening bracket to closing bracket.
    """

    OPEN_BRAC = auto()
    GENERATION = auto()
    END = auto()
