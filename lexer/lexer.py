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
    end_switch: Switcher

    def __init__(self, text: str) -> None:
        assert len(text)

        self.text = text
        self.current_char = text[0]

        self.init_switches()

    def init_switches(self) -> None:
        self.start_switch = Switcher.from_dict({
            '+': lambda: self.add_token(Token(TokenType.OP_PLUS, self.line_number))
        })

        self.end_switch = Switcher.from_dict({
            LexingState.START: lambda: self.add_token(Token(TokenType.EOF, self.line_number))
        })

    def begin_token(self, new_state: LexingState = None):
        self.token_start_line_number = self.line_number
        if new_state:
            self.state = new_state

    def add_token(self, op_token: Token, rollback=False):
        self.tokens.append(op_token)
        self.token_buffer = ''
        self.state = LexingState.START
        if rollback:
            self.offset -= 1

    def lex_start(self):
        pass

    def lex(self):
        pass

    def lex_all(self):
        while self.offset < len(self.text):
            self.lex()
            self.offset += 1

        self.current_char = ' '
        self.lex()


if __name__ == '__main__':
    with open("main.f12") as main_file:
        source_text = ''.join(main_file.readlines())

        lexer = Lexer(source_text)



