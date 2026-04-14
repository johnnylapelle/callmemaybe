from .state import StateStr
from .vocabulary import Vocabulary
from ..models.models_class import TypeParserModel


class StringParser():
    def __init__(self, vocab: Vocabulary):

        TypeParserModel(
            vocab=vocab
        )

        self.state = StateStr.QUOTE
        self.vocab = vocab
        self.result = ""
        self.max_token = 20
        self.char_count = 0

    def transition(self, token: str) -> bool:
        if token != '"':
            self.result += token
            self.char_count += 1

        if self.state == StateStr.QUOTE:
            self.state = StateStr.CHARACTERS

        elif self.state == StateStr.CHARACTERS:
            if token == '"' or self.char_count >= self.max_token:
                self.state = StateStr.END
            elif token == '/':
                self.state = StateStr.ESCAPE

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
        self.char_count = 0
