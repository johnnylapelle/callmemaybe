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
        self.state = StateStr.QUOTE
        self.vocab = vocab
        self.result = ""

    def transition(self, token: str) -> bool:
        if token != '"':
            self.result += token

        if self.state == StateStr.QUOTE:
            self.state = StateStr.CHARACTERS

        elif self.state == StateStr.CHARACTERS:
            if token == '"':
                self.state = StateStr.END
            elif token == '/':
                self.state == StateStr.ESCAPE

        elif self.state == StateStr.ESCAPE:
            self.state = StateStr.CHARACTERS

        if self.state == StateStr.END:
            return True

        return False

    def get_valid_ids(self) -> list[int]:
        valid_ids: list[int] = []

        if self.state == StateStr.QUOTE:
            valid_ids = self.vocab.get_ids_for(['"'])

        elif self.state == StateStr.CHARACTERS:
            valid_ids = [id for token, id in self.vocab.vocab.items()
                         if '"' not in token or token == '"']

        elif self.state == StateStr.ESCAPE:
            valid_ids = self.vocab.get_ids_for([
                '"', '\\', "/", 'b', 'f', 'n', 'r', 't'])

        return valid_ids

    def reset(self) -> None:
        self.result = ""
        self.state = StateStr.QUOTE
