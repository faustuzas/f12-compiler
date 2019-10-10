from typing import List
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
    state: LexingState
    token_buffer: str
    line_number: int
    offset: int
    tokens: List[Token]
    token_start_line_number: int
    current_char: str

    """
    Switch imitating objects
    Have to be initialized one to optimize memory consumption and performance
    """
    main_switch: Switcher
    start_switch: Switcher
    end_switch: Switcher

    def __init__(self, text: str) -> None:
        assert len(text)

        self.state = LexingState.START
        self.token_buffer = ''
        self.line_number = 1
        self.offset = 0
        self.tokens: List[Token] = []
        self.token_start_line_number = 0
        self.text = text
        self.current_char = text[0]

        self.init_switches()

    def init_switches(self) -> None:
        self.main_switch = Switcher.from_dict({
            LexingState.START: self.lex_start
        })

        self.start_switch = Switcher.from_dict({
            '+': lambda: self.add_token(TokenType.OP_PLUS),
            '-': lambda: self.add_token(TokenType.OP_MINUS),
        })

        self.end_switch = Switcher.from_dict({
            LexingState.START: lambda: self.add_token(TokenType.EOF)
        })

    def begin_token(self, new_state: LexingState = None):
        self.token_start_line_number = self.line_number
        if new_state:
            self.state = new_state

    def add_token(self, token_type: TokenType, rollback=False):
        self.tokens.append(Token(token_type, self.line_number, self.token_buffer))
        self.token_buffer = ''
        self.state = LexingState.START
        if rollback:
            self.offset -= 1

    def lex_start(self):
        self.start_switch.exec(self.current_char)

    def lex(self):
        self.main_switch.exec(self.current_char)

    def lex_all(self):
        while self.offset < len(self.text):
            self.lex()
            self.offset += 1

        self.current_char = ' '
        self.lex()

        self.end_switch.exec(self.state)


if __name__ == '__main__':
    with open("main.f12") as main_file:
        source_text = ''.join(main_file.readlines())

        lexer = Lexer(source_text)



