from abc import ABC
from typing import List, Union

from models import TokenType, Token
from models.scope import Scope
from utils.error_printer import print_error_from_token as print_error, print_error_simple
from utils.list_utils import find_in_list
from utils.type_checking_helpers import unify_types, prepare_for_printing


def handle_typing_error(cause, token):
    print_error('Typing error', cause, token)


class Node(ABC):

    def __init__(self) -> None:
        self._parent = None

    @property
    def parent(self):
        return self._parent

    @property
    def reference_token(self):
        raise NotImplementedError(f'Reference token is not implemented for {self.__class__}')

    def add_children(self, *children):
        for child in children:
            if child is None:
                continue
            child._parent = self

    def find_parent(self, parent_type):
        current_node = self.parent
        while current_node:
            if isinstance(current_node, parent_type):
                return current_node
            current_node = current_node.parent
        return None

    def print(self, ast_printer):
        for key in self.__dict__:
            if key.startswith('_'):
                continue

            val = self.__dict__[key]
            ast_printer.print(key, val)

    def resolve_includes(self):
        return None

    def resolve_names(self, scope: Scope):
        raise NotImplementedError(f'Resolve names not implemented for {self.__class__}')

    def resolve_types(self):
        raise NotImplementedError(f'Resolve types not implemented for {self.__class__}')

    def is_accessible(self):
        return False


class Type(Node, ABC):

    def resolve_types(self):
        return self

    def is_arithmetic(self):
        return False

    def is_comparable(self):
        return False

    def has_value(self):
        return False

    @property
    def reference_token(self):
        return None


class TypeArray(Type):

    def __init__(self, inner_type) -> None:
        super().__init__()
        self.inner_type = inner_type

    def access_type(self) -> Type:
        return self.inner_type

    def resolve_names(self, scope: Scope):
        return self.inner_type.resolve_names(scope)


class TypePrimitive(Type):

    def __init__(self, kind):
        super().__init__()
        self.kind = kind

    def resolve_names(self, scope: Scope):
        pass

    def is_arithmetic(self):
        return self.kind_type == TokenType.PRIMITIVE_INT or \
            self.kind_type == TokenType.PRIMITIVE_FLOAT

    def is_comparable(self):
        return self.kind_type == TokenType.PRIMITIVE_INT or \
            self.kind_type == TokenType.PRIMITIVE_FLOAT

    def has_value(self):
        return self.kind_type != TokenType.PRIMITIVE_VOID

    @property
    def kind_type(self):
        return self.kind.type if isinstance(self.kind, Token) else self.kind

    @property
    def reference_token(self):
        return None


class TypeUnit(Type):

    def __init__(self, unit_name, unit_decl_node=None):
        super().__init__()
        self.unit_name = unit_name
        self.unit_decl_node = unit_decl_node

    def resolve_names(self, scope: Scope):
        self.unit_decl_node = scope.resolve_name(self.unit_name)

    def resolve_types(self):
        return self

    def is_accessible(self):
        return True


class Expr(Node, ABC):
    pass


class ExprBinary(Expr, ABC):
    def __init__(self, left, right) -> None:
        super().__init__()
        self.add_children(left, right)
        self.left = left
        self.right = right

    def resolve_names(self, scope: Scope):
        self.left.resolve_names(scope)
        self.right.resolve_names(scope)

    @property
    def reference_token(self):
        return self.left.reference_token


class ExprBinaryArithmetic(ExprBinary, ABC):

    def resolve_types(self):
        left_type = self.left.resolve_types()
        right_type = self.right.resolve_types()

        if not left_type:
            return None

        reference_token = self.left.reference_token
        if left_type.is_arithmetic():
            unify_types(reference_token, left_type, right_type, 'Right operand type does not match left\'s one')
        else:
            handle_typing_error(
                f'Cannot perform arithmetic operations with type "{prepare_for_printing(left_type)}"',
                reference_token
            )
        return left_type


class ExprBinaryComparison(ExprBinary, ABC):

    def resolve_types(self):
        left_type = self.left.resolve_types()
        right_type = self.right.resolve_types()

        if not left_type:
            return None

        reference_token = self.left.reference_token
        if left_type.is_comparable():
            unify_types(reference_token, left_type, right_type, 'Right operand type does not match left\'s one')
        else:
            handle_typing_error(
                f'Cannot perform compare operations with {self.left.__class__.__name__}',
                reference_token
            )
        return TypePrimitive(TokenType.PRIMITIVE_BOOL)


class ExprBinaryEquality(ExprBinary, ABC):

    def resolve_types(self):
        left_type = self.left.resolve_types()
        right_type = self.right.resolve_types()

        if not left_type:
            return None

        reference_token = self.left.reference_token
        if left_type.has_value():
            unify_types(reference_token, left_type, right_type, 'Right operand type does not match left\'s one')
        else:
            handle_typing_error(
                f'Cannot perform equality operations with {self.left.__class__.__name__}',
                reference_token
            )
        return TypePrimitive(TokenType.PRIMITIVE_BOOL)


class ExprBinaryLogic(ExprBinary, ABC):

    def resolve_types(self):
        left_type = self.left.resolve_types()
        right_type = self.right.resolve_types()

        if not left_type:
            return None

        unify_types(self.left.reference_token, left_type, TypePrimitive(TokenType.PRIMITIVE_BOOL))
        unify_types(self.right.reference_token, right_type, TypePrimitive(TokenType.PRIMITIVE_BOOL))

        return TypePrimitive(TokenType.PRIMITIVE_BOOL)


class ExprOr(ExprBinaryLogic):
    pass


class ExprAnd(ExprBinaryLogic):
    pass


class ExprEq(ExprBinaryEquality):
    pass


class ExprNe(ExprBinaryEquality):
    pass


class ExprGt(ExprBinaryComparison):
    pass


class ExprGe(ExprBinaryComparison):
    pass


class ExprLt(ExprBinaryComparison):
    pass


class ExprLe(ExprBinaryComparison):
    pass


class ExprAdd(ExprBinaryArithmetic):
    pass


class ExprSub(ExprBinaryArithmetic):
    pass


class ExprMul(ExprBinaryArithmetic):
    pass


class ExprDiv(ExprBinaryArithmetic):
    pass


class ExprMod(ExprBinaryArithmetic):
    pass


class ExprPow(ExprBinaryArithmetic):
    pass


class ExprUnaryOp(Expr):

    def __init__(self, expr) -> None:
        super().__init__()
        self.add_children(expr)
        self.expr = expr

    def resolve_names(self, scope: Scope):
        self.expr.resolve_names(scope)

    @property
    def reference_token(self):
        return self.expr.reference_token

    def resolve_types(self):
        type_ = self.expr.resolve_types()
        if type_.is_arithmetic():
            return type_

        handle_typing_error('Unary operators applicable only to int and float', self.reference_token)


class ExprUPlus(ExprUnaryOp):
    pass


class ExprUMinus(ExprUnaryOp):
    pass


class ExprLit(Expr, ABC):

    def __init__(self, value):
        super().__init__()
        self.value = value

    @property
    def reference_token(self):
        return self.value

    def resolve_names(self, scope: Scope):
        pass

    @property
    def kind(self):
        raise NotImplementedError(f'Kind property not implemented for {self.__class__}')

    def resolve_types(self):
        return TypePrimitive(self.kind)


class ExprLitStr(ExprLit):

    @property
    def kind(self):
        return TokenType.PRIMITIVE_STRING


class ExprLitFloat(ExprLit):

    @property
    def kind(self):
        return TokenType.PRIMITIVE_FLOAT


class ExprLitInt(ExprLit):

    @property
    def kind(self):
        return TokenType.PRIMITIVE_INT


class ExprLitBool(ExprLit):

    @property
    def kind(self):
        return TokenType.PRIMITIVE_BOOL


class ExprLitArray(ExprLit):

    def __init__(self, value, start_token):
        super().__init__(value)
        self._start_token = start_token

    def resolve_names(self, scope: Scope):
        for el in self.value:
            el.resolve_names(scope)

    def resolve_types(self):
        if len(self.value):
            first_val_type = self.value[0].resolve_types()
            for i in range(1, len(self.value)):
                unify_types(self.value[i].reference_token, first_val_type, self.value[i].resolve_types())
            return TypeArray(first_val_type) if first_val_type else None
        return None

    @property
    def kind(self):
        if len(self.value):
            return self.value[0].resolve_types()
        return None

    @property
    def reference_token(self):
        if len(self.value):
            return self.value[0].reference_token
        return self._start_token


class ExprFromStdin(Expr):

    @property
    def reference_token(self):
        return None

    def resolve_types(self):
        return None

    def resolve_names(self, scope: Scope):
        pass


class Assignable(ABC):
    def resolve_identifier(self):
        raise NotImplementedError(f'Resolve identifier is not implemented for {self.__class__}')


class ExprAssign(Expr):

    def __init__(self, obj, value) -> None:
        super().__init__()
        self.add_children(obj, value)
        self.object = obj
        self.value = value

    def resolve_names(self, scope: Scope):
        self.value.resolve_names(scope)
        obj_decl = self.object.resolve_names(scope)
        if hasattr(obj_decl, 'is_constant') and obj_decl.is_constant:
            print_error(
                'Constant',
                'Assign to constant variable',
                self.reference_token
            )

    def resolve_types(self):
        obj_type = self.object.resolve_types()
        value_type = self.value.resolve_types()
        unify_types(self.object.reference_token, obj_type, value_type)
        return value_type

    @property
    def reference_token(self):
        return self.object.reference_token


class ExprVar(Expr, Assignable):

    def __init__(self, identifier) -> None:
        super().__init__()
        self.add_children(identifier)
        self.identifier = identifier
        self.decl_node = None

    def resolve_names(self, scope: Scope):
        self.decl_node = scope.resolve_name(self.resolve_identifier())
        return self.decl_node

    def resolve_types(self):
        if self.decl_node:
            if isinstance(self.decl_node, (DeclVar, StmntDeclVar)):
                return self.decl_node.type
            else:
                handle_typing_error(f'Not a valid type for variable', self.reference_token)

    def resolve_identifier(self):
        return self.identifier

    @property
    def reference_token(self):
        return self.identifier

    def is_accessible(self):
        return isinstance(self.decl_node.type, TypeUnit)


class ExprAccess(Expr, Assignable):

    def __init__(self, obj, field) -> None:
        super().__init__()
        self.add_children(obj, field)
        self.object = obj
        self.field = field
        self.field_decl_node = None

    def resolve_names(self, scope: Scope):
        object_decl_node = self.object.resolve_names(scope)

        if not object_decl_node or not isinstance(object_decl_node.type, (TypeUnit, TypeArray)):
            # print error maybe
            return None

        if isinstance(object_decl_node.type, TypeArray):
            unit_decl_node = object_decl_node.type.inner_type.unit_decl_node
        else:
            unit_decl_node = object_decl_node.type.unit_decl_node
        self.field_decl_node = unit_decl_node.fields_scope.resolve_name(self.field)
        return self.field_decl_node

    def resolve_identifier(self):
        return self.object.resolve_identifier()

    @property
    def reference_token(self):
        return self.field

    def is_accessible(self):
        return self.field_decl_node and self.field_decl_node.is_accessible()

    def resolve_types(self):
        type_ = self.object.resolve_types()
        if not type_ or not type_.is_accessible():
            handle_typing_error('You cannot access this type', self.object.reference_token)
        return self.field_decl_node.type if self.field_decl_node else None


class ExprArrayAccess(Expr, Assignable):

    def __init__(self, array, index_expr) -> None:
        super().__init__()
        self.add_children(array, index_expr)
        self.array = array
        self.index_expr = index_expr

    def resolve_names(self, scope: Scope):
        self.index_expr.resolve_names(scope)
        return self.array.resolve_names(scope)

    def resolve_identifier(self):
        return self.array.resolve_identifier()

    def resolve_types(self):
        # check if array variable is Iterable
        array_type = self.array.resolve_types()
        if not isinstance(array_type, TypeArray):
            handle_typing_error(f'You cannot access {array_type.__class__.__name__}', self.reference_token)
            return None

        # check if index expr evaluates to int
        unify_types(self.index_expr.reference_token,
                    TypePrimitive(TokenType.PRIMITIVE_INT),
                    self.index_expr.resolve_types())

        return array_type.inner_type.resolve_types()

    def is_accessible(self):
        return self.array.is_accessible()

    @property
    def reference_token(self):
        return self.array.reference_token


class ExprFnCall(Expr):

    def __init__(self, function_name, args) -> None:
        super().__init__()
        self.add_children(*args)
        self.function_name = function_name
        self.args = args
        self.function_decl_node = None

    def resolve_names(self, scope: Scope):
        self.function_decl_node = scope.resolve_name(self.function_name)

        for arg in self.args:
            arg.resolve_names(scope)

    def resolve_types(self):
        if not self.function_decl_node:
            return
        if not isinstance(self.function_decl_node, DeclFun):
            handle_typing_error(f'Item "{self.function_name}" is not a function', self.reference_token)
            return
        params = self.function_decl_node.params
        if len(params) != len(self.args):
            handle_typing_error(f'Wrong number of arguments. Expected: {len(params)}, got: {len(self.args)}', self.reference_token)
        else:
            for arg in self.args:
                arg.resolve_types()
        return self.function_decl_node.return_type

    @property
    def reference_token(self):
        return self.function_name


class ExprCreateUnit(Expr):

    def __init__(self, unit_name, args) -> None:
        super().__init__()
        self.add_children(*args)
        self.unit_name = unit_name
        self.args = args
        self.unit_decl_node = None

    def resolve_names(self, scope: Scope):
        self.unit_decl_node = scope.resolve_name(self.unit_name)

        if self.unit_decl_node:
            for arg in self.args:
                arg.resolve_names(scope)

    def resolve_types(self):
        if not self.unit_decl_node:
            return None

        if not isinstance(self.unit_decl_node, DeclUnit):
            handle_typing_error(f'Item "{self.unit_name}" is not a unit', self.reference_token)
            return None

        fields = self.unit_decl_node.fields

        # check if args count matches fields count
        if fields and len(self.unit_decl_node.fields) != len(self.args):
            handle_typing_error('Wrong number of arguments', self.reference_token)
            return None

        for field in fields:
            arg_for_field = find_in_list(self.args, lambda a: field.name.value == a.field.value)
            if not arg_for_field:
                handle_typing_error(f'There is no argument for \'{field.name.value}\'', self.reference_token)
                continue

            value_type = arg_for_field.value.resolve_types()
            unify_types(arg_for_field.reference_token, field.type, value_type)

        return TypeUnit(self.unit_decl_node.name, self.unit_decl_node)

    @property
    def reference_token(self):
        return self.unit_name


class CreateUnitArg(Node):

    def __init__(self, unit_name, field, value) -> None:
        super().__init__()
        self.add_children(field, value)
        self.unit_name = unit_name
        self.field = field
        self.value = value
        self.field_decl_node = None

    def resolve_names(self, scope: Scope):
        unit_decl_node = scope.resolve_name(self.unit_name)
        if unit_decl_node:
            self.field_decl_node = unit_decl_node.fields_scope.resolve_name(self.field)

        self.value.resolve_names(scope)

    def resolve_types(self):
        return self.value.resolve_types()

    @property
    def reference_token(self):
        return self.value.reference_token


class Stmnt(Node, ABC):
    pass


class StmntEmpty(Stmnt):

    def resolve_names(self, scope: Scope):
        pass

    def resolve_types(self):
        pass

    @property
    def reference_token(self):
        return None


class StmntDeclVar(Stmnt):

    def __init__(self, type_: Type, name, value=None, is_constant=False) -> None:
        super().__init__()
        self.add_children(type_)
        self.type = type_
        self.name = name
        self.value = value
        self.is_constant = is_constant

    def resolve_names(self, scope: Scope):
        scope.add(self.name, self)
        self.type.resolve_names(scope)

        if self.value:
            self.value.resolve_names(scope)

    def resolve_types(self):
        if self.value:
            value_type = self.value.resolve_types()
            unify_types(self.reference_token, self.type, value_type)

    @property
    def reference_token(self):
        return self.name


class StmntIf(Stmnt):

    def __init__(self, condition: Expr, stmnt_block, else_clause=None) -> None:
        super().__init__()
        self.add_children(condition, stmnt_block, else_clause)
        self.condition = condition
        self.stmnt_block = stmnt_block
        self.else_clause = else_clause

    def resolve_names(self, scope: Scope):
        self.condition.resolve_names(scope)
        self.stmnt_block.resolve_names(scope)
        if self.else_clause:
            self.else_clause.resolve_names(scope)

    def resolve_types(self):
        condition_type = self.condition.resolve_types()
        unify_types(self.condition.reference_token, TypePrimitive(TokenType.PRIMITIVE_BOOL), condition_type)
        self.stmnt_block.resolve_types()
        if self.else_clause:
            self.else_clause.resolve_types()

    @property
    def reference_token(self):
        return self.condition.reference_token


class StmntControl(Stmnt, ABC):

    def __init__(self, token) -> None:
        super().__init__()
        self.token = token

    def resolve_types(self):
        pass

    @property
    def reference_token(self):
        return self.token

    def _outer_loop(self):
        outer_while = self.find_parent(StmntWhile)
        if outer_while:
            return outer_while

        return self.find_parent(StmntEach)


class StmntBreak(StmntControl):

    def resolve_names(self, scope: Scope):
        if not self._outer_loop():
            print_error(
                'Invalid keyword',
                '\'break\' keyword has to be in a loop',
                self.reference_token
            )


class StmntContinue(StmntControl):

    def resolve_names(self, scope: Scope):
        if not self._outer_loop():
            print_error(
                'Invalid keyword',
                '\'continue\' keyword has to be in a loop',
                self.reference_token
            )


class StmntReturn(StmntControl):

    def __init__(self, token, value: Expr = None) -> None:
        super().__init__(token)
        self.add_children(value)
        self.value = value

    def resolve_names(self, scope: Scope):
        if self.value:
            self.value.resolve_names(scope)

    def resolve_types(self):
        ret_type = self.find_parent(DeclFun).return_type
        if self.value:
            val_type = self.value.resolve_types()
        else:
            val_type = TypePrimitive(TokenType.PRIMITIVE_VOID)
        unify_types(self.token, ret_type, val_type)


class StmntExpr(Stmnt):

    def __init__(self, expr: Expr) -> None:
        super().__init__()
        self.add_children(expr)
        self.expr = expr

    def resolve_names(self, scope: Scope):
        self.expr.resolve_names(scope)

    def resolve_types(self):
        return self.expr.resolve_types()

    @property
    def reference_token(self):
        return self.expr.reference_token


class StmntToStdout(Stmnt):

    def __init__(self, values: List[Expr]) -> None:
        super().__init__()
        self.add_children(*values)
        self.values = values

    def resolve_names(self, scope: Scope):
        for value in self.values:
            value.resolve_names(scope)

    def resolve_types(self):
        for value in self.values:
            value.resolve_types()

    @property
    def reference_token(self):
        return self.values[0].reference_token if len(self.values) else None


class StmntEach(Stmnt):

    def __init__(self, element, array, stmnt_block) -> None:
        super().__init__()
        self.add_children(element, array, stmnt_block)
        self.element = element
        self.array = array
        self.stmnt_block = stmnt_block

    def resolve_names(self, scope: Scope):
        self.element.resolve_names(scope)
        self.array.resolve_names(scope)
        self.stmnt_block.resolve_names(scope)

    def resolve_types(self):
        self.element.resolve_types()
        self.array.resolve_types()
        self.stmnt_block.resolve_types()

    @property
    def reference_token(self):
        return self.element.reference_token


class StmntWhile(Stmnt):

    def __init__(self, condition, stmnt_block) -> None:
        super().__init__()
        self.add_children(condition, stmnt_block)
        self.condition = condition
        self.stmnt_block = stmnt_block

    def resolve_names(self, scope: Scope):
        self.condition.resolve_names(scope)
        self.stmnt_block.resolve_names(scope)

    def resolve_types(self):
        condition_type = self.condition.resolve_types()
        unify_types(self.condition.reference_token, TypePrimitive(TokenType.PRIMITIVE_BOOL), condition_type)

        self.stmnt_block.resolve_types()

    @property
    def reference_token(self):
        return self.condition.reference_token


class StmntBlock(Node):

    def __init__(self, statements: List[Stmnt]) -> None:
        super().__init__()
        self.add_children(*statements)
        self.statements = statements

    def resolve_names(self, scope: Scope):
        block_scope = Scope(scope)

        for stmnt in self.statements:
            stmnt.resolve_names(block_scope)

    def resolve_types(self):
        for stmnt in self.statements:
            stmnt.resolve_types()

    @property
    def reference_token(self):
        return self.statements[0].reference_token if len(self.statements) else None


class FunParam(Node):

    def __init__(self, type_: Type, name):
        super().__init__()
        self.add_children(type_)
        self.type = type_
        self.name = name

    def resolve_names(self, scope: Scope):
        scope.add(self.name, self)

    def resolve_types(self):
        pass

    @property
    def reference_token(self):
        return self.name


class Decl(Node, ABC):
    pass


class DeclFun(Decl):

    def __init__(self, name, params: List[FunParam], return_type: Type, body: StmntBlock) -> None:
        super().__init__()
        self.add_children(*params, return_type, body)
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body

    def resolve_names(self, scope: Scope):
        fn_scope = Scope(scope)

        for param in self.params:
            param.resolve_names(fn_scope)

        self.body.resolve_names(fn_scope)

    def resolve_types(self):
        self.body.resolve_types()

    @property
    def reference_token(self):
        return self.name


class DeclVar(Decl):

    def __init__(self, type_: Type, name, value=None, is_constant=False) -> None:
        super().__init__()
        self.add_children(type_, value)
        self.type = type_
        self.name = name
        self.value = value
        self.is_constant = is_constant

    def resolve_names(self, scope: Scope):
        if self.value:
            self.value.resolve_names(scope)
        scope.add(self.name, self)

    def resolve_types(self):
        if self.value:
            return self.value.resolve_types()

    @property
    def reference_token(self):
        return self.name


class DeclArrayElement(Decl):
    """
    This class is used to represent temporary variable
    which is created when we iterate thought an array
    """

    def __init__(self, name, iterable_node: Expr):
        super().__init__()
        self.add_children(iterable_node)
        self.name = name
        self.iterable_node = iterable_node
        self._type = None

    def resolve_names(self, scope: Scope):
        scope.add(self.name, self)

    def resolve_types(self):
        array_type = self.iterable_node.resolve_types()
        if array_type:
            self._type = array_type.inner_type
            return self._type
        return None

    @property
    def type(self):
        return self._type

    @property
    def reference_token(self):
        return self.name


class DeclUnitField(Node):

    def __init__(self, type_: Type, name) -> None:
        super().__init__()
        self.add_children(type_)
        self.type = type_
        self.name = name

    def resolve_names(self, scope: Scope):
        self.type.resolve_names(scope)
        scope.add(self.name, self)

    def is_accessible(self):
        return self.type.is_accessible()

    def resolve_types(self):
        pass

    @property
    def reference_token(self):
        return self.name


class DeclUnit(Decl):

    def __init__(self, name, fields: List[DeclUnitField]) -> None:
        super().__init__()
        self.add_children(*fields)
        self.name = name
        self.fields = fields
        self._fields_scope = None

    def resolve_names(self, scope: Scope):
        self._fields_scope = Scope(scope)
        scope.add(self.name, self)
        for field in self.fields:
            field.resolve_names(self._fields_scope)

    @property
    def fields_scope(self):
        return self._fields_scope

    def resolve_types(self):
        return None

    @property
    def reference_token(self):
        return self.name


class Helper(Node, ABC):
    """
    Helpers are gone in semantic checking phase
    """
    def resolve_names(self, scope: Scope):
        pass

    def resolve_types(self):
        pass

    @property
    def reference_token(self):
        return None


class HelperInclude(Helper):

    def __init__(self, file_name_token) -> None:
        super().__init__()
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
            print_error('Include', 'File not found', self.file_name_token)
            raise ValueError


class Program(Node):
    root_elements: List[Union[Decl, Helper]]

    def __init__(self, root_elements: List[Union[Decl, Helper]]) -> None:
        super().__init__()
        self.add_children(*root_elements)
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

    def resolve_types(self):
        for el in self.root_elements:
            el.resolve_types()

    def check_for_entry_point(self):
        main_fns = [el for el in self.root_elements
                    if isinstance(el, DeclFun) and el.name.value == 'main']

        if len(main_fns) != 1:
            return print_error_simple(
                'Entry point',
                'You have to provide single function with a name \'main\' for a program entry point'
            )

        main_fn = main_fns[0]

        ret_type = main_fn.return_type
        returns_int = isinstance(ret_type, TypePrimitive) and ret_type.kind_type == TokenType.PRIMITIVE_INT
        if not returns_int:
            print_error(
                'Entry point',
                '\'main\' function has to return int',
                main_fn.reference_token
            )

        if len(main_fn.params) != 0:
            print_error(
                'Entry point',
                '\'main\' function must not take any params',
                main_fn.reference_token
            )

    @property
    def reference_token(self):
        return None
