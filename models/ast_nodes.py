from abc import ABC
from typing import List, Union


class Node(ABC):

    def print(self, ast_printer):
        for key in self.__dict__:
            val = self.__dict__[key]
            ast_printer.print(key, val)


class Type(Node):

    def __init__(self, is_array):
        self.is_array = is_array


class TypePrimitive(Type):

    def __init__(self, kind, is_array=False):
        super().__init__(is_array)
        self.kind = kind


class TypeUnit(Type):

    def __init__(self, unit_name, is_array=False):
        super().__init__(is_array)
        self.unit_name = unit_name


class Expr(Node):
    pass


class Statement(Node):
    pass


class StatementBlock(Node):

    def __init__(self, statements: List[Statement]) -> None:
        self.statements = statements


class FunParam(Node):

    def __init__(self, type_: Type, name):
        self.type = type_
        self.name = name


class Decl(Node):
    pass


class DeclFun(Decl):

    def __init__(self, name, params: List[FunParam], return_type: Type, statements: StatementBlock) -> None:
        self.name = name
        self.params = params
        self.return_type = return_type
        self.statements = statements


class DeclVar(Decl):

    def __init__(self, type_: Type, name, value=None, is_constant=False) -> None:
        self.type = type_
        self.name = name
        self.value = value
        self.is_constant = is_constant


class DeclUnit(Decl):
    pass


class Helper(Node):
    pass


class HelperInclude(Helper):

    def __init__(self, file_name) -> None:
        self.file_name = file_name


class Program(Node):

    root_elements: List[Union[Decl, Helper]]

    def __init__(self, root_elements: List[Union[Decl, Helper]]) -> None:
        self.root_elements = root_elements
