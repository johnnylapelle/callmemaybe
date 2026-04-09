from enum import Enum, auto


class State(Enum):
    START = auto()  # start
    VALUE_FUNC_NAME = auto()  # the function name
    PARAMETERS = auto()  # determine the type of the param
    VALUE_PARAM_NUMBER = auto()  # param if its a number
    VALUE_PARAM_STR = auto()  # param if its a str
    VALUE_PARAM_INT = auto()  # param if its a str
    VALUE_PARAM_BOOL = auto()  # param if its a str
    END = auto()  # end
