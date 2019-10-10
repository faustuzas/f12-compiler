from models import LexingState, Token, TokenType
from utils import Switcher


"""
What can I found? 
    - "+"
    - "-"
        + "-"
            + ">"
    - "/"
        + ""
        + "/"
        + "*"
    - "*"
        + ""
        + "/"
    - "%"
    - "^"
    - "."
        + "[0-9]*"
            + ""
            + "E" or "e"
                + "" or "+" or "-"
                    + "[0-9]*"
    - "!"
        + ""
        + "="
    - "="
        + ""
        + "="
    - ">"
        + ""
        + "="
        + "include"
    - "<"
        + ""
        + "="
        + "-"
            + "-"
    - "&"
        + "&"
    - "|"
        + "|"
    - ";"
    - ":"
    - ","
    - "("
    - ")"
    - "{"
    - "}"
    - "["
    - "]"
    - "[0-9]*"
        + "" // int
        + "."
            + ""
            + "[0-9]*"
                + ""
                + "E" or "e"
                    + "" or "+" or "-"
                        + "[0-9]*"
    - "\""
        + ".*"
            + "\""
        + "\\"
            + "n" or "t" or "\"" or "r"
                + back to string
    - [a-zA-z]
        + [a-zA-z1-9_]
            = keyword
            = identifier
            = type
    
"""


class Lexer:
    state: LexingState = LexingState.START
    token_buffer: str = ''
    line_number: int = 1
    offset: int = 0
    tokens: list = []
    token_start_line_number: int = 0
    current_char: str = None

    """
    Switch imitating objects
    Have to be initialized one to optimize memory consumption and performance
    """
    start_switch: Switcher

    def __init__(self, text: str) -> None:
        assert len(text)

        self.text = text
        self.current_char = text[0]

        self.init_switches()

    def init_switches(self) -> None:
        self.start_switch = Switcher.from_dict({
            '+': lambda: self.add_token(Token(TokenType.OP_PLUS, self.line_number))
        })

    def add_token(self, op_token: Token):
        self.tokens.append(op_token)
        self.proceed()

    def proceed(self, string=False, clear_buffer=False) -> None:
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

        if clear_buffer:
            self.token_buffer = ''

        self.current_char = self.text[self.offset]

    # def lex_start(self):


if __name__ == '__main__':
    with open("main.f12") as main_file:
        source_text = ''.join(main_file.readlines())

        lexer = Lexer(source_text)



