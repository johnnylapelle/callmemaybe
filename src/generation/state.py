from enum import Enum, auto


class State(Enum):
    START = auto()  # start
    VALUE_FUNC_NAME = auto()  # the function name
    VALUE_PARAM_NUMBER = auto()  # param if its a number
    VALUE_PARAM_STR = auto()  # param if its a str
    VALUE_PARAM_BOOL = auto()  # param if its a str
    END = auto()  # end


class StateNum(Enum):
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
    QUOTE = auto()
    CHARACTERS = auto()
    ESCAPE = auto()
    END = auto()
