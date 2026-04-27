import re

from ..models.models_class import TypeParserModel
from .state import StateStr
from .vocabulary import Vocabulary


class StringParser():
    """Parses string and boolean parameter values token by token using a FSM.

    Handles two generation modes: free string generation constrained to
    latin characters, and regex pattern generation constrained to simple
    alphanumeric patterns.

    Attributes:
        state: Current FSM state.
        vocab: Vocabulary instance used for token filtering.
        result: Accumulated generated string, excluding the opening quote.
        max_token: Maximum number of tokens before forcing END.
        char_count: Counter to enforce the maximum token limit.
        re_regex: Pre-compiled regex to
          filter vocabulary for regex-mode generation.
        re_chars: Pre-compiled regex to
          filter vocabulary for free string generation.
    """

    def __init__(self, vocab: Vocabulary):
        """Initialize StringParser and validate inputs.

        Pre-compiles vocabulary filter patterns at initialization
        to avoid recompilation on every get_valid_ids call.

        Args:
            vocab: Vocabulary instance used for token filtering.
        """
        TypeParserModel(
            vocab=vocab
        )

        self.state = StateStr.QUOTE
        self.vocab = vocab
        self.result = ""
        self.max_token = 30
        self.char_count = 0

        self.re_regex = re.compile(r'^[a-zA-Z0-9\\+\[\]]+$')
        self.re_chars = re.compile(r"^[a-zA-Z0-9\sĠ '.,!?;:()\-_+&{}$*\\/]+$")

    def transition(self, token: str, curr_param: str) -> bool:
        """Process a token and advance the FSM state.

        Args:
            token: The decoded token string to process.
            curr_param: The name of the current parameter, used to detect
                regex-mode generation.

        Returns:
            True if the string is complete, False otherwise.
        """

        if '"' not in token:
            self.result += token
            self.char_count += 1

        elif '"' in token:
            for letter in token:
                if letter == '"':
                    break
                self.result += letter

        if self.state == StateStr.QUOTE:
            if curr_param == "regex":
                self.state = StateStr.REGEX
            else:
                self.state = StateStr.CHARACTERS

        elif self.state == StateStr.CHARACTERS:
            if '"' in token or self.char_count >= self.max_token:
                self.state = StateStr.END

        elif self.state == StateStr.REGEX:
            if '"' in token or self.char_count >= self.max_token:
                self.state = StateStr.END
            if ']' in token:
                self.state = StateStr.END

        if self.state == StateStr.END:
            return True

        return False

    def get_valid_ids(self) -> list[int]:
        """Return the list of valid token ids for the current FSM state.

        Returns:
            List of valid token ids based on the current state and
            the active generation mode (free string or regex).
        """
        valid_ids: list[int] = []

        if self.state == StateStr.QUOTE:
            valid_ids = self.vocab.get_ids_for(['"'])

        elif self.state == StateStr.CHARACTERS:
            valid_ids = [id for token, id in self.vocab.vocab.items()
                         if self.re_chars.match(token) or '"' in token]

        elif self.state == StateStr.REGEX:
            valid_ids = [id for token, id in self.vocab.vocab.items()
                         if self.re_regex.match(token) or '"' in token]

        return valid_ids

    def reset(self) -> None:
        """Reset the parser to its initial state for reuse."""
        self.result = ""
        self.state = StateStr.QUOTE
        self.char_count = 0
