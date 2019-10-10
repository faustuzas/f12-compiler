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

    def __init__(self, text: str) -> None:
        assert len(text)

        self.state = LexingState.START
        self.token_buffer = ''
        self.line_number = 1
        self.offset = 0
        self.tokens: List[Token] = []
        self.token_start_line_number = 0
        self.text = text

    def lex_all(self):
        while self.offset < len(self.text):
            self.current_char = self.text[self.offset]
            self.lex()
            self.offset += 1

        self.current_char = ' '
        self.lex()

        Switcher.from_dict({
            (LexingState.START, LexingState.SL_COMMENT): lambda: self.add_token(TokenType.EOF)
        }).exec(self.state)

    def lex(self):
        Switcher.from_dict({
            LexingState.START: self.lex_start,
            LexingState.OP_MINUS: self.lex_op_minus,
            LexingState.OP_MINUS_2: self.lex_op_minus_2,
            LexingState.OP_DIV: self.lex_op_div,
            LexingState.SL_COMMENT: self.lex_sl_comment
        }).exec(self.state)

    def lex_start(self):
        Switcher.from_dict({
            '+': lambda: self.add_token(TokenType.OP_PLUS),
            '-': lambda: self.begin_tokenizing(LexingState.OP_MINUS),
            '/': lambda: self.begin_tokenizing(LexingState.OP_DIV),
            '\n': self.inc_new_line,
            ' ': lambda: ()  # ignore
            # TODO: Add unrecognised char handling
        }).exec(self.current_char)

    def lex_op_minus(self):
        Switcher.from_dict({
            ' ': lambda: self.add_token(TokenType.OP_MINUS),
            '-': lambda: self.to_state(LexingState.OP_MINUS_2)
        }).exec(self.current_char)

    def lex_op_minus_2(self):
        Switcher.from_dict({
            '>': lambda: self.add_token(TokenType.KW_TO_STDOUT),
            '-': lambda: self.add_token(TokenType.OP_MINUS, keep_state=True)
        }).default(lambda: (self.add_token(TokenType.OP_MINUS),
                            self.add_token(TokenType.OP_MINUS))).exec(self.current_char)

    def lex_op_div(self):
        Switcher.from_dict({
            '/': lambda: self.to_state(LexingState.SL_COMMENT),
            # '*': lambda: self.to_state(TokenType.MULTI_COMMENT_START)
        }).default(lambda: self.add_token(TokenType.OP_DIV, rollback=True)).exec(self.current_char)

    def lex_sl_comment(self):
        Switcher.from_dict({
            '\n': lambda: (self.to_state(LexingState.START), self.inc_new_line())
        }).exec(self.current_char)

    def begin_tokenizing(self, new_state: LexingState):
        self.token_start_line_number = self.line_number
        self.to_state(new_state)

    def add_token(self, token_type: TokenType, rollback=False, keep_state=False):
        self.tokens.append(Token(token_type, self.line_number, self.token_buffer))
        self.token_buffer = ''
        if not keep_state:
            self.state = LexingState.START
        if rollback:
            self.offset -= 1

    def to_state(self, state: LexingState):
        assert state is not None
        self.state = state

    def inc_new_line(self):
        self.line_number += 1
