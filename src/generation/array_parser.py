from ..models.models_class import TypeParserModel
from .state import StateArray
from .vocabulary import Vocabulary


class ArrayParser():
    """Parses array-type parameter values token by token using a FSM.

    Handles the generation of JSON array values by constraining the LLM
    to first emit an opening bracket, then generate content freely until
    a closing bracket is detected.

    Attributes:
        state: Current FSM state.
        vocab: Vocabulary instance used for token filtering.
        result: Accumulated generated string, excluding quote characters.
    """

    def __init__(self, vocab: Vocabulary):
        """Initialize ArrayParser and validate inputs.

        Args:
            vocab: Vocabulary instance used for token filtering.
        """
        TypeParserModel(
            vocab=vocab
        )

        self.state = StateArray.OPEN_BRAC
        self.vocab = vocab
        self.result = ""
        self.max_token = 30
        self.char_count = 0

    def transition(self, token: str) -> bool:
        """Process a token and advance the FSM state.

        Args:
            token: The decoded token string to process.

        Returns:
            True if the array is complete, False otherwise.
        """
        if ']' in token:
            for letter in token:
                if letter == ']':
                    self.result += ']'
                    break
                self.result += letter
        else:
            self.result += token
            self.char_count += 1

        if self.state == StateArray.OPEN_BRAC:
            self.state = StateArray.GENERATION

        elif self.state == StateArray.GENERATION:
            if "]" in token:
                self.state = StateArray.END
            elif self.char_count > self.max_token:
                self.result += ']'
                self.state = StateArray.END

        if self.state == StateArray.END:
            return True

        return False

    def get_valid_ids(self) -> list[int]:
        """Return the list of valid token ids for the current FSM state.

        Returns:
            List of valid token ids. Returns only '[' in OPEN_BRAC state,
            or the full vocabulary in GENERATION state.
        """
        valid_ids: list[int] = []

        if self.state == StateArray.OPEN_BRAC:
            valid_ids = self.vocab.get_ids_for(['['])

        elif self.state == StateArray.GENERATION:
            valid_ids = [id for id in self.vocab.vocab.values()]

        return valid_ids

    def reset(self) -> None:
        """Reset the parser to its initial state for reuse."""
        self.result = ""
        self.state = StateArray.OPEN_BRAC
        self.char_count = 0
