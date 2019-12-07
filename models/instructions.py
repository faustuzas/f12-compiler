from models import ExtendedEnum
from utils.bytes_utils import select_from_bytes_func


class InstructionType(ExtendedEnum):
    OR = 'OR'
    AND = 'AND'

    EQ = 'EQ'
    NE = 'NE'

    INT_GT = 'INT_GT'
    INT_GE = 'INT_GE'
    INT_LT = 'INT_LT'
    INT_LE = 'INT_LE'

    FLOAT_GT = 'FLOAT_GT'
    FLOAT_GE = 'FLOAT_GE'
    FLOAT_LT = 'FLOAT_LT'
    FLOAT_LE = 'FLOAT_LE'

    INT_ADD = 'INT_ADD'
    INT_SUB = 'INT_SUB'
    INT_MUL = 'INT_MUL'
    INT_DIV = 'INT_DIV'
    INT_MOD = 'INT_MOD'
    INT_POW = 'INT_POW'

    FLOAT_ADD = 'FLOAT_ADD'
    FLOAT_SUB = 'FLOAT_SUB'
    FLOAT_MUL = 'FLOAT_MUL'
    FLOAT_DIV = 'FLOAT_DIV'
    FLOAT_MOD = 'FLOAT_MOD'
    FLOAT_POW = 'FLOAT_POW'

    INT_UNARY_PLUS = 'INT_UNARY_PLUS'
    INT_UNARY_MINUS = 'INT_UNARY_MINUS'
    FLOAT_UNARY_PLUS = 'FLOAT_UNARY_PLUS'
    FLOAT_UNARY_MINUS = 'FLOAT_UNARY_MINUS'

    RET = 'RET'

    JMP = 'JMP'
    JZ = 'JZ'

    SET_GLOBAL = 'SET_GLOBAL'
    SET_LOCAL = 'SET_LOCAL'

    PUSH_INT = 'PUSH_INT'
    PUSH_BOOL = 'PUSH_BOOL'
    PUSH_FLOAT = 'PUSH_FLOAT'
    PUSH_STRING = 'PUSH_STRING'


class Instruction:

    def __init__(self, op_code, type_: InstructionType, ops_types) -> None:
        self.op_code = op_code
        self.type = type_
        self.ops_types = ops_types

    def fetch_ops(self, code, offset):
        ops = []
        for op_type in self.ops_types:
            value, offset = select_from_bytes_func(op_type)(code, offset)
            ops.append(value)

        return ops, offset


instructions_by_type = {}
instructions_by_op_code = {}


def add_instruction(op_code, type_, ops_types):
    inst = Instruction(op_code, type_, ops_types)
    instructions_by_type[type_] = inst
    instructions_by_op_code[op_code] = inst


add_instruction(0x10, InstructionType.PUSH_INT, [int])
add_instruction(0x11, InstructionType.PUSH_BOOL, [bool])
add_instruction(0x12, InstructionType.PUSH_FLOAT, [float])
add_instruction(0x13, InstructionType.PUSH_STRING, [str])

add_instruction(0x20, InstructionType.SET_GLOBAL, [int])
add_instruction(0x21, InstructionType.SET_LOCAL, [int])

add_instruction(0x30, InstructionType.RET, [])
add_instruction(0x31, InstructionType.JZ, [int])
add_instruction(0x32, InstructionType.JMP, [int])
