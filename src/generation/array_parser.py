from ..models.models_class import TypeParserModel
from .state import StateArray
from .vocabulary import Vocabulary


class ArrayParser():
    def __init__(self, vocab: Vocabulary):

        TypeParserModel(
            vocab=vocab
        )

        self.state = StateArray.OPEN_BRAC
        self.vocab = vocab
        self.result = ""

    def transition(self, token: str) -> bool:
        if token not in '"':
            self.result += token

        if self.state == StateArray.OPEN_BRAC:
            self.state = StateArray.GENERATION

        elif self.state == StateArray.GENERATION:
            if "]" in token:
                self.state = StateArray.END

        if self.state == StateArray.END:
            return True

        return False

    def get_valid_ids(self) -> list[int]:
        valid_ids: list[int] = []

        if self.state == StateArray.OPEN_BRAC:
            valid_ids = self.vocab.get_ids_for(['['])

        elif self.state == StateArray.GENERATION:
            valid_ids = [id for id in self.vocab.vocab.values()]

        return valid_ids

    def reset(self) -> None:
        self.result = ""
        self.state = StateArray.OPEN_BRAC
