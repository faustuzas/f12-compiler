from abc import ABC

from utils import sizes


class Type(ABC):
    
    @staticmethod
    def name_in_code():
        raise NotImplementedError()

    @staticmethod
    def to_stdout_instr():
        raise NotImplementedError()

    @staticmethod
    def size_in_bytes():
        raise NotImplementedError()


class Int(Type):
    
    @staticmethod
    def name_in_code():
        return 'int'

    @staticmethod
    def to_stdout_instr():
        from models.instructions import InstructionType
        return InstructionType.TO_STDOUT_INT

    @staticmethod
    def size_in_bytes():
        return sizes.int


class Float(Type):

    @staticmethod
    def name_in_code():
        return 'float'

    @staticmethod
    def to_stdout_instr():
        from models.instructions import InstructionType
        return InstructionType.TO_STDOUT_FLOAT

    @staticmethod
    def size_in_bytes():
        return sizes.float


class Char(Type):

    @staticmethod
    def name_in_code():
        return 'char'

    @staticmethod
    def to_stdout_instr():
        from models.instructions import InstructionType
        return InstructionType.TO_STDOUT_CHAR

    @staticmethod
    def size_in_bytes():
        return sizes.char


class String(Type):
    
    @staticmethod
    def name_in_code():
        return 'string'

    @staticmethod
    def to_stdout_instr():
        from models.instructions import InstructionType
        return InstructionType.TO_STDOUT_STRING

    @staticmethod
    def size_in_bytes():
        return sizes.address


class Bool(Type):
    
    @staticmethod
    def name_in_code():
        return 'bool'

    @staticmethod
    def to_stdout_instr():
        from models.instructions import InstructionType
        return InstructionType.TO_STDOUT_BOOL

    @staticmethod
    def size_in_bytes():
        return sizes.bool


class Void(Type):
    
    @staticmethod
    def name_in_code():
        return 'void'

    @staticmethod
    def to_stdout_instr():
        return 0

    @staticmethod
    def size_in_bytes():
        return 0


def find_type(type_):
    if type_ is int:
        return Int
    if type_ is float:
        return Float
    if type_ is str:
        return String
    if type_ is bool:
        return Bool
    raise ValueError(f'There is no type class for {type_}')