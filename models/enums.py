from enum import Enum


class ExtendedEnum(Enum):
    def __str__(self):
        return self.value

