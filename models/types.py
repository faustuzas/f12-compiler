from abc import ABC

from utils import sizes


class Type(ABC):
    
    @staticmethod
    def name_in_code():
        raise NotImplementedError()

    @staticmethod
    def size_in_bytes():
        raise NotImplementedError()


class Int(Type):
    
    @staticmethod
    def name_in_code():
        return 'int'

    @staticmethod
    def size_in_bytes():
        return sizes.int


class Float(Type):

    @staticmethod
    def name_in_code():
        return 'int'

    @staticmethod
    def size_in_bytes():
        return sizes.float


class Char(Type):

    @staticmethod
    def name_in_code():
        return 'char'

    @staticmethod
    def size_in_bytes():
        return sizes.char


class String(Type):
    
    @staticmethod
    def name_in_code():
        return 'string'

    @staticmethod
    def size_in_bytes():
        return sizes.address


class Bool(Type):
    
    @staticmethod
    def name_in_code():
        return 'bool'

    @staticmethod
    def size_in_bytes():
        return sizes.bool


class Void(Type):
    
    @staticmethod
    def name_in_code():
        return 'void'

    @staticmethod
    def size_in_bytes():
        raise Exception('Unreachable code')

