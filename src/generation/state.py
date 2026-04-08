from enum import Enum, auto


class State(Enum):
    START = auto()  # {
    KEY_PROMPT = auto()  # "prompt":
    VALUE_PROMPT = auto()  # the prompt used
    KEY_FUNC_NAME = auto()  # "name":
    VALUE_FUNC_NAME = auto()  # the function name
    KEY_PARAMETERS = auto()  # "parameters":
    KEY_PARAM = auto()  # force "param_name"
    VALUE_PARAM_NUMBER = auto()  # a number
    VALUE_PARAM_STR = auto()  # a str
    NEXT_PARAM = auto()  # force , or } depending on the params left
    CLOSE_PARAMETERS = auto()  # }
    END = auto()  # }
    DONE = auto()
