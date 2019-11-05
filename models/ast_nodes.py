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


class ExprOr(Expr):

    def __init__(self, left, right) -> None:
        self.left = left
        self.right = right


class ExprAnd(Expr):

    def __init__(self, left, right) -> None:
        self.left = left
        self.right = right


class ExprEq(Expr):

    def __init__(self, left, right) -> None:
        self.left = left
        self.right = right


class ExprNe(Expr):

    def __init__(self, left, right) -> None:
        self.left = left
        self.right = right


class ExprGt(Expr):

    def __init__(self, left, right) -> None:
        self.left = left
        self.right = right


class ExprGe(Expr):

    def __init__(self, left, right) -> None:
        self.left = left
        self.right = right


class ExprLt(Expr):

    def __init__(self, left, right) -> None:
        self.left = left
        self.right = right


class ExprLe(Expr):

    def __init__(self, left, right) -> None:
        self.left = left
        self.right = right


class ExprAdd(Expr):

    def __init__(self, left, right) -> None:
        self.left = left
        self.right = right


class ExprSub(Expr):

    def __init__(self, left, right) -> None:
        self.left = left
        self.right = right


class ExprMul(Expr):

    def __init__(self, left, right) -> None:
        self.left = left
        self.right = right


class ExprDiv(Expr):

    def __init__(self, left, right) -> None:
        self.left = left
        self.right = right


class ExprMod(Expr):

    def __init__(self, left, right) -> None:
        self.left = left
        self.right = right


class ExprUPlus(Expr):

    def __init__(self, expr) -> None:
        self.expr = expr


class ExprUMinus(Expr):

    def __init__(self, expr) -> None:
        self.expr = expr


class ExprPow(Expr):

    def __init__(self, left, right) -> None:
        self.left = left
        self.right = right


class ExprFnCall(Expr):

    def __init__(self, function_name, params) -> None:
        self.function_name = function_name
        self.params = params


class ExprAccess(Expr):

    def __init__(self, obj, field) -> None:
        self.object = obj
        self.field = field


class ExprAssign(Expr):

    def __init__(self, obj, value) -> None:
        self.object = obj
        self.value = value


class ExprLit(Expr):

    def __init__(self, value):
        self.value = value


class ExprLitStr(ExprLit):
    pass


class ExprLitFloat(ExprLit):
    pass


class ExprLitInt(ExprLit):
    pass


class ExprLitBool(ExprLit):
    pass


class ExprLitArray(ExprLit):
    pass


class ExprLitNull(ExprLit):
    pass


class ExprVar(Expr):

    def __init__(self, identifier):
        self.identifier = identifier


class ExprFromStdin(Expr):
    pass


class ExprArrayAccess(Expr):
    def __init__(self, array, index_expr):
        self.array = array
        self.index_expr = index_expr


class ExprCreateUnit(Expr):
    def __init__(self, unit_name, args):
        self.unit_name = unit_name
        self.args = args


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


class DeclUnitField(Node):

    def __init__(self, type_: Type, name) -> None:
        self.type = type_
        self.name = name


class DeclUnit(Decl):

    def __init__(self, name, fields: List[DeclUnitField]) -> None:
        self.name = name
        self.fields = fields


class Helper(Node):
    pass


class HelperInclude(Helper):

    def __init__(self, file_name) -> None:
        self.file_name = file_name


class Program(Node):

    root_elements: List[Union[Decl, Helper]]

    def __init__(self, root_elements: List[Union[Decl, Helper]]) -> None:
        self.root_elements = root_elements
