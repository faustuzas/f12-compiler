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
    OP_EQ = 'OP_EQ'
    OP_ASSIGN = 'OP_ASSIGN'
    OP_AND = 'OP_AND'
    OP_OR = 'OP_OR'
    OP_LT = 'OP_LT'
    OP_LE = 'OP_LE'

    C_SEMI = 'C_SEMI'
    C_COLON = 'C_COLON'
    C_COMMA = 'C_COMMA'
    C_ROUND_L = 'C_ROUND_L'
    C_ROUND_R = 'C_ROUND_R'
    C_CURLY_L = 'C_CURLY_L'
    C_CURLY_R = 'C_CURLY_R'
    C_SQUARE_L = 'C_SQUARE_L'
    C_SQUARE_R = 'C_SQUARE_R'

    KW_TO_STDOUT = 'KW_TO_STDOUT'
    KW_FROM_STDIN = 'KW_FROM_STDIN'


class Token:
    def __init__(self, token_type: TokenType, line_number: int, value='') -> None:
        self.type = token_type
        self.value = value
        self.line_number = line_number

    def __repr__(self):
        value_part = f' | {self.value}' if self.value != '' else ''
        return str(self.type) + value_part
