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

    FN_CALL_BEGIN = 'FN_CALL_BEGIN'
    FN_CALL = 'FN_CALL'
    RET = 'RET'
    RET_VALUE = 'RET_VALUE'

    JMP = 'JMP'
    JZ = 'JZ'

    SET_GLOBAL = 'SET_GLOBAL'
    SET_LOCAL = 'SET_LOCAL'

    POP = 'POP'
    PUSH_INT = 'PUSH_INT'
    PUSH_BOOL = 'PUSH_BOOL'
    PUSH_FLOAT = 'PUSH_FLOAT'
    PUSH_STRING = 'PUSH_STRING'

    ARRAY_FILL_GLOBAL = 'ARRAY_FILL_GLOBAL'
    ARRAY_FILL_LOCAL = 'ARRAY_FILL_LOCAL'
    ARRAY_SET_VALUE_LOCAL = 'ARRAY_SET_VALUE_LOCAL'
    ARRAY_SET_VALUE_GLOBAL = 'ARRAY_SET_VALUE_GLOBAL'

    TO_STDOUT = 'TO_STDOUT'


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


add_instruction(0x10, InstructionType.POP, [])
add_instruction(0x11, InstructionType.PUSH_INT, [int])
add_instruction(0x12, InstructionType.PUSH_BOOL, [bool])
add_instruction(0x13, InstructionType.PUSH_FLOAT, [float])
add_instruction(0x14, InstructionType.PUSH_STRING, [str])

add_instruction(0x20, InstructionType.SET_GLOBAL, [int])
add_instruction(0x21, InstructionType.SET_LOCAL, [int])

add_instruction(0x30, InstructionType.FN_CALL_BEGIN, [])
add_instruction(0x31, InstructionType.FN_CALL, [int, int])
add_instruction(0x32, InstructionType.RET, [])
add_instruction(0x33, InstructionType.RET_VALUE, [])
add_instruction(0x34, InstructionType.JZ, [int])
add_instruction(0x35, InstructionType.JMP, [int])

add_instruction(0x40, InstructionType.ADD_INT, [])
add_instruction(0x41, InstructionType.SUB_INT, [])
add_instruction(0x42, InstructionType.MUL_INT, [])
add_instruction(0x43, InstructionType.DIV_INT, [])
add_instruction(0x44, InstructionType.MOD_INT, [])
add_instruction(0x45, InstructionType.POW_INT, [])
add_instruction(0x46, InstructionType.ADD_FLOAT, [])
add_instruction(0x47, InstructionType.SUB_FLOAT, [])
add_instruction(0x48, InstructionType.MUL_FLOAT, [])
add_instruction(0x49, InstructionType.DIV_FLOAT, [])
add_instruction(0x4A, InstructionType.MOD_FLOAT, [])
add_instruction(0x4B, InstructionType.POW_FLOAT, [])

add_instruction(0x4C, InstructionType.UNARY_PLUS_INT, [])
add_instruction(0x4D, InstructionType.UNARY_MINUS_INT, [])
add_instruction(0x4E, InstructionType.UNARY_PLUS_FLOAT, [])
add_instruction(0x4F, InstructionType.UNARY_MINUS_FLOAT, [])

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

# will take array at arg1 slot and fill it with arg2 values from stack
add_instruction(0x60, InstructionType.ARRAY_FILL_LOCAL, [int, int])
add_instruction(0x61, InstructionType.ARRAY_FILL_GLOBAL, [int, int])

# will take array at arg1 slot and set the value at index from stack with value from stack
add_instruction(0x62, InstructionType.ARRAY_SET_VALUE_GLOBAL, [int])
add_instruction(0x63, InstructionType.ARRAY_SET_VALUE_LOCAL, [int])

add_instruction(0x70, InstructionType.TO_STDOUT, [int])
