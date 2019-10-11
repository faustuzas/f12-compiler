from models.enums import ExtendedEnum


class LexingState(ExtendedEnum):
    START = 'START'
    LIT_STR = 'LIT_STR'

    OP_MINUS = 'OP_MINUS'
    OP_MINUS_2 = 'OP_MINUS_2'

    OP_DIV = 'OP_DIV'
    OP_NOT = 'OP_NOT'
    OP_ASSIGN = 'OP_ASSIGN'
    OP_AND = 'OP_AND'
    OP_OR = 'OP_OR'
    OP_LT = 'OP_LT'

    SL_COMMENT = 'SL_COMMENT'
    ML_COMMENT = 'ML_COMMENT'
    ML_COMMENT_END = 'ML_COMMENT_END'

    KW_FROM_STDIN = 'KW_FROM_STDIN'
