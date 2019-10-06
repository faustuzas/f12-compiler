from typing import List

from models import LexingState
from preparators import BasePreparator, include_preparator
from preparators.errors import PreparationError
from utils import printer


class Lexer:
    token_buffer: str = ''
    line_number: int = 1
    offset: int = 0
    state: LexingState = LexingState.START
    tokens: list = []
    token_start_line_number: int = 0

    preparators: List[BasePreparator] = [
        include_preparator
    ]

    def __init__(self, text: str) -> None:
        self.text = text

    def prepare(self) -> bool:
        for prep in self.preparators:
            try:
                self.text = prep.prepare(self.text)
            except PreparationError as error:
                printer.error(str(error), 'Preparation error')
                return False
        return True

    def lex(self):
        if not self.prepare():
            return


if __name__ == '__main__':
    with open("main.f12") as main_file:
        source_text = ''.join(main_file.readlines())

        lexer = Lexer(source_text)
        lexer.prepare()



