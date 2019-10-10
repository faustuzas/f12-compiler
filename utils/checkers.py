from .ranges import char_range

lower_letters = char_range('a', 'z')
upper_letters = char_range('A', 'Z')


def ident_start_char(char: str) -> bool:
    return \
        char in lower_letters \
        or char in upper_letters \
        or char == '_'
