from typing import Tuple


def char_range(c1, c2) -> Tuple[str]:
    return tuple([chr(c) for c in range(ord(c1), ord(c2) + 1)])


lower_letters = char_range('a', 'z')
upper_letters = char_range('A', 'Z')
letters = lower_letters + upper_letters
