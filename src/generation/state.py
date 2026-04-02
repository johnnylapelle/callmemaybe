from enum import Enum, auto


class State(Enum):
    START = auto()  # {
    KEY_PROMPT = auto()  # "prompt":
    VALUE_PROMPT = auto()  # the prompt used
    KEY_FUNC_NAME = auto()  # "name":
    VALUE_FUNC_NAME = auto()  # the function name
    KEY_PARAMETERS = auto()  # "paramaters":
    OPEN_PARAMETERS = auto()  # {
    COLON_PARAMETERS = auto()  # ,
    VALUE_PARAM_NUMBER = auto()  # a number
    VALUE_PARAM_STR = auto()  # a str
    CLOSE_PARAMTERS = auto()  # }
    END = auto()  # }
    DONE = auto()
