from ..models.models_class import TypeParserModel
from .state import StateNum
from .vocabulary import Vocabulary


class NumberParser():
    """Parses numeric parameter values token by token using a FSM.

    Handles integers, floats, and scientific notation following the JSON
    number specification. Generation ends when a closing quote or comma
    is encountered.

    Attributes:
        state: Current FSM state.
        vocab: Vocabulary instance used for token filtering.
        result: Accumulated numeric string, excluding quotes and commas.
        digits_count: Counter to enforce the maximum digit limit.
        max_digits: Maximum number of digits allowed before forcing END.
    """

    def __init__(self, vocab: Vocabulary):
        """Initialize NumberParser and validate inputs.

        Args:
            vocab: Vocabulary instance used for token filtering.
        """
        TypeParserModel(
            vocab=vocab
        )

        self.state = StateNum.QUOTE
        self.vocab = vocab
        self.result = ""

        self.digits_count = 0
        self.max_digits = 10

    def transition(self, token: str) -> bool:
        """Process a token and advance the FSM state.

        Args:
            token: The decoded token string to process.

        Returns:
            True if the number is complete, False otherwise.
        """
        if token not in ',"':
            self.result += token

        if self.state == StateNum.QUOTE:
            self.state = StateNum.START

        elif self.state == StateNum.START:
            if token == "0":
                self.state = StateNum.AFTER_INT
            elif token in "-123456789":
                self.state = StateNum.DIGITS

        elif self.state == StateNum.DIGITS:
            self.digits_count += 1
            if token in '",':
                self.state = StateNum.END
            elif self.digits_count >= self.max_digits:
                self.digits_count = 0
                self.state = StateNum.END
            elif token == ".":
                self.state = StateNum.DECIMAL
            elif token in "Ee":
                self.state = StateNum.EXPONENT

        elif self.state == StateNum.AFTER_INT:
            if token in '",':
                self.state = StateNum.END
            elif token in "Ee":
                self.state = StateNum.EXPONENT
            else:
                self.state = StateNum.DECIMAL

        elif self.state == StateNum.DECIMAL:
            if token in '",':
                self.state = StateNum.END
            else:
                self.state = StateNum.DECIMAL_DIGITS

        elif self.state == StateNum.DECIMAL_DIGITS:
            if token in '",':
                self.state = StateNum.END
            elif token in "eE":
                self.state = StateNum.EXPONENT
            else:
                self.state = StateNum.DECIMAL_DIGITS

        elif self.state == StateNum.EXPONENT:
            if token in '",':
                self.state = StateNum.END
            elif token in "+-":
                self.state = StateNum.EXP_SIGN
            else:
                self.state = StateNum.EXP_DIGITS

        elif self.state == StateNum.EXP_SIGN:
            self.state = StateNum.EXP_DIGITS

        elif self.state == StateNum.EXP_DIGITS:
            if token in '",':
                self.state = StateNum.END
            else:
                self.state = StateNum.EXP_DIGITS

        if self.state == StateNum.END:
            return True

        return False

    def get_valid_ids(self) -> list[int]:
        """Return the list of valid token ids for the current FSM state.

        Returns:
            List of valid token ids based on the current state,
            following the JSON number specification.
        """
        valid_ids: list[int] = []

        if self.state == StateNum.QUOTE:
            valid_ids = self.vocab.get_ids_for(['"'])

        elif self.state == StateNum.START:
            valid_ids = self.vocab.get_ids_for([
                    '-', '0', '1', '2', '3', '4',
                    '5', '6', '7', '8', '9'])

        elif self.state == StateNum.DIGITS:
            valid_ids = self.vocab.get_ids_for([
                '0', '1', '2', '3', '4',
                '5', '6', '7', '8', '9',
                '.', 'e', 'E', '"'])

        elif self.state == StateNum.AFTER_INT:
            valid_ids = self.vocab.get_ids_for([
                '.', 'E', 'e', '"'
                ])

        elif self.state == StateNum.DECIMAL:
            valid_ids = self.vocab.get_ids_for([
                '0', '1', '2', '3', '4',
                '5', '6', '7', '8', '9',
                '"'])

        elif self.state == StateNum.DECIMAL_DIGITS:
            valid_ids = self.vocab.get_ids_for([
                '0', '1', '2', '3', '4',
                '5', '6', '7', '8', '9',
                'e', 'E', '"'])

        elif self.state == StateNum.EXPONENT:
            valid_ids = self.vocab.get_ids_for([
                '0', '1', '2', '3', '4',
                '5', '6', '7', '8', '9',
                'e', 'E', '"', '+', '-'])

        elif self.state == StateNum.EXP_SIGN:
            valid_ids = self.vocab.get_ids_for([
                '0', '1', '2', '3', '4',
                '5', '6', '7', '8', '9'
                ])

        elif self.state == StateNum.EXP_DIGITS:
            valid_ids = self.vocab.get_ids_for([
                '0', '1', '2', '3', '4',
                '5', '6', '7', '8', '9',
                '"'])

        return valid_ids

    def reset(self) -> None:
        """Reset the parser to its initial state for reuse."""
        self.result = ""
        self.state = StateNum.QUOTE
        self.digits_count = 0
