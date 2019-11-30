from abc import ABC
from typing import List, Union

from models.scope import Scope
from utils.error_printer import print_error


class Node(ABC):

    def print(self, ast_printer):
        for key in self.__dict__:
            if key.startswith('_'):
                continue

            val = self.__dict__[key]
            ast_printer.print(key, val)

    def resolve_includes(self):
        return None

    def resolve_names(self, scope: Scope) -> None:
        raise NotImplementedError(f'Resolve names not implemented for {self.__class__}')


class Type(Node, ABC):
    pass


class TypePrimitive(Type):

    def __init__(self, kind):
        self.kind = kind

    def resolve_names(self, scope: Scope):
        pass


class TypeArrayPrimitive(TypePrimitive):
    pass


class TypeUnit(Type):

    def __init__(self, unit_name):
        self.unit_name = unit_name
        self.unit_decl_node = None

    def resolve_names(self, scope: Scope):
        self.unit_decl_node = scope.resolve_name(self.unit_name)


class TypeArrayUnit(TypeUnit):
    pass


class Expr(Node, ABC):
    pass


class ExprBinary(Expr, ABC):
    def __init__(self, left, right) -> None:
        self.left = left
        self.right = right

    def resolve_names(self, scope: Scope):
        self.left.resolve_names(scope)
        self.right.resolve_names(scope)


class ExprBinaryLogic(ExprBinary):

    def resolve_types(self):
        pass


class ExprOr(ExprBinary):
    pass


class ExprAnd(ExprBinary):
    pass


class ExprEq(ExprBinary):
    pass


class ExprNe(ExprBinary):
    pass


class ExprGt(ExprBinary):
    pass


class ExprGe(ExprBinary):
    pass


class ExprLt(ExprBinary):
    pass


class ExprLe(ExprBinary):
    pass


class ExprAdd(ExprBinary):
    pass


class ExprSub(ExprBinary):
    pass


class ExprMul(ExprBinary):
    pass


class ExprDiv(ExprBinary):
    pass


class ExprMod(ExprBinary):
    pass


class ExprUnaryOp(Expr):

    def __init__(self, expr) -> None:
        self.expr = expr

    def resolve_names(self, scope: Scope):
        self.expr.resolve_names(scope)


class ExprUPlus(ExprUnaryOp):
    pass


class ExprUMinus(ExprUnaryOp):
    pass


class ExprPow(ExprBinary):
    pass


class ExprLit(Expr, ABC):

    def __init__(self, value):
        self.value = value

    def resolve_names(self, scope: Scope):
        pass


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


class ExprFromStdin(Expr):

    def resolve_names(self, scope: Scope):
        pass


class Assignable(ABC):
    def resolve_identifier(self):
        raise NotImplementedError(f'Resolve identifier is not implemented for {self.__class__}')

    def resolve_decl_node(self):
        raise NotImplementedError(f'Resolve decl node is not implemented for {self.__class__}')

    def resolve_type_node(self):
        raise NotImplementedError(f'Resolve type node is not implemented for {self.__class__}')


class ExprAssign(Expr):

    def __init__(self, obj, value) -> None:
        self.object = obj
        self.value = value
        self.target_decl_node = None

    def resolve_names(self, scope: Scope):
        self.value.resolve_names(scope)
        self.object.resolve_names(scope)
        self.target_decl_node = self.object.resolve_decl_node()


class ExprVar(Expr, Assignable):

    def __init__(self, identifier) -> None:
        self.identifier = identifier
        self.decl_node = None

    def resolve_names(self, scope: Scope):
        self.decl_node = scope.resolve_name(self.resolve_identifier())

    def resolve_identifier(self):
        return self.identifier

    def resolve_decl_node(self):
        return self.decl_node

    def resolve_type_node(self):
        return self.decl_node.type


class ExprAccess(Expr, Assignable):

    def __init__(self, obj, field) -> None:
        self.object = obj
        self.field = field
        self.unit_decl_node = None
        self.field_decl_node = None

    def resolve_names(self, scope: Scope):
        self.object.resolve_names(scope)
        self.unit_decl_node = self.resolve_type_node().unit_decl_node
        self.field_decl_node = self.resolve_decl_node().fields_scope().resolve_name(self.field)

    def resolve_identifier(self):
        return self.object.resolve_identifier()

    def resolve_decl_node(self):
        return self.unit_decl_node

    def resolve_type_node(self):
        return self.object.resolve_type_node()


class ExprArrayAccess(Expr, Assignable):
    def __init__(self, array, index_expr) -> None:
        self.array = array
        self.index_expr = index_expr
        self.array_decl_node = None

    def resolve_names(self, scope: Scope):
        self.array_decl_node = scope.resolve_name(self.resolve_identifier())
        self.index_expr.resolve_names(scope)

    def resolve_identifier(self):
        return self.array.resolve_identifier()

    def resolve_decl_node(self):
        return self.array_decl_node

    def resolve_type_node(self):
        pass


class ExprFnCall(Expr):

    def __init__(self, function_name, args) -> None:
        self.function_name = function_name
        self.args = args
        self.function_decl_node = None

    def resolve_names(self, scope: Scope):
        self.function_decl_node = scope.resolve_name(self.function_name)

        for arg in self.args:
            arg.resolve_names(scope)


class ExprCreateUnit(Expr):

    def __init__(self, unit_name, args) -> None:
        self.unit_name = unit_name
        self.args = args
        self.unit_decl_node = None

    def resolve_names(self, scope: Scope):
        self.unit_decl_node = scope.resolve_name(self.unit_name)

        if self.unit_decl_node:
            for arg in self.args:
                arg.resolve_names(scope)


class CreateUnitArg(Node):

    def __init__(self, unit_name, field, value) -> None:
        self.unit_name = unit_name
        self.field = field
        self.value = value
        self.field_decl_node = None

    def resolve_names(self, scope: Scope):
        unit_decl_node = scope.resolve_name(self.unit_name)
        if unit_decl_node:
            self.field_decl_node = unit_decl_node.fields_scope().resolve_name(self.field)

        self.value.resolve_names(scope)


class Stmnt(Node, ABC):
    pass


class StmntEmpty(Stmnt):

    def resolve_names(self, scope: Scope):
        pass


class StmntDeclVar(Stmnt):

    def __init__(self, type_: Type, name, value=None, is_constant=False) -> None:
        self.type = type_
        self.name = name
        self.value = value
        self.is_constant = is_constant

    def resolve_names(self, scope: Scope):
        scope.add(self.name, self)
        self.type.resolve_names(scope)

        if self.value:
            self.value.resolve_names(scope)


class StmntIf(Stmnt):

    def __init__(self, condition: Expr, stmnt_block, else_clause=None) -> None:
        self.condition = condition
        self.stmnt_block = stmnt_block
        self.else_clause = else_clause

    def resolve_names(self, scope: Scope):
        self.condition.resolve_names(scope)
        self.stmnt_block.resolve_names(scope)
        if self.else_clause:
            self.else_clause.resolve_names(scope)


class StmntControl(Stmnt, ABC):

    def __init__(self, token) -> None:
        self.token = token

    def resolve_names(self, scope: Scope):
        pass


class StmntBreak(StmntControl):
    pass


class StmntContinue(StmntControl):
    pass


class StmntReturn(StmntControl):

    def __init__(self, token, value: Expr = None) -> None:
        super().__init__(token)
        self.value = value

    def resolve_names(self, scope: Scope):
        if self.value:
            self.value.resolve_names(scope)


class StmntExpr(Stmnt):

    def __init__(self, expr: Expr) -> None:
        self.expr = expr

    def resolve_names(self, scope: Scope):
        self.expr.resolve_names(scope)


class StmntToStdout(Stmnt):

    def __init__(self, values: List[Expr]) -> None:
        self.values = values

    def resolve_names(self, scope: Scope):
        for value in self.values:
            value.resolve_names(scope)


class StmntEach(Stmnt):

    def __init__(self, element, array, stmnt_block) -> None:
        self.element = element
        self.array = array
        self.stmnt_block = stmnt_block

    def resolve_names(self, scope: Scope):
        self.element.resolve_names(scope)
        self.array.resolve_names(scope)
        self.stmnt_block.resolve_names(scope)


class StmntWhile(Stmnt):

    def __init__(self, condition, stmnt_block) -> None:
        self.condition = condition
        self.stmnt_block = stmnt_block

    def resolve_names(self, scope: Scope):
        self.condition.resolve_names(scope)
        self.stmnt_block.resolve_names(scope)


class StmntBlock(Node):

    def __init__(self, statements: List[Stmnt]) -> None:
        self.statements = statements

    def resolve_names(self, scope: Scope):
        block_scope = Scope(scope)

        for stmnt in self.statements:
            stmnt.resolve_names(block_scope)


class FunParam(Node):

    def __init__(self, type_: Type, name):
        self.type = type_
        self.name = name

    def resolve_names(self, scope: Scope):
        scope.add(self.name, self)


class Decl(Node, ABC):
    pass


class DeclFun(Decl):

    def __init__(self, name, params: List[FunParam], return_type: Type, body: StmntBlock) -> None:
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body

    def resolve_names(self, scope: Scope):
        fn_scope = Scope(scope)

        for param in self.params:
            param.resolve_names(fn_scope)

        self.body.resolve_names(fn_scope)


class DeclVar(Decl):

    def __init__(self, type_: Type, name, value=None, is_constant=False) -> None:
        self.type = type_
        self.name = name
        self.value = value
        self.is_constant = is_constant

    def resolve_names(self, scope: Scope):
        if self.value:
            self.value.resolve_names(scope)
        scope.add(self.name, self)


class DeclArrayElement(Decl):
    """
    This class is used to represent temporary variable
    which is created when we iterate thought an array
    """

    def __init__(self, name, iterable_node: Expr):
        self.name = name
        self.iterable_node = iterable_node

    def resolve_names(self, scope: Scope):
        scope.add(self.name, self)


class DeclUnitField(Node):

    def __init__(self, type_: Type, name) -> None:
        self.type = type_
        self.name = name

    def resolve_names(self, scope: Scope):
        self.type.resolve_names(scope)
        scope.add(self.name, self)


class DeclUnit(Decl):

    def __init__(self, name, fields: List[DeclUnitField]) -> None:
        self.name = name
        self.fields = fields
        self._fields_scope = None

    def resolve_names(self, scope: Scope):
        self._fields_scope = Scope(scope)
        scope.add(self.name, self)
        for field in self.fields:
            field.resolve_names(self._fields_scope)

    def fields_scope(self):
        return self._fields_scope


class Helper(Node, ABC):

    def resolve_names(self, scope: Scope):
        pass


class HelperInclude(Helper):

    def __init__(self, file_name_token) -> None:
        self.file_name_token = file_name_token

    def resolve_includes(self):
        from lexer.lexer import Lexer
        from parse.parser import Parser

        file_name = self.file_name_token.value

        try:
            with open(file_name) as f:
                content = ''.join(f.readlines())

                lexer = Lexer(content, file_name)
                lexer.lex_all()

                parser = Parser(lexer.tokens)
                root = parser.parse()

                root.resolve_includes()

                return root
        except FileNotFoundError:
            print_error('Include',
                        'File not found',
                        self.file_name_token.line_number,
                        self.file_name_token.offset_in_line,
                        self.file_name_token.file_name)
            raise ValueError


class Program(Node):

    root_elements: List[Union[Decl, Helper]]

    def __init__(self, root_elements: List[Union[Decl, Helper]]) -> None:
        self.root_elements = root_elements

    def resolve_includes(self):
        new_root_elements = []
        for el in self.root_elements:
            included_root = el.resolve_includes()
            if included_root is None:
                new_root_elements.append(el)
                continue

            new_root_elements.extend(included_root.root_elements)
        self.root_elements = new_root_elements

    def resolve_names(self, scope: Scope):

        # register function and unit declarations
        for decl in self.root_elements:
            if isinstance(decl, DeclFun):
                scope.add(decl.name, decl)

        # resolve names of the functions body and assignments expressions
        for decl in self.root_elements:
            decl.resolve_names(scope)
