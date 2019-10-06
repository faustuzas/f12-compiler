from enum import Enum


class TokenType(Enum):
    LIT_STR = 'LIT_STR'


class Token:
    def __init__(self, token_type: TokenType, value, line_number: int) -> None:
        self.type = token_type
        self.value = value
        self.line_number = line_number
