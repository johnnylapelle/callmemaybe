# QUOTE_OPEN
#   → '"' → CHARACTERS

# CHARACTERS
#   → any codepoint except " \ control chars → CHARACTERS (loop)
#   → '\' → ESCAPE
#   → '"' → END

# ESCAPE
#   → '"'  → CHARACTERS  (escaped quote)
#   → '\'  → CHARACTERS  (escaped backslash)
#   → '/'  → CHARACTERS  (solidus)
#   → 'b'  → CHARACTERS  (backspace)
#   → 'f'  → CHARACTERS  (formfeed)
#   → 'n'  → CHARACTERS  (newline)
#   → 'r'  → CHARACTERS  (carriage return)
#   → 't'  → CHARACTERS  (tab)
#   → 'u'  → UNICODE

# UNICODE
#   → 4 hex digits → CHARACTERS

from .state import StateStr
from .vocabulary import Vocabulary


class StringParser():
    def __init__(self, vocab: Vocabulary):
        self.state_str = StateStr.QUOTE
        self.vocab = vocab
        self.result = ""

    def transition(self, token: str) -> bool:
        self.result += token

        if self.state_str == StateStr.QUOTE:
            self.state_str = StateStr.CHARACTERS

        elif self.state_str == StateStr.CHARACTERS:
            if token == '"':
                self.state_str = StateStr.END
            elif token == '/':
                self.state_str == StateStr.ESCAPE

        elif self.state_str == StateStr.ESCAPE:
            self.state_str = StateStr.CHARACTERS

        if self.state_str == StateStr.END:
            return True

        return False

    def get_valid_ids(self) -> list[int]:
        valid_ids: list[int] = []

        if self.state_str == StateStr.QUOTE:
            valid_ids = self.vocab.get_ids_for(['"'])

        elif self.state_str == StateStr.CHARACTERS:
            valid_ids = list(self.vocab.vocab.values())

        elif self.state_str == StateStr.ESCAPE:
            valid_ids = self.vocab.get_ids_for([
                '"', '\\', "/", 'b', 'f', 'n', 'r', 't'])

        return valid_ids

    def reset(self) -> None:
        self.state_str = StateStr.QUOTE
