from enum import Enum, EnumMeta


class ExtendedEnumMeta(EnumMeta):
    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            return None


class ExtendedEnum(Enum, metaclass=ExtendedEnumMeta):
    def __str__(self):
        return self.value

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, ExtendedEnum):
            return str(other) == str(self)

    def __hash__(self):
        return super.__hash__(self.__str__())
