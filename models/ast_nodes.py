from abc import ABC
from typing import List, Union

from codegen.code_writer import CodeWriter, Label
from models import TokenType, Token
from models.instructions import InstructionType
from models.scope import Scope
from models.slot_dispenser import SlotDispenser
from utils.error_printer import print_error_from_token as print_error, print_error_simple
from utils.list_utils import find_in_list
from utils.type_checking_helpers import unify_types, prepare_for_printing

global_slot_dispenser = SlotDispenser()
stack_slot_dispenser = SlotDispenser()


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

    def write_code(self, code_writer: CodeWriter):
        raise NotImplementedError(f'Write code not implemented for {self.__class__}')

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

    def is_valid_var_type(self):
        return True

    @property
    def reference_token(self):
        return None

    def write_code(self, code_writer: CodeWriter):
        pass


class TypeArray(Type):

    def __init__(self, inner_type, size) -> None:
        super().__init__()
        self.inner_type = inner_type
        self.size = size

    def access_type(self) -> Type:
        return self.inner_type

    def resolve_names(self, scope: Scope):
        return self.inner_type.resolve_names(scope)

    @property
    def length(self):
        return int(self.size.value if isinstance(self.size, Token) else self.size)

    def resolve_types(self):
        if self.length <= 0:
            handle_typing_error('Array size must be bigger than 0', self.size)
            return None
        return self


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

    def is_valid_var_type(self):
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


class ExprNumeric(Expr, ABC):

    def write_code_for_type(self, type_, code_writer):
        if not isinstance(type_, TypePrimitive):
            raise NotImplementedError(f'There are no numeric expr for: {type_.__class__}')

        kind = type_.kind_type
        if kind == TokenType.PRIMITIVE_INT:
            instruction_type = self.instruction_type_for_int
        elif kind == TokenType.PRIMITIVE_FLOAT:
            instruction_type = self.instruction_type_for_float
        else:
            raise NotImplementedError(f'There are no binary operators for: {kind}')
        code_writer.write(instruction_type)

    @property
    def instruction_type_for_int(self):
        raise NotImplementedError(f'Expr binary instruction type for int not implemented for {self.__class__}')

    @property
    def instruction_type_for_float(self):
        raise NotImplementedError(f'Expr binary instruction type for float not implemented for {self.__class__}')


class ExprBinaryNumeric(ExprBinary, ExprNumeric, ABC):

    def write_code(self, code_writer: CodeWriter):
        self.left.write_code(code_writer)
        self.right.write_code(code_writer)

        type_ = self.left.resolve_types()
        self.write_code_for_type(type_, code_writer)


class ExprBinaryArithmetic(ExprBinaryNumeric, ABC):

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


class ExprBinaryComparison(ExprBinaryNumeric, ABC):

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

    def write_code(self, code_writer: CodeWriter):
        self.left.write_code(code_writer)
        self.right.write_code(code_writer)
        code_writer.write(self.instruction_type)

    @property
    def instruction_type(self):
        raise NotImplementedError(f'Instruction type is not implemented for: {self.__class__} ')


class ExprBinaryLogic(ExprBinary, ABC):

    def resolve_types(self):
        left_type = self.left.resolve_types()
        right_type = self.right.resolve_types()

        if not left_type:
            return None

        unify_types(self.left.reference_token, left_type, TypePrimitive(TokenType.PRIMITIVE_BOOL))
        unify_types(self.right.reference_token, right_type, TypePrimitive(TokenType.PRIMITIVE_BOOL))

        return TypePrimitive(TokenType.PRIMITIVE_BOOL)

    def write_code(self, code_writer: CodeWriter):
        self.left.write_code(code_writer)
        self.right.write_code(code_writer)
        code_writer.write(self.instruction_type)

    @property
    def instruction_type(self):
        raise NotImplementedError(f'Instruction type is not implemented for: {self.__class__} ')


class ExprOr(ExprBinaryLogic):

    @property
    def instruction_type(self):
        return InstructionType.OR


class ExprAnd(ExprBinaryLogic):

    @property
    def instruction_type(self):
        return InstructionType.AND


class ExprEq(ExprBinaryEquality):

    @property
    def instruction_type(self):
        return InstructionType.EQ


class ExprNe(ExprBinaryEquality):

    @property
    def instruction_type(self):
        return InstructionType.NE


class ExprGt(ExprBinaryComparison):

    @property
    def instruction_type_for_int(self):
        return InstructionType.GT_INT

    @property
    def instruction_type_for_float(self):
        return InstructionType.GT_FLOAT


class ExprGe(ExprBinaryComparison):

    @property
    def instruction_type_for_int(self):
        return InstructionType.GE_INT

    @property
    def instruction_type_for_float(self):
        return InstructionType.GE_FLOAT


class ExprLt(ExprBinaryComparison):

    @property
    def instruction_type_for_int(self):
        return InstructionType.LT_INT

    @property
    def instruction_type_for_float(self):
        return InstructionType.LT_FLOAT


class ExprLe(ExprBinaryComparison):

    @property
    def instruction_type_for_int(self):
        return InstructionType.LE_INT

    @property
    def instruction_type_for_float(self):
        return InstructionType.LE_FLOAT


class ExprAdd(ExprBinaryArithmetic):

    @property
    def instruction_type_for_int(self):
        return InstructionType.ADD_INT

    @property
    def instruction_type_for_float(self):
        return InstructionType.ADD_FLOAT


class ExprSub(ExprBinaryArithmetic):

    @property
    def instruction_type_for_int(self):
        return InstructionType.SUB_INT

    @property
    def instruction_type_for_float(self):
        return InstructionType.SUB_FLOAT


class ExprMul(ExprBinaryArithmetic):

    @property
    def instruction_type_for_int(self):
        return InstructionType.MUL_INT

    @property
    def instruction_type_for_float(self):
        return InstructionType.MUL_FLOAT


class ExprDiv(ExprBinaryArithmetic):

    @property
    def instruction_type_for_int(self):
        return InstructionType.DIV_INT

    @property
    def instruction_type_for_float(self):
        return InstructionType.DIV_FLOAT


class ExprMod(ExprBinaryArithmetic):

    @property
    def instruction_type_for_int(self):
        return InstructionType.MOD_INT

    @property
    def instruction_type_for_float(self):
        return InstructionType.MOD_FLOAT


class ExprPow(ExprBinaryArithmetic):

    @property
    def instruction_type_for_int(self):
        return InstructionType.POW_INT

    @property
    def instruction_type_for_float(self):
        return InstructionType.POW_FLOAT


class ExprUnaryOp(ExprNumeric, Expr, ABC):

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

    def write_code(self, code_writer: CodeWriter):
        self.expr.write_code(code_writer)

        type_ = self.expr.resolve_types()
        self.write_code_for_type(type_, code_writer)


class ExprUPlus(ExprUnaryOp):

    @property
    def instruction_type_for_int(self):
        return InstructionType.UNARY_PLUS_INT

    @property
    def instruction_type_for_float(self):
        return InstructionType.UNARY_PLUS_FLOAT


class ExprUMinus(ExprUnaryOp):

    @property
    def instruction_type_for_int(self):
        return InstructionType.UNARY_MINUS_INT

    @property
    def instruction_type_for_float(self):
        return InstructionType.UNARY_MINUS_FLOAT


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

    def write_code(self, code_writer: CodeWriter):
        code_writer.write(InstructionType.PUSH_STRING, self.value.value)


class ExprLitFloat(ExprLit):

    @property
    def kind(self):
        return TokenType.PRIMITIVE_FLOAT

    def write_code(self, code_writer: CodeWriter):
        code_writer.write(InstructionType.PUSH_FLOAT, float(self.value.value))


class ExprLitInt(ExprLit):

    @property
    def kind(self):
        return TokenType.PRIMITIVE_INT

    def write_code(self, code_writer: CodeWriter):
        code_writer.write(InstructionType.PUSH_INT, int(self.value.value))


class ExprLitBool(ExprLit):

    @property
    def kind(self):
        return TokenType.PRIMITIVE_BOOL

    def write_code(self, code_writer: CodeWriter):
        value = self.value.type == TokenType.CONSTANT_TRUE
        code_writer.write(InstructionType.PUSH_BOOL, value)


class ExprLitArray(ExprLit):

    def __init__(self, value, start_token):
        super().__init__(value)
        self._start_token = start_token

    def resolve_names(self, scope: Scope):
        for el in self.value:
            el.resolve_names(scope)

    def resolve_types(self):
        array_size = len(self.value)
        if array_size > 0:
            first_val_type = self.value[0].resolve_types()
            for i in range(1, len(self.value)):
                unify_types(self.value[i].reference_token, first_val_type, self.value[i].resolve_types())
            return TypeArray(first_val_type, array_size) if first_val_type else None
        else:
            handle_typing_error('Array cannot be empty', self.reference_token)

    def write_code(self, code_writer: CodeWriter):
        for el in reversed(self.value):
            el.write_code(code_writer)

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

    def write_code(self, code_writer: CodeWriter):
        self.object.write_assigment_code(code_writer, self.value)


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
            if isinstance(self.decl_node, (DeclVar, StmntDeclVar, FunParam)):
                return self.decl_node.type
            else:
                handle_typing_error(f'Not a valid type for variable', self.reference_token)

    def resolve_identifier(self):
        return self.identifier

    @property
    def reference_token(self):
        return self.identifier

    @property
    def is_local(self):
        return type(self.decl_node) == StmntDeclVar

    @property
    def type(self):
        return self.decl_node.type

    @property
    def slot(self):
        if self.is_local:
            return self.decl_node.stack_slot
        return self.decl_node.global_slot

    def is_accessible(self):
        return isinstance(self.decl_node.type, TypeUnit)

    def write_assigment_code(self, code_writer, value):
        value.write_code(code_writer)
        if self.is_local:
            if isinstance(self.type, TypeArray):
                code_writer.write(InstructionType.ARRAY_FILL_LOCAL, self.slot, self.type.length)
            else:
                code_writer.write(InstructionType.SET_LOCAL, self.slot)
        else:
            if isinstance(self.type, TypeArray):
                code_writer.write(InstructionType.ARRAY_FILL_GLOBAL, self.slot, self.type.length)
            else:
                code_writer.write(InstructionType.SET_GLOBAL, self.slot)


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

    def write_assigment_code(self, code_writer, value):
        value.write_code(code_writer)
        self.index_expr.write_code(code_writer)
        if self.array.is_local:
            code_writer.write(InstructionType.ARRAY_SET_VALUE_LOCAL, self.array.slot)
        else:
            code_writer.write(InstructionType.ARRAY_SET_VALUE_GLOBAL, self.array.slot)


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
            return None
        if not isinstance(self.function_decl_node, DeclFun):
            handle_typing_error(f'Item "{self.function_name}" is not a function', self.reference_token)
            return None
        params = self.function_decl_node.params
        if len(params) != len(self.args):
            handle_typing_error(
                f'Wrong number of arguments. Expected: {len(params)}, got: {len(self.args)}',
                self.reference_token
            )
        else:
            for arg in self.args:
                arg.resolve_types()
        return self.function_decl_node.return_type

    def write_code(self, code_writer: CodeWriter):
        code_writer.write(InstructionType.FN_CALL_BEGIN)
        for arg in self.args:
            arg.write_code(code_writer)
        code_writer.write(InstructionType.FN_CALL, self.function_decl_node.label, len(self.args))

    @property
    def reference_token(self):
        return self.function_name

    @property
    def return_type(self):
        return self.function_decl_node.return_type


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
            if not field.type.is_valid_var_type():
                continue

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

    def write_code(self, code_writer: CodeWriter):
        pass


class StmntDeclVar(Stmnt):

    def __init__(self, type_: Type, name, value=None, is_constant=False) -> None:
        super().__init__()
        self.add_children(type_)
        self.type = type_
        self.name = name
        self.value = value
        self.is_constant = is_constant
        self.stack_slot = 0

    def resolve_names(self, scope: Scope):
        self.type.resolve_names(scope)
        if self.value:
            self.value.resolve_names(scope)

        scope.add(self.name, self)
        self.stack_slot = stack_slot_dispenser.get_slot()

    def resolve_types(self):
        self.type.resolve_types()
        if not self.type.is_valid_var_type():
            handle_typing_error('Cannot create a variable of the given type', self.reference_token)
            return None

        if self.value:
            value_type = self.value.resolve_types()
            unify_types(self.reference_token, self.type, value_type)

    def write_code(self, code_writer: CodeWriter):
        if self.value:
            self.value.write_code(code_writer)
            if isinstance(self.type, TypeArray):
                code_writer.write(InstructionType.ARRAY_FILL_LOCAL, self.stack_slot, self.type.length)
            else:
                code_writer.write(InstructionType.SET_LOCAL, self.stack_slot)

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

    def write_code(self, code_writer: CodeWriter):
        else_label = Label()
        end_label = Label()
        self.condition.write_code(code_writer)
        code_writer.write(InstructionType.JZ, else_label)
        self.stmnt_block.write_code(code_writer)
        code_writer.write(InstructionType.JMP, end_label)
        code_writer.place_label(else_label)
        if self.else_clause:
            self.else_clause.write_code(code_writer)
        code_writer.place_label(end_label)

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

    def write_code(self, code_writer: CodeWriter):
        _, end_label = code_writer.current_loop()
        code_writer.write(InstructionType.JMP, end_label)


class StmntContinue(StmntControl):

    def resolve_names(self, scope: Scope):
        if not self._outer_loop():
            print_error(
                'Invalid keyword',
                '\'continue\' keyword has to be in a loop',
                self.reference_token
            )

    def write_code(self, code_writer: CodeWriter):
        start_label, _ = code_writer.current_loop()
        code_writer.write(InstructionType.JMP, start_label)


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

    def write_code(self, code_writer: CodeWriter):
        if self.value:
            self.value.write_code(code_writer)
            code_writer.write(InstructionType.RET_VALUE)
        else:
            code_writer.write(InstructionType.RET)


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

    def write_code(self, code_writer: CodeWriter):
        if isinstance(self.expr, ExprFnCall):
            self.expr.write_code(code_writer)
            if self.expr.return_type.kind_type != TokenType.PRIMITIVE_VOID:
                code_writer.write(InstructionType.POP)
        elif isinstance(self.expr, (ExprLit, ExprArrayAccess, ExprVar)):
            pass  # no-op
        elif isinstance(self.expr, ExprAssign):
            self.expr.write_code(code_writer)
        else:
            self.expr.write_code(code_writer)
            code_writer.write(InstructionType.POP)


class StmntToStdout(Stmnt):

    def __init__(self, token, values: List[Expr]) -> None:
        super().__init__()
        self.add_children(*values)
        self.token = token
        self.values = values

    def resolve_names(self, scope: Scope):
        for value in self.values:
            value.resolve_names(scope)

    def resolve_types(self):
        if len(self.values) == 0:
            handle_typing_error("To stdout operator has to receive at least one value", self.reference_token)

        for value in self.values:
            value.resolve_types()

    @property
    def reference_token(self):
        return self.token

    def write_code(self, code_writer: CodeWriter):
        for value in self.values:
            value.write_code(code_writer)
        code_writer.write(InstructionType.TO_STDOUT, len(self.values))


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

    def write_code(self, code_writer: CodeWriter):
        start_label = Label()
        end_label = Label()

        code_writer.start_loop(start_label, end_label)
        code_writer.place_label(start_label)
        self.condition.write_code(code_writer)
        code_writer.write(InstructionType.JZ, end_label)
        self.stmnt_block.write_code(code_writer)
        code_writer.write(InstructionType.JMP, start_label)
        code_writer.place_label(end_label)
        code_writer.end_loop()

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

    def write_code(self, code_writer: CodeWriter):
        for stmnt in self.statements:
            stmnt.write_code(code_writer)

    @property
    def reference_token(self):
        return self.statements[0].reference_token if len(self.statements) else None


class FunParam(Node):

    def __init__(self, type_: Type, name):
        super().__init__()
        self.add_children(type_)
        self.type = type_
        self.name = name
        self.stack_slot = 0

    def resolve_names(self, scope: Scope):
        scope.add(self.name, self)

    def resolve_types(self):
        if not self.type.is_valid_var_type():
            handle_typing_error('Cannot create a parameter of the given type', self.reference_token)

    @property
    def reference_token(self):
        return self.name

    def write_code(self, code_writer: CodeWriter):
        pass


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
        self._label = Label()

    def resolve_names(self, scope: Scope):
        fn_scope = Scope(scope)

        stack_slot_dispenser.reset()
        for param in self.params:
            param.resolve_names(fn_scope)
            param.stack_slot = stack_slot_dispenser.get_slot()

        self.body.resolve_names(fn_scope)

    def resolve_types(self):
        self.return_type.resolve_types()
        for param in self.params:
            param.resolve_types()
        self.body.resolve_types()

    def write_code(self, code_writer: CodeWriter):
        code_writer.place_label(self.label)
        self.body.write_code(code_writer)
        code_writer.write(InstructionType.RET)

    @property
    def reference_token(self):
        return self.name

    @property
    def label(self):
        return self._label


class DeclVar(Decl):

    def __init__(self, type_: Type, name, value=None, is_constant=False) -> None:
        super().__init__()
        self.add_children(type_, value)
        self.type = type_
        self.name = name
        self.value = value
        self.is_constant = is_constant
        self.global_slot = 0

    def resolve_names(self, scope: Scope):
        self.type.resolve_names(scope)
        if self.value:
            self.value.resolve_names(scope)

        scope.add(self.name, self)
        self.global_slot = global_slot_dispenser.get_slot()

    def resolve_types(self):
        self.type.resolve_types()
        if not self.type.is_valid_var_type():
            handle_typing_error('Cannot create a variable of the given type', self.reference_token)
            return None

        if self.value:
            return self.value.resolve_types()

    def write_code(self, code_writer: CodeWriter):
        if self.value:
            self.value.write_code(code_writer)
            if isinstance(self.type, TypeArray):
                code_writer.write(InstructionType.ARRAY_FILL_GLOBAL, self.global_slot, self.type.length)
            else:
                code_writer.write(InstructionType.SET_GLOBAL, self.global_slot)

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
        self.field_slot = 0

    def resolve_names(self, scope: Scope):
        self.type.resolve_names(scope)
        scope.add(self.name, self)

    def is_accessible(self):
        return self.type.is_accessible()

    def resolve_types(self):
        self.type.resolve_types()
        if not self.type.is_valid_var_type():
            handle_typing_error('Cannot create a field of the given type', self.reference_token)

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

        field_slot_dispenser = SlotDispenser()
        for field in self.fields:
            field.resolve_names(self._fields_scope)
            field.field_slot = field_slot_dispenser.get_slot()

    @property
    def fields_scope(self):
        return self._fields_scope

    def resolve_types(self):
        for field in self.fields:
            field.resolve_types()

    @property
    def reference_token(self):
        return self.name

    def write_code(self, code_writer: CodeWriter):
        pass


class Helper(Node, ABC):
    """
    Helpers are gone in semantic checking phase and later
    """
    def resolve_names(self, scope: Scope):
        pass

    def resolve_types(self):
        pass

    @property
    def reference_token(self):
        return None

    def write_code(self, code_writer: CodeWriter):
        pass


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

    def write_code(self, code_writer: CodeWriter):
        for element in self.root_elements:
            element.write_code(code_writer)

    @property
    def reference_token(self):
        return None
