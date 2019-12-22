from typing import Tuple


def char_range(c1, c2) -> Tuple[str]:
    return tuple([chr(c) for c in range(ord(c1), ord(c2) + 1)])


lower_letters = char_range('a', 'z')
upper_letters = char_range('A', 'Z')
letters = lower_letters + upper_letters
digits = char_range('0', '9')
digits_without_zero = char_range('1', '9')

special_chars_without_quotes = (
    '!', '#', '$', '%', '&', '(', ')', '*', '+', ',', '-', '.',
    '/', ':', ';', '<', '=', '>', '?', '@', '{', '|', '}', '~'
)

chars = letters + digits + special_chars_without_quotes + ('"',)
string_chars = letters + digits + special_chars_without_quotes + ('\'',)

