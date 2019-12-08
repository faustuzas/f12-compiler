from models import ExtendedEnum
from utils.bytes_utils import select_from_bytes_func


class InstructionType(ExtendedEnum):
    OR = 'OR'
    AND = 'AND'

    EQ = 'EQ'
    NE = 'NE'

    GT_INT = 'GT_INT'
    GE_INT = 'GE_INT'
    LT_INT = 'LT_INT'
    LE_INT = 'LE_INT'

    GT_FLOAT = 'GT_FLOAT'
    GE_FLOAT = 'GE_FLOAT'
    LT_FLOAT = 'LT_FLOAT'
    LE_FLOAT = 'LE_FLOAT'

    ADD_INT = 'ADD_INT'
    SUB_INT = 'SUB_INT'
    MUL_INT = 'MUL_INT'
    DIV_INT = 'DIV_INT'
    MOD_INT = 'MOD_INT'
    POW_INT = 'POW_INT'

    ADD_FLOAT = 'ADD_FLOAT'
    SUB_FLOAT = 'SUB_FLOAT'
    MUL_FLOAT = 'MUL_FLOAT'
    DIV_FLOAT = 'DIV_FLOAT'
    MOD_FLOAT = 'MOD_FLOAT'
    POW_FLOAT = 'POW_FLOAT'

    UNARY_PLUS_INT = 'UNARY_PLUS_INT'
    UNARY_MINUS_INT = 'UNARY_MINUS_INT'
    UNARY_PLUS_FLOAT = 'UNARY_PLUS_FLOAT'
    UNARY_MINUS_FLOAT = 'UNARY_MINUS_FLOAT'

    RET = 'RET'

    JMP = 'JMP'
    JZ = 'JZ'

    SET_GLOBAL = 'SET_GLOBAL'
    SET_LOCAL = 'SET_LOCAL'

    PUSH_INT = 'PUSH_INT'
    PUSH_BOOL = 'PUSH_BOOL'
    PUSH_FLOAT = 'PUSH_FLOAT'
    PUSH_STRING = 'PUSH_STRING'

    ARRAY_INIT = 'ARRAY_INIT'


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

add_instruction(0x40, InstructionType.ADD_INT, [])
add_instruction(0x41, InstructionType.ADD_FLOAT, [])

add_instruction(0x50, InstructionType.OR, [])
add_instruction(0x51, InstructionType.AND, [])
add_instruction(0x52, InstructionType.EQ, [])
add_instruction(0x53, InstructionType.NE, [])
add_instruction(0x54, InstructionType.GT_INT, [])
add_instruction(0x55, InstructionType.GE_INT, [])
add_instruction(0x56, InstructionType.LT_INT, [])
add_instruction(0x57, InstructionType.LE_INT, [])
add_instruction(0x58, InstructionType.GT_FLOAT, [])
add_instruction(0x59, InstructionType.GE_FLOAT, [])
add_instruction(0x5A, InstructionType.LT_FLOAT, [])
add_instruction(0x5B, InstructionType.LE_FLOAT, [])

add_instruction(0x60, InstructionType.ARRAY_INIT, [int])
