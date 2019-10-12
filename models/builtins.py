from models.token import TokenType

keywords = {
    'fun': TokenType.KW_FUN,
    'if': TokenType.KW_IF,
    'ret': TokenType.KW_RETURN,
    'unit': TokenType.KW_UNIT,
    'else': TokenType.KW_ELSE,
    'each': TokenType.KW_EACH,
    'while': TokenType.KW_WHILE,
    'const': TokenType.KW_CONST,
    'continue': TokenType.KW_CONTINUE,
    'break': TokenType.KW_BEAK
}

primitive_types = {
    'int': TokenType.PRIMITIVE_INT,
    'float': TokenType.PRIMITIVE_FLOAT,
    'string': TokenType.PRIMITIVE_STRING,
    'bool': TokenType.PRIMITIVE_BOOL
}

constants = {
    'null': TokenType.CONSTANT_NULL,
    'false': TokenType.CONSTANT_FALSE,
    'true': TokenType.CONSTANT_TRUE
}

helpers = {
    'include': TokenType.HELPER_INCLUDE
}
