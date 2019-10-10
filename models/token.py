from models.enums import ExtendedEnum


class TokenType(ExtendedEnum):
    OP_PLUS = 'OP_PLUS'
    LIT_STR = 'LIT_STR'


class Token:
    def __init__(self, token_type: TokenType, line_number: int, value=None) -> None:
        self.type = token_type
        self.value = value
        self.line_number = line_number
