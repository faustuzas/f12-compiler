from models.enums import ExtendedEnum


class TokenType(ExtendedEnum):
    EOF = 'EOF'

    LIT_STR = 'LIT_STR'

    OP_PLUS = 'OP_PLUS'
    OP_MINUS = 'OP_MINUS'
    OP_DIV = 'OP_DIV'
    OP_MUL = 'OP_MUL'
    OP_POV = 'OP_POV'
    OP_MOD = 'OP_MOD'
    OP_NE = 'OP_NE'
    OP_NOT = 'OP_NOT'

    KW_TO_STDOUT = 'KW_TO_STDOUT'


class Token:
    def __init__(self, token_type: TokenType, line_number: int, value='') -> None:
        self.type = token_type
        self.value = value
        self.line_number = line_number

    def __repr__(self):
        value_part = f' | {self.value}' if self.value != '' else ''
        return str(self.type) + value_part
