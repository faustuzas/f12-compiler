from enum import Enum


class Lexem(Enum):
    def __str__(self):
        return self.value


class KeyWord(Lexem):
    FUN = 'fun'
    HELPER_START = '>'
    IF = 'if'
    RETURN = 'ret'
    FAT_ARROW = '=>'
    UNIT = 'unit'
    TO_STDOUT = '-->'
    FROM_STDOUT = '<--'
    ELSE = 'else'
    EACH = 'each'
    WHILE = 'while'
    CONST = 'const'
    CONTINUE = 'continue'
    BEAK = 'break'
    NULL = 'null'


class PrimitiveType(Lexem):
    INT = 'int'
    FLOAT = 'float'
    STRING = 'str'
    BOOL = 'bool'
    CHAR = 'char'
    BYTE = 'byte'

    def __str__(self):
        return self.value
