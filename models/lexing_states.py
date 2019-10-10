from models.enums import ExtendedEnum


class LexingState(ExtendedEnum):
    START = 'START'
    LIT_STR = 'LIT_STR'
    OP_MINUS = 'OP_MINUS'
