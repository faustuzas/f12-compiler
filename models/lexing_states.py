from models.enums import ExtendedEnum


class LexingState(ExtendedEnum):
    START = 'ROOT'
    LIT_STR = 'LIT_STR'
