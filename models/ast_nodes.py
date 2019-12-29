from abc import ABC
from typing import List, Union, Type

from codegen.code_writer import CodeWriter, Label
from models.instructions import InstructionType
from models.scope import Scope
from models.slot_dispenser import SlotDispenser
from codegen.string_storage import string_storage
from models.token import TokenType
from utils.error_printer import print_error_from_token as print_error, print_error_simple
from utils.list_utils import find_in_list
from utils.type_checking_helpers import unify_types, prepare_for_printing
import utils.sizes as sizes
import models.types as types

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

    @property
    def is_accessible(self):
        return False

    @property
    def size_in_stack(self):
        raise NotImplementedError(f'Size in stack not implemented for "{self.__class__}"')

    @property
    def size_in_heap(self):
        raise Exception('Unreachable code')

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

    def to_stdout_instr(self):
        raise Exception('Unreachable code')

    def resolve_includes(self):
        return None

    def resolve_names(self, scope: Scope):
        raise NotImplementedError(f'Resolve names not implemented for {self.__class__}')

    def resolve_types(self):
        raise NotImplementedError(f'Resolve types not implemented for {self.__class__}')

    def write_code(self, code_writer: CodeWriter):
        raise NotImplementedError(f'Write code not implemented for {self.__class__}')


class AstType(Node, ABC):

    def resolve_types(self):
        return self

    @property
    def is_arithmetic(self):
        return False

    @property
    def is_comparable(self):
        return False

    @property
    def has_value(self):
        return False

    @property
    def is_valid_var_type(self):
        return True

    @property
    def reference_token(self):
        return None

    @property
    def is_iterable(self):
        return False

    @property
    def kind(self):  # -> Union[Type[types.Type], AstType]
        raise NotImplementedError(f'Kind not implemented for "{self.__class__}"')

    @property
    def iterable_element_type(self):
        raise TypeError(f'You cannot iterate through {prepare_for_printing(self)}')

    def write_code(self, code_writer: CodeWriter):
        pass


class AstTypePointer(AstType):

    def __init__(self, of_type: Union[AstType, None]) -> None:
        super().__init__()
        self.of_type = of_type

    @property
    def size_in_stack(self) -> int:
        return sizes.address

    @property
    def size_in_heap(self):
        return self.of_type.size_in_heap

    @property
    def kind(self):
        return self.of_type.kind if self.of_type else None

    @property
    def is_iterable(self):
        return self.of_type.is_iterable if self.of_type else False

    @property
    def iterable_element_type(self):
        return self.of_type

    def resolve_names(self, scope: Scope):
        return self.of_type.resolve_names(scope)

    def to_stdout_instr(self):
        return self.of_type.to_stdout_instr()


class AstTypeArray(AstType):

    def __init__(self, inner_type) -> None:
        super().__init__()
        self.inner_type = inner_type

    @property
    def access_type(self):
        return self.inner_type

    @property
    def size_in_stack(self):
        return sizes.address

    @property
    def size_in_heap(self):
        return self.inner_type.size_in_heap

    @property
    def kind(self):
        return self.inner_type.kind

    @property
    def is_iterable(self):
        return True

    @property
    def iterable_element_type(self):
        return self.inner_type

    def resolve_names(self, scope: Scope):
        return self.inner_type.resolve_names(scope)


class AstTypePrimitive(AstType):

    def __init__(self, type_: Type[types.Type]):
        super().__init__()
        self.type = type_

    @property
    def kind(self):
        return self.type

    @property
    def is_arithmetic(self):
        return self.type == types.Int or \
            self.type == types.Float

    @property
    def is_comparable(self):
        return self.type == types.Int or \
            self.type == types.Float

    @property
    def has_value(self):
        return self.type != types.Void

    @property
    def is_valid_var_type(self):
        return self.type != types.Void

    @property
    def size_in_stack(self) -> int:
        return self.type.size_in_bytes()

    @property
    def size_in_heap(self):
        if self.type == types.String:
            return types.Char.size_in_bytes()
        return self.type.size_in_bytes()

    @property
    def is_iterable(self):
        return self.type == types.String

    @property
    def reference_token(self):
        return None

    @property
    def iterable_element_type(self):
        if self.type == types.String:
            return AstTypePrimitive(types.Char)
        return super().iterable_element_type()

    def to_stdout_instr(self):
        return self.type.to_stdout_instr()

    def resolve_names(self, scope: Scope):
        pass


class AstTypeUnit(AstType):

    def __init__(self, name, decl_node=None):
        super().__init__()
        self.name = name
        self.decl_node = decl_node

    @property
    def kind(self):
        return self

    @property
    def size_in_stack(self):
        return sizes.address

    @property
    def is_accessible(self):
        return True

    def resolve_names(self, scope: Scope):
        self.decl_node = scope.resolve_name(self.name)

    def resolve_types(self):
        return self


class Expr(Node, ABC):
    pass


class ExprLit(Expr, ABC):

    def __init__(self, value):
        super().__init__()
        self.value = value

    @property
    def reference_token(self):
        return self.value

    @property
    def kind(self):  # -> Union[Type[types.Type], AstType]
        raise NotImplementedError(f'Kind not implemented for "{self.__class__}"')

    @property
    def size_in_heap(self):
        return self.size_in_stack

    def resolve_names(self, scope: Scope):
        pass

    def resolve_types(self):
        return AstTypePrimitive(self.kind)


class ExprLitChar(ExprLit):

    @property
    def size_in_stack(self):
        return types.Char.size_in_bytes()

    @property
    def kind(self):
        return types.Char

    def write_code(self, code_writer: CodeWriter):
        code_writer.write(InstructionType.PUSH_CHAR, self.value.value)


class ExprLitStr(ExprLit):

    def __init__(self, value):
        super().__init__(value)
        self._label = string_storage.add_string(value.value)

    @property
    def size_in_stack(self):
        return types.String.size_in_bytes()

    @property
    def kind(self):
        return types.String

    @property
    def label(self):
        return self._label

    def write_code(self, code_writer: CodeWriter):
        code_writer.write(InstructionType.PUSH_INT, self.label)


class ExprLitFloat(ExprLit):

    @property
    def size_in_stack(self):
        return types.Float.size_in_bytes()

    @property
    def kind(self):
        return types.Float

    def write_code(self, code_writer: CodeWriter):
        code_writer.write(InstructionType.PUSH_FLOAT, float(self.value.value))


class ExprLitInt(ExprLit):

    @property
    def size_in_stack(self):
        return types.Int.size_in_bytes()

    @property
    def kind(self):
        return types.Int

    def write_code(self, code_writer: CodeWriter):
        code_writer.write(InstructionType.PUSH_INT, int(self.value.value))


class ExprLitBool(ExprLit):

    @property
    def size_in_stack(self):
        return types.Bool.size_in_bytes()

    @property
    def kind(self):
        return types.Bool

    def write_code(self, code_writer: CodeWriter):
        value = self.value.type == TokenType.CONSTANT_TRUE
        code_writer.write(InstructionType.PUSH_BOOL, value)


class ExprLitArray(ExprLit):

    def __init__(self, value, start_token):
        super().__init__(value)
        self._start_token = start_token

    @property
    def kind(self):
        if self.length > 0:
            return self.value[0].resolve_types()
        return None

    @property
    def reference_token(self):
        if self.length > 0:
            return self.value[0].reference_token
        return self._start_token

    @property
    def length(self):
        return len(self.value)

    @property
    def single_el_size(self):
        return self.value[0].resolve_types().size_in_stack

    @property
    def size_in_stack(self):
        return sizes.address

    @property
    def size_in_heap(self):
        return self.length * self.single_el_size

    def resolve_names(self, scope: Scope):
        for el in self.value:
            el.resolve_names(scope)

    def resolve_types(self):
        if self.length > 0:
            first_val_type = self.value[0].resolve_types()
            for i in range(1, len(self.value)):
                unify_types(self.value[i].reference_token, first_val_type, self.value[i].resolve_types())
            return AstTypeArray(first_val_type) if first_val_type else None
        else:
            handle_typing_error('Array cannot be empty', self.reference_token)

    def write_code(self, code_writer: CodeWriter):
        for el in reversed(self.value):
            el.write_code(code_writer)


class ExprNew(Node, ABC):

    @property
    def size_in_stack(self):
        return sizes.address


class ExprNewFromSizedType(ExprNew):

    def __init__(self, token, type_, size_expr) -> None:
        super().__init__()
        self.add_children(type_, size_expr)
        self.token = token
        self.type = type_
        self.size_expr = size_expr

    @property
    def reference_token(self):
        return self.token

    def resolve_names(self, scope: Scope):
        self.type.resolve_names(scope)
        self.size_expr.resolve_names(scope)

    def resolve_types(self):
        expr_type = self.size_expr.resolve_types()
        unify_types(self.size_expr.reference_token, AstTypePrimitive(types.Int), expr_type)
        return AstTypePointer(AstTypeArray(self.type))

    def write_code(self, code_writer: CodeWriter):
        self.size_expr.write_code(code_writer)
        code_writer.write(InstructionType.PUSH_INT, self.type.size_in_heap)
        code_writer.write(InstructionType.MUL_INT)
        code_writer.write(InstructionType.MEMORY_ALLOCATE)


class ExprNewFromArrayLit(ExprNew):

    def __init__(self, array: ExprLitArray) -> None:
        super().__init__()
        self.add_children(array)
        self.array = array

    @property
    def reference_token(self):
        return self.array.reference_token

    @property
    def size_in_stack(self):
        return sizes.address

    def resolve_names(self, scope: Scope):
        self.array.resolve_names(scope)

    def resolve_types(self):
        type_ = self.array.resolve_types()
        if type_:
            return AstTypePointer(type_)

    def write_code(self, code_writer: CodeWriter):
        for el in reversed(self.array.value):
            el.write_code(code_writer)

        # allocate memory for an array
        code_writer.write(InstructionType.PUSH_INT, self.array.size_in_heap)
        code_writer.write(InstructionType.MEMORY_ALLOCATE)

        el_size = self.array.single_el_size
        for i in range(self.array.length):
            code_writer.write(InstructionType.MEMORY_SET_PUSH, el_size)
            if i + 1 != self.array.length:
                code_writer.write(InstructionType.PUSH_INT, el_size)
                code_writer.write(InstructionType.ADD_INT)
        # calculate the original address and leave it in the stack
        code_writer.write(InstructionType.PUSH_INT, self.array.length * (el_size - 1) - 1)
        code_writer.write(InstructionType.SUB_INT)


class ExprBinary(Expr, ABC):

    def __init__(self, left, right) -> None:
        super().__init__()
        self.add_children(left, right)
        self.left = left
        self.right = right

    @property
    def reference_token(self):
        return self.left.reference_token

    @property
    def size_in_stack(self):
        type_ = self.left.resolve_types()
        return type_.size_in_stack

    def resolve_names(self, scope: Scope):
        self.left.resolve_names(scope)
        self.right.resolve_names(scope)


class ExprNumeric(Expr, ABC):

    @property
    def instruction_type_for_int(self):
        raise NotImplementedError(f'Expr binary instruction type for int not implemented for {self.__class__}')

    @property
    def instruction_type_for_float(self):
        raise NotImplementedError(f'Expr binary instruction type for float not implemented for {self.__class__}')

    def ensure_valid_type(self, type_: AstTypePrimitive):
        if not isinstance(type_, AstTypePrimitive):
            raise NotImplementedError(f'There are no numeric expr for: {type_.__class__}')

        if type_.kind in (types.Int, types.Float):
            return type_.kind
        raise NotImplementedError(f'There are no binary operators for: {type_.kind}')

    def write_code_for_type(self, type_, code_writer):
        kind = self.ensure_valid_type(type_)
        if kind == types.Int:
            instruction_type = self.instruction_type_for_int
        else:
            instruction_type = self.instruction_type_for_float
        code_writer.write(instruction_type)


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
        if left_type.is_arithmetic:
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
        if left_type.is_comparable:
            unify_types(reference_token, left_type, right_type, 'Right operand type does not match left\'s one')
        else:
            handle_typing_error(
                f'Cannot perform compare operations with {prepare_for_printing(left_type)}',
                reference_token
            )
        return AstTypePrimitive(types.Bool)


class ExprBinaryEquality(ExprBinary, ABC):

    @property
    def instruction_type(self):
        raise NotImplementedError(f'Instruction type is not implemented for: {self.__class__} ')

    def resolve_types(self):
        left_type = self.left.resolve_types()
        right_type = self.right.resolve_types()

        if not left_type:
            return None

        reference_token = self.left.reference_token
        if left_type.has_value:
            unify_types(reference_token, left_type, right_type, 'Valueless expressions cannot be comparable')
        else:
            handle_typing_error(
                f'Cannot perform equality operations with {prepare_for_printing(left_type)}',
                reference_token
            )
        return AstTypePrimitive(types.Bool)

    def write_code(self, code_writer: CodeWriter):
        self.left.write_code(code_writer)
        self.right.write_code(code_writer)
        code_writer.write(self.instruction_type, self.left.resolve_types().size_in_stack)


class ExprBinaryLogic(ExprBinary, ABC):

    @property
    def instruction_type(self):
        raise NotImplementedError(f'Instruction type is not implemented for: {self.__class__} ')

    def resolve_types(self):
        left_type = self.left.resolve_types()
        right_type = self.right.resolve_types()

        if not left_type:
            return None

        unify_types(self.left.reference_token, left_type, AstTypePrimitive(types.Bool))
        unify_types(self.right.reference_token, right_type, AstTypePrimitive(types.Bool))

        return AstTypePrimitive(types.Bool)

    def write_code(self, code_writer: CodeWriter):
        self.left.write_code(code_writer)
        self.right.write_code(code_writer)
        code_writer.write(self.instruction_type)


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

    @property
    def reference_token(self):
        return self.expr.reference_token

    @property
    def size_in_stack(self):
        return self.expr.size_in_stack

    def resolve_names(self, scope: Scope):
        self.expr.resolve_names(scope)

    def resolve_types(self):
        type_ = self.expr.resolve_types()
        if type_.is_arithmetic:
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


class ExprFromStdin(Expr):

    @property
    def size_in_stack(self):
        return types.Char.size_in_bytes()

    @property
    def reference_token(self):
        return None

    def resolve_types(self):
        return AstTypePrimitive(types.Char)

    def resolve_names(self, scope: Scope):
        pass

    def write_code(self, code_writer: CodeWriter):
        code_writer.write(InstructionType.FROM_STDIN)


class Assignable(ABC):

    def resolve_identifier(self):
        raise NotImplementedError(f'Resolve identifier is not implemented for {self.__class__}')


class ExprAssign(Expr):

    @property
    def size_in_stack(self):
        return self.value.size_in_stack

    @property
    def reference_token(self):
        return self.object.reference_token

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

    def write_code(self, code_writer: CodeWriter):
        if self.is_local:
            code_writer.write(InstructionType.GET_LOCAL, self.slot, self.type.size_in_stack)
        else:
            code_writer.write(InstructionType.GET_GLOBAL, self.slot, self.type.size_in_stack)

    def resolve_identifier(self):
        return self.identifier

    @property
    def reference_token(self):
        return self.identifier

    @property
    def is_local(self):
        return isinstance(self.decl_node, (StmntDeclVar, FunParam))

    @property
    def type(self):
        return self.decl_node.type

    @property
    def slot(self):
        if self.is_local:
            return self.decl_node.stack_slot
        return self.decl_node.global_slot

    @property
    def size_in_stack(self):
        return self.type.size_in_stack

    @property
    def size_in_heap(self):
        return self.type.size_in_heap

    @property
    def is_accessible(self):
        return isinstance(self.decl_node.type, AstTypeUnit)

    def write_assigment_code(self, code_writer, value):
        value.write_code(code_writer)
        code_writer.write(InstructionType.POP_PUSH_N, self.size_in_stack, 2)
        if self.is_local:
            code_writer.write(InstructionType.SET_LOCAL, self.slot, self.size_in_stack)
        else:
            code_writer.write(InstructionType.SET_GLOBAL, self.slot, self.size_in_stack)


class ExprAccess(Expr, Assignable):

    def __init__(self, obj, field) -> None:
        super().__init__()
        self.add_children(obj, field)
        self.object = obj
        self.field = field
        self.field_decl_node = None

    @property
    def reference_token(self):
        return self.field

    @property
    def size_in_stack(self):
        raise Exception('Unreachable code')

    @property
    def is_accessible(self):
        return self.field_decl_node and self.field_decl_node.is_accessible()

    def resolve_names(self, scope: Scope):
        object_decl_node = self.object.resolve_names(scope)

        if not object_decl_node or not isinstance(object_decl_node.type, (AstTypeUnit, AstTypeArray)):
            # print error maybe
            return None

        if isinstance(object_decl_node.type, AstTypeArray):
            unit_decl_node = object_decl_node.type.inner_type.decl_node
        else:
            unit_decl_node = object_decl_node.type.decl_node
        self.field_decl_node = unit_decl_node.fields_scope.resolve_name(self.field)
        return self.field_decl_node

    def resolve_identifier(self):
        return self.object.resolve_identifier()

    def resolve_types(self):
        type_ = self.object.resolve_types()
        if not type_ or not type_.is_accessible():
            handle_typing_error('You cannot access this type', self.object.reference_token)
        return self.field_decl_node.type if self.field_decl_node else None

    def write_code(self, code_writer: CodeWriter):
        raise Exception('Unreachable code')


class ExprArrayAccess(Expr, Assignable):

    def __init__(self, array, index_expr) -> None:
        super().__init__()
        self.add_children(array, index_expr)
        self.array = array
        self.index_expr = index_expr

    @property
    def size_in_stack(self):
        return self.array.resolve_types().size_in_stack

    @property
    def is_accessible(self):
        return self.array.is_accessible()

    @property
    def reference_token(self):
        return self.array.reference_token

    def resolve_names(self, scope: Scope):
        self.index_expr.resolve_names(scope)
        return self.array.resolve_names(scope)

    def resolve_identifier(self):
        return self.array.resolve_identifier()

    def resolve_types(self):
        # check if array variable is Iterable
        array_type = self.array.resolve_types()
        if isinstance(array_type, AstTypePointer):
            array_type = array_type.of_type

        if not array_type.is_iterable:
            handle_typing_error(
                f'You cannot access variable of {prepare_for_printing(array_type)}',
                self.reference_token
            )
            return None

        # check if index expr evaluates to int
        unify_types(self.index_expr.reference_token,
                    AstTypePrimitive(types.Int),
                    self.index_expr.resolve_types())

        return array_type.iterable_element_type.resolve_types()

    def write_code(self, code_writer: CodeWriter):
        self.array.write_code(code_writer)
        self.index_expr.write_code(code_writer)
        code_writer.write(InstructionType.PUSH_INT, self.array.size_in_heap)
        code_writer.write(InstructionType.MUL_INT)
        code_writer.write(InstructionType.ADD_INT)

        type_ = self.array.resolve_types()
        # if isinstance(type_, AstTypePointer):
        #     bytes_to_get = type_.size_in_heap
        # else:
        #     bytes_to_get = type_.size_in_stack
        bytes_to_get = type_.size_in_heap
        code_writer.write(InstructionType.MEMORY_GET, bytes_to_get)

    def write_assigment_code(self, code_writer, value):
        value.write_code(code_writer)
        # pop the value and push it two times into the stack because assignment has to have value
        code_writer.write(InstructionType.POP_PUSH_N, value.size_in_heap, 2)

        # offset bytes depending on the type
        self.index_expr.write_code(code_writer)
        code_writer.write(InstructionType.PUSH_INT, self.array.size_in_heap)
        code_writer.write(InstructionType.MUL_INT)

        if self.array.is_local:
            code_writer.write(InstructionType.GET_LOCAL, self.array.slot, self.array.size_in_stack)
        else:
            code_writer.write(InstructionType.GET_GLOBAL, self.array.slot, self.array.size_in_stack)
        # add offset to address stored in variable
        code_writer.write(InstructionType.ADD_INT)

        code_writer.write(InstructionType.MEMORY_SET, self.array.size_in_heap)


class ExprFnCall(Expr):

    def __init__(self, function_name, args) -> None:
        super().__init__()
        self.add_children(*args)
        self.function_name = function_name
        self.args = args
        self.function_decl_node = None

    @property
    def reference_token(self):
        return self.function_name

    @property
    def return_type(self):
        return self.function_decl_node.return_type

    @property
    def size_in_stack(self):
        return self.function_decl_node.return_type.size_in_stack

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
        code_writer.write(InstructionType.FN_CALL, self.function_decl_node.label, self.function_decl_node.params_offset)


class ExprCreateUnit(Expr):

    def __init__(self, unit_name, args) -> None:
        super().__init__()
        self.add_children(*args)
        self.unit_name = unit_name
        self.args = args
        self.unit_decl_node = None

    @property
    def reference_token(self):
        return self.unit_name

    @property
    def size_in_stack(self):
        raise NotImplementedError()

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
            if not field.type.is_valid_var_type:
                continue

            arg_for_field = find_in_list(self.args, lambda a: field.name.value == a.field.value)
            if not arg_for_field:
                handle_typing_error(f'There is no argument for \'{field.name.value}\'', self.reference_token)
                continue

            value_type = arg_for_field.value.resolve_types()
            unify_types(arg_for_field.reference_token, field.type, value_type)

        return AstTypeUnit(self.unit_decl_node.name, self.unit_decl_node)

    def write_code(self, code_writer: CodeWriter):
        raise NotImplementedError('This feature is not implemented yet')


class CreateUnitArg(Node):

    def __init__(self, unit_name, field, value) -> None:
        super().__init__()
        self.add_children(field, value)
        self.unit_name = unit_name
        self.field = field
        self.value = value
        self.field_decl_node = None

    @property
    def reference_token(self):
        return self.value.reference_token

    @property
    def size_in_stack(self):
        return self.field_decl_node.size_in_stack

    def resolve_names(self, scope: Scope):
        unit_decl_node = scope.resolve_name(self.unit_name)
        if unit_decl_node:
            self.field_decl_node = unit_decl_node.fields_scope.resolve_name(self.field)

        self.value.resolve_names(scope)

    def resolve_types(self):
        return self.value.resolve_types()

    def write_code(self, code_writer: CodeWriter):
        raise NotImplementedError('This feature is not implemented yet')


class Stmnt(Node, ABC):

    @property
    def size_in_stack(self):
        raise Exception('Unreachable code')


class StmntEmpty(Stmnt):

    @property
    def reference_token(self):
        return None

    def resolve_names(self, scope: Scope):
        pass

    def resolve_types(self):
        pass

    def write_code(self, code_writer: CodeWriter):
        pass


class StmntFree(Stmnt):

    def __init__(self, address) -> None:
        super().__init__()
        self.add_children(address)
        self.address = address

    @property
    def reference_token(self):
        return self.address.reference_token

    def resolve_names(self, scope: Scope):
        self.address.resolve_names(scope)

    def resolve_types(self):
        type_ = self.address.resolve_types()
        unify_types(self.reference_token, AstTypePointer(None), type_)

    def write_code(self, code_writer: CodeWriter):
        self.address.write_code(code_writer)
        code_writer.write(InstructionType.MEMORY_FREE)


class StmntDeclVar(Stmnt):

    def __init__(self, type_: AstType, name, value=None, is_constant=False) -> None:
        super().__init__()
        self.add_children(type_)
        self.type = type_
        self.name = name
        self.value = value
        self.is_constant = is_constant
        self.stack_slot = 0

    @property
    def reference_token(self):
        return self.name

    def resolve_names(self, scope: Scope):
        self.type.resolve_names(scope)
        if self.value:
            self.value.resolve_names(scope)

        scope.add(self.name, self)
        self.stack_slot = stack_slot_dispenser.get_slot(self.type.size_in_stack)

    def resolve_types(self):
        self.type.resolve_types()
        if not self.type.is_valid_var_type:
            handle_typing_error('Cannot create a variable of the given type', self.reference_token)
            return None

        if self.value:
            value_type = self.value.resolve_types()
            unify_types(self.reference_token, self.type, value_type)

    def write_code(self, code_writer: CodeWriter):
        if self.value:
            self.value.write_code(code_writer)
            code_writer.write(InstructionType.SET_LOCAL, self.stack_slot, self.value.size_in_stack)


class StmntIf(Stmnt):

    def __init__(self, condition: Expr, stmnt_block, else_clause=None) -> None:
        super().__init__()
        self.add_children(condition, stmnt_block, else_clause)
        self.condition = condition
        self.stmnt_block = stmnt_block
        self.else_clause = else_clause

    @property
    def reference_token(self):
        return self.condition.reference_token

    def resolve_names(self, scope: Scope):
        self.condition.resolve_names(scope)
        self.stmnt_block.resolve_names(scope)
        if self.else_clause:
            self.else_clause.resolve_names(scope)

    def resolve_types(self):
        condition_type = self.condition.resolve_types()
        unify_types(self.condition.reference_token, AstTypePrimitive(types.Bool), condition_type)
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


class StmntControl(Stmnt, ABC):

    def __init__(self, token) -> None:
        super().__init__()
        self.token = token

    @property
    def reference_token(self):
        return self.token

    def resolve_types(self):
        pass

    def _outer_loop(self):
        outer_while = self.find_parent(StmntWhile)
        if outer_while:
            return outer_while
        return None


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
            val_type = AstTypePrimitive(types.Void)
        unify_types(self.token, ret_type, val_type)

    def write_code(self, code_writer: CodeWriter):
        if self.value:
            self.value.write_code(code_writer)
            code_writer.write(InstructionType.RET_VALUE, self.value.size_in_stack)
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
        self.expr.write_code(code_writer)
        code_writer.write(InstructionType.POP, self.expr.size_in_stack)


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
        for value in self.values:
            type_ = value.resolve_types()
            if type_ is None:
                continue

            if not isinstance(type_, AstTypePrimitive):
                handle_typing_error(f'You cannot print {prepare_for_printing(type_)}', value.reference_token)

    @property
    def reference_token(self):
        return self.token

    def write_code(self, code_writer: CodeWriter):
        for value in self.values:
            value.write_code(code_writer)
            instr = value.resolve_types().to_stdout_instr()
            code_writer.write(instr)


class StmntWhile(Stmnt):

    def __init__(self, condition, stmnt_block) -> None:
        super().__init__()
        self.add_children(condition, stmnt_block)
        self.condition = condition
        self.stmnt_block = stmnt_block

    @property
    def reference_token(self):
        return self.condition.reference_token

    def resolve_names(self, scope: Scope):
        self.condition.resolve_names(scope)
        self.stmnt_block.resolve_names(scope)

    def resolve_types(self):
        condition_type = self.condition.resolve_types()
        unify_types(self.condition.reference_token, AstTypePrimitive(types.Bool), condition_type)

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


class StmntBlock(Node):

    def __init__(self, statements: List[Stmnt]) -> None:
        super().__init__()
        self.add_children(*statements)
        self.statements = statements

    @property
    def reference_token(self):
        return self.statements[0].reference_token if len(self.statements) else None

    @property
    def size_in_stack(self):
        raise Exception('Unreachable code')

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


class FunParam(Node):

    def __init__(self, type_: AstType, name):
        super().__init__()
        self.add_children(type_)
        self.type = type_
        self.name = name
        self.stack_slot = 0

    @property
    def size_in_stack(self):
        return self.type.size_in_stack

    @property
    def reference_token(self):
        return self.name

    @property
    def is_local(self):
        return True

    def resolve_names(self, scope: Scope):
        scope.add(self.name, self)

    def resolve_types(self):
        if not self.type.is_valid_var_type:
            handle_typing_error('Cannot create a parameter of the given type', self.reference_token)

    def write_code(self, code_writer: CodeWriter):
        pass


class Decl(Node, ABC):
    pass


class DeclFun(Decl):

    def __init__(self, name, params: List[FunParam], return_type: AstType, body: StmntBlock) -> None:
        super().__init__()
        self.add_children(*params, return_type, body)
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body
        self._label = Label()
        self._locals_offset = 0

    @property
    def reference_token(self):
        return self.name

    @property
    def label(self):
        return self._label

    @property
    def size_in_stack(self):
        raise Exception('Unreachable code')

    @property
    def params_offset(self):
        sum_ = 0
        for param in self.params:
            sum_ += param.size_in_stack
        return sum_

    def resolve_names(self, scope: Scope):
        fn_scope = Scope(scope)

        stack_slot_dispenser.reset()
        for param in self.params:
            param.resolve_names(fn_scope)
            param.stack_slot = stack_slot_dispenser.get_slot(param.type.size_in_stack)

        self.body.resolve_names(fn_scope)
        self._locals_offset = stack_slot_dispenser.current_slot

    def resolve_types(self):
        self.return_type.resolve_types()
        for param in self.params:
            param.resolve_types()
        self.body.resolve_types()

    def write_code(self, code_writer: CodeWriter):
        code_writer.place_label(self.label)
        if self._locals_offset > 0:
            code_writer.write(InstructionType.ALLOCATE_IN_STACK, self._locals_offset)
        self.body.write_code(code_writer)
        code_writer.write(InstructionType.RET)


class DeclVar(Decl):

    def __init__(self, type_: AstType, name, value=None, is_constant=False) -> None:
        super().__init__()
        self.add_children(type_, value)
        self.type = type_
        self.name = name
        self.value = value
        self.is_constant = is_constant
        self.global_slot = 0

    @property
    def reference_token(self):
        return self.name

    @property
    def size_in_stack(self):
        return self.type.size_in_stack

    def resolve_names(self, scope: Scope):
        self.type.resolve_names(scope)
        if self.value:
            self.value.resolve_names(scope)

        scope.add(self.name, self)
        self.global_slot = global_slot_dispenser.get_slot(self.type.size_in_stack)

    def resolve_types(self):
        self.type.resolve_types()
        if not self.type.is_valid_var_type:
            handle_typing_error('Cannot create a variable of the given type', self.reference_token)
            return None

        if self.value:
            return self.value.resolve_types()

    def write_code(self, code_writer: CodeWriter):
        if self.value:
            self.value.write_code(code_writer)
            code_writer.write(InstructionType.SET_GLOBAL, self.global_slot, self.value.size_in_stack)


class DeclUnitField(Node):

    def __init__(self, type_: AstType, name) -> None:
        super().__init__()
        self.add_children(type_)
        self.type = type_
        self.name = name
        self.field_slot = 0

    @property
    def reference_token(self):
        return self.name

    @property
    def size_in_stack(self):
        return self.type.size_in_stack

    def resolve_names(self, scope: Scope):
        self.type.resolve_names(scope)
        scope.add(self.name, self)

    def is_accessible(self):
        return self.type.is_accessible

    def resolve_types(self):
        self.type.resolve_types()
        if not self.type.is_valid_var_type:
            handle_typing_error('Cannot create a field of the given type', self.reference_token)

    def write_code(self, code_writer: CodeWriter):
        pass


class DeclUnit(Decl):

    def __init__(self, name, fields: List[DeclUnitField]) -> None:
        super().__init__()
        self.add_children(*fields)
        self.name = name
        self.fields = fields
        self._fields_scope = None

    @property
    def fields_scope(self):
        return self._fields_scope

    @property
    def reference_token(self):
        return self.name

    @property
    def size_in_stack(self):
        return sizes.address

    def resolve_names(self, scope: Scope):
        self._fields_scope = Scope(scope)
        scope.add(self.name, self)

        field_slot_dispenser = SlotDispenser()
        for field in self.fields:
            field.resolve_names(self._fields_scope)
            field.field_slot = field_slot_dispenser.get_slot(field.type.size_in_stack)

    def resolve_types(self):
        for field in self.fields:
            field.resolve_types()

    def write_code(self, code_writer: CodeWriter):
        pass


class Helper(Node, ABC):
    """
    Helpers are gone in semantic checking phase and later
    """
    @property
    def reference_token(self):
        return None

    @property
    def size_in_stack(self):
        raise Exception('Unreachable code')

    def resolve_names(self, scope: Scope):
        pass

    def resolve_types(self):
        pass

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
        self._main_fn = None

    @property
    def size_in_stack(self):
        raise Exception('Unreachable code')

    @property
    def reference_token(self):
        return None

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
        returns_int = isinstance(ret_type, AstTypePrimitive) and ret_type.type == types.Void
        if not returns_int:
            print_error(
                'Entry point',
                '\'main\' does not return anything',
                main_fn.reference_token
            )

        if len(main_fn.params) != 0:
            print_error(
                'Entry point',
                '\'main\' function must not take any params',
                main_fn.reference_token
            )

        self._main_fn = main_fn

    def write_code(self, code_writer: CodeWriter):
        global_vars = []
        others = []

        global_vars_size = 0
        for element in self.root_elements:
            if isinstance(element, DeclVar):
                global_vars_size += element.size_in_stack
                global_vars.append(element)
            else:
                others.append(element)

        code_writer.write(InstructionType.ALLOCATE_IN_STACK, global_vars_size)
        for global_var in global_vars:
            global_var.write_code(code_writer)

        code_writer.write(InstructionType.FN_CALL_BEGIN)
        code_writer.write(InstructionType.FN_CALL, self._main_fn.label, self._main_fn.params_offset)
        code_writer.write(InstructionType.EXIT)

        for element in others:
            element.write_code(code_writer)

        string_storage.place_labels(code_writer)
