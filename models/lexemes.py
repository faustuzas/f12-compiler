from models.enums import ExtendedEnum


class KeyWord(ExtendedEnum):
    FUN = 'fun'
    IF = 'if'
    RETURN = 'ret'
    FAT_ARROW = '=>'
    UNIT = 'unit'
    ELSE = 'else'
    EACH = 'each'
    WHILE = 'while'
    CONST = 'const'
    CONTINUE = 'continue'
    BEAK = 'break'
    NULL = 'null'


class PrimitiveType(ExtendedEnum):
    INT = 'int'
    FLOAT = 'float'
    STRING = 'str'
    BOOL = 'bool'
    CHAR = 'char'
    BYTE = 'byte'


class Helper(ExtendedEnum):
    INCLUDE = 'INCLUDE'
