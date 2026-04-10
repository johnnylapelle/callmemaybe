from .state import StateNum
from .vocabulary import Vocabulary


class NumberParser():
    def __init__(self, vocab: Vocabulary):
        self.state_num = StateNum.QUOTE
        self.vocab = vocab
        self.result = ""

        self.digits_count = 0
        self.max_digits = 10

    def transition(self, token: str) -> bool:
        if token not in ',"':
            self.result += token

        if self.state_num == StateNum.QUOTE:
            self.state_num = StateNum.START

        elif self.state_num == StateNum.START:
            if token == "0":
                self.state_num = StateNum.AFTER_INT
            elif token in "-123456789":
                self.state_num = StateNum.DIGITS

        elif self.state_num == StateNum.DIGITS:
            self.digits_count += 1
            if token in '",':
                self.state_num = StateNum.END
            elif self.digits_count >= self.max_digits:
                self.digits_count = 0
                self.state_num = StateNum.END
            elif token == ".":
                self.state_num = StateNum.DECIMAL
            elif token in "Ee":
                self.state_num = StateNum.EXPONENT

        elif self.state_num == StateNum.AFTER_INT:
            if token in '",':
                self.state_num = StateNum.END
            elif token in "Ee":
                self.state_num = StateNum.EXPONENT

        elif self.state_num == StateNum.DECIMAL:
            if token in '",':
                self.state_num = StateNum.END
            else:
                self.state_num = StateNum.DECIMAL_DIGITS

        elif self.state_num == StateNum.DECIMAL_DIGITS:
            if token in '",':
                self.state_num = StateNum.END
            elif token in "eE":
                self.state_num = StateNum.EXPONENT
            else:
                self.state_num = StateNum.DECIMAL_DIGITS

        elif self.state_num == StateNum.EXPONENT:
            if token in '",':
                self.state_num = StateNum.END
            elif token in "+-":
                self.state_num = StateNum.EXP_SIGN
            else:
                self.state_num = StateNum.EXP_DIGITS

        elif self.state_num == StateNum.EXP_SIGN:
            self.state_num = StateNum.EXP_DIGITS

        elif self.state_num == StateNum.EXP_DIGITS:
            if token in '",':
                self.state_num = StateNum.END
            else:
                self.state_num = StateNum.EXP_DIGITS

        if self.state_num == StateNum.END:
            return True

        return False

    def get_valid_ids(self) -> list[int]:
        valid_ids: list[int] = []

        if self.state_num == StateNum.QUOTE:
            valid_ids = self.vocab.get_ids_for(['"'])

        elif self.state_num == StateNum.START:
            valid_ids = self.vocab.get_ids_for([
                    '-', '0', '1', '2', '3', '4',
                    '5', '6', '7', '8', '9'])

        elif self.state_num == StateNum.DIGITS:
            valid_ids = self.vocab.get_ids_for([
                '0', '1', '2', '3', '4',
                '5', '6', '7', '8', '9',
                '.', 'e', 'E', '"'])

        elif self.state_num == StateNum.AFTER_INT:
            valid_ids = self.vocab.get_ids_for([
                '.', 'E', 'e', '"'
                ])

        elif self.state_num == StateNum.DECIMAL:
            valid_ids = self.vocab.get_ids_for([
                '0', '1', '2', '3', '4',
                '5', '6', '7', '8', '9',
                '"'])

        elif self.state_num == StateNum.DECIMAL_DIGITS:
            valid_ids = self.vocab.get_ids_for([
                '0', '1', '2', '3', '4',
                '5', '6', '7', '8', '9',
                'e', 'E', '"'])

        elif self.state_num == StateNum.EXPONENT:
            valid_ids = self.vocab.get_ids_for([
                '0', '1', '2', '3', '4',
                '5', '6', '7', '8', '9',
                'e', 'E', '"', '+', '-'])

        elif self.state_num == StateNum.EXP_SIGN:
            valid_ids = self.vocab.get_ids_for([
                '0', '1', '2', '3', '4',
                '5', '6', '7', '8', '9'
                ])

        elif self.state_num == StateNum.EXP_DIGITS:
            valid_ids = self.vocab.get_ids_for([
                '0', '1', '2', '3', '4',
                '5', '6', '7', '8', '9',
                '"'])

        return valid_ids

    def reset(self) -> None:
        self.state_num = StateNum.QUOTE
