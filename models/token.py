from models.enums import ExtendedEnum


class TokenType(ExtendedEnum):
    EOF = 'EOF'

    LIT_STR = 'LIT_STR'
    LIT_FLOAT = 'LIT_FLOAT'
    LIT_INT = 'LIT_INT'
    LIT_BOOL = 'LIT_BOOL'

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
    OP_GT = 'OP_GT'
    OP_GE = 'OP_GE'
    OP_ACCESS = 'OP_ACCESS'

    C_SEMI = 'C_SEMI'
    C_COLON = 'C_COLON'
    C_COMMA = 'C_COMMA'
    C_ROUND_L = 'C_ROUND_L'
    C_ROUND_R = 'C_ROUND_R'
    C_CURLY_L = 'C_CURLY_L'
    C_CURLY_R = 'C_CURLY_R'
    C_SQUARE_L = 'C_SQUARE_L'
    C_SQUARE_R = 'C_SQUARE_R'

    KW_FAT_ARROW = 'KW_FAT_ARROW'
    KW_TO_STDOUT = 'KW_TO_STDOUT'
    KW_FROM_STDIN = 'KW_FROM_STDIN'
    KW_FUN = 'KW_FUN'
    KW_IF = 'KW_IF'
    KW_RETURN = 'KW_RETURN'
    KW_UNIT = 'KW_UNIT'
    KW_ELSE = 'KW_ELSE'
    KW_EACH = 'KW_EACH'
    KW_WHILE = 'KW_WHILE'
    KW_CONST = 'KW_CONST'
    KW_CONTINUE = 'KW_CONTINUE'
    KW_BEAK = 'KW_BEAK'
    KW_IN = 'KW_IN'

    PRIMITIVE_INT = 'PRIMITIVE_INT'
    PRIMITIVE_FLOAT = 'PRIMITIVE_FLOAT'
    PRIMITIVE_STRING = 'PRIMITIVE_STRING'
    PRIMITIVE_BOOL = 'PRIMITIVE_BOOL'
    PRIMITIVE_VOID = 'PRIMITIVE_VOID'

    CONSTANT_NULL = 'CONSTANT_NULL'
    CONSTANT_TRUE = 'CONSTANT_TRUE'
    CONSTANT_FALSE = 'CONSTANT_FALSE'

    HELPER_INCLUDE = 'HELPER_INCLUDE'

    IDENTIFIER = 'IDENTIFIER'


class Token:
    def __init__(self, token_type: TokenType, line_number: int, file_name: str, value='') -> None:
        self.type = token_type
        self.value = value
        self.line_number = line_number
        self.file_name = file_name

    def __repr__(self):
        value_part = f' | {self.value}' if self.value != '' else ''
        return str(self.type) + value_part


primitive_type_tokens = [
    TokenType.PRIMITIVE_INT,
    TokenType.PRIMITIVE_VOID,
    TokenType.PRIMITIVE_BOOL,
    TokenType.PRIMITIVE_FLOAT,
    TokenType.PRIMITIVE_STRING,
]

type_tokens = [
    *primitive_type_tokens,
    TokenType.IDENTIFIER
]
