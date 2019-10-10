from enum import Enum


class KeyWord(Enum):
    FUN = 'fun'
    HELPER_START = '>'

    def __str__(self):
        return self.value
