from typing import List

from models import LexingState, KeyWord
from preparators import BasePreparator, include_preparator, comments_preparator
from preparators.errors import PreparationError
from utils import Switcher, printer


class Lexer:
    token_buffer: str = ''
    line_number: int = 1
    offset: int = 0
    state: LexingState = LexingState.ROOT
    tokens: list = []
    token_start_line_number: int = 0
    current_char: str = None

    preparators: List[BasePreparator] = [
        include_preparator,
        comments_preparator
    ]

    def __init__(self, text: str) -> None:
        assert len(text)

        self.text = text
        self.current_char = text[0]

    def lex_start(self):
        pass

    def check_future(self, string):
        return self.text.startswith(str(string), self.offset)

    def prepare(self) -> bool:
        for prep in self.preparators:
            try:
                self.text = prep.prepare(self.text)
            except PreparationError as error:
                printer.error(str(error), 'Preparation error')
                return False
        return True

    def lex_stmnt_fun(self):
        pass

    def lex_stmnt_helper(self):
        pass

    def lex_char(self):
        Switcher.from_dict({
            LexingState.ROOT: Switcher.from_dict({
                # Ignore whitespace
                self.current_char.isspace: self.proceed,
                # Check if function declaration
                lambda: self.check_future(KeyWord.FUN): self.lex_stmnt_fun,
                # Check if helper
                lambda: self.check_future(KeyWord.HELPER_START): self.lex_stmnt_helper,
                # Check for identifier start
                # lambda: checkers.ident_start_char(self.current_char):
            }).exec(),
        })

    def proceed(self, string=False) -> None:
        """
        If string is set to true, then don't increase line number on new line symbol
        """
        if string:
            self.offset += 1
        else:
            if self.current_char == '\n':
                self.line_number += 1
                self.offset = 0
            else:
                self.offset += 1

        self.current_char = self.text[self.offset]

    def lex(self) -> None:
        if not self.prepare():
            return

        while self.offset < len(self.text):
            self.lex_char()


if __name__ == '__main__':
    with open("main.f12") as main_file:
        source_text = ''.join(main_file.readlines())

        lexer = Lexer(source_text)
        lexer.prepare()



