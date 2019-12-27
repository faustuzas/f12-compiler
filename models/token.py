from models.enums import ExtendedEnum
from models.types import Types


class TokenType(ExtendedEnum):
    EOF = 'EOF'

    LIT_STR = 'LIT_STR'
    LIT_FLOAT = 'LIT_FLOAT'
    LIT_INT = 'LIT_INT'
    LIT_CHAR = 'LIT_CHAR'
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
    C_PIPE = 'C_PIPE'

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
    KW_BREAK = 'KW_BREAK'
    KW_IN = 'KW_IN'

    PRIMITIVE_INT = 'PRIMITIVE_INT'
    PRIMITIVE_FLOAT = 'PRIMITIVE_FLOAT'
    PRIMITIVE_STRING = 'PRIMITIVE_STRING'
    PRIMITIVE_BOOL = 'PRIMITIVE_BOOL'
    PRIMITIVE_CHAR = 'PRIMITIVE_CHAR'
    PRIMITIVE_VOID = 'PRIMITIVE_VOID'

    CONSTANT_TRUE = 'CONSTANT_TRUE'
    CONSTANT_FALSE = 'CONSTANT_FALSE'

    HELPER_INCLUDE = 'HELPER_INCLUDE'

    IDENTIFIER = 'IDENTIFIER'

    NEW = 'NEW'
    FREE = 'FREE'


class Token:
    def __init__(self, token_type: TokenType, line_number: int, file_name: str, offset_in_line, value='') -> None:
        self.type = token_type
        self.value = value
        self.line_number = line_number
        self.file_name = file_name
        self.offset_in_line = offset_in_line

    def __repr__(self):
        value_part = f' | {self.value}' if self.value != '' else ''
        return str(self.type) + value_part

    def __str__(self):
        return self.__repr__()


primitive_types_by_token_type = {
    TokenType.PRIMITIVE_INT: Types.INT,
    TokenType.PRIMITIVE_VOID: Types.VOID,
    TokenType.PRIMITIVE_BOOL: Types.INT,
    TokenType.PRIMITIVE_FLOAT: Types.FLOAT,
    TokenType.PRIMITIVE_STRING: Types.STRING,
    TokenType.PRIMITIVE_CHAR: Types.CHAR
}

primitive_type_tokens = [
    TokenType.PRIMITIVE_INT,
    TokenType.PRIMITIVE_VOID,
    TokenType.PRIMITIVE_BOOL,
    TokenType.PRIMITIVE_FLOAT,
    TokenType.PRIMITIVE_STRING,
    TokenType.PRIMITIVE_CHAR
]

type_tokens = [
    *primitive_type_tokens,
    TokenType.IDENTIFIER
]
