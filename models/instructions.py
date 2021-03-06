from models.enums import ExtendedEnum
from models.types import Char, Int, Bool, Float
from utils.bytes_utils import select_from_bytes_func


class InstructionType(ExtendedEnum):
    NOT = 'NOT'

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

    ALLOCATE_IN_STACK = 'ALLOCATE_IN_STACK'
    SET_GLOBAL = 'SET_GLOBAL'
    SET_LOCAL = 'SET_LOCAL'
    GET_GLOBAL = 'GET_GLOBAL'
    GET_LOCAL = 'GET_LOCAL'

    POP = 'POP'
    PUSH_INT = 'PUSH_INT'
    PUSH_FLOAT = 'PUSH_FLOAT'
    PUSH_CHAR = 'PUSH_CHAR'
    PUSH_BOOL = 'PUSH_BOOL'
    POP_PUSH_N = 'POP_PUSH_N'

    MEMORY_ALLOCATE = 'MEMORY_ALLOCATE'
    MEMORY_FREE = 'MEMORY_FREE'

    MEMORY_SET = 'MEMORY_SET'
    MEMORY_SET_PUSH = 'MEMORY_SET_PUSH'
    MEMORY_GET = 'MEMORY_GET'

    TO_STDOUT_INT = 'TO_STDOUT_INT'
    TO_STDOUT_FLOAT = 'TO_STDOUT_FLOAT'
    TO_STDOUT_STRING = 'TO_STDOUT_STRING'
    TO_STDOUT_CHAR = 'TO_STDOUT_CHAR'
    TO_STDOUT_BOOL = 'TO_STDOUT_BOOL'

    FROM_STDIN = 'FROM_STDIN'

    CLEAR_SCREEN = 'CLEAR_SCREEN'
    PUT_CHAR_X_Y = 'PUT_CHAR_X_Y'
    GET_INPUT = 'GET_INPUT'
    SLEEP = 'SLEEP'

    EXIT = 'EXIT'
    MARKER_STATIC_START = 'MARKER_STATIC_START'


class Instruction:

    def __init__(self, op_code, type_: InstructionType, ops_types) -> None:
        self.op_code = op_code
        self.type = type_
        self.ops_types = ops_types

    def fetch_ops(self, code, offset):
        ops = []
        for op_type in self.ops_types:
            value, offset = select_from_bytes_func(op_type)(code, offset)
            if value == '\n':
                value = '\\n'
            ops.append(value)

        return ops, offset


instructions_by_type = {}
instructions_by_op_code = {}
op_code_by_type = {}


def add_instruction(op_code, type_, ops_types):
    inst = Instruction(op_code, type_, ops_types)
    instructions_by_type[type_] = inst
    instructions_by_op_code[op_code] = inst
    op_code_by_type[type_] = op_code


# Pop N bytes from stack
add_instruction(0x10, InstructionType.POP, [Int])
# Pop N bytes from stack and push them K times
add_instruction(0x11, InstructionType.POP_PUSH_N, [Int, Int])
add_instruction(0x12, InstructionType.PUSH_INT, [Int])
add_instruction(0x13, InstructionType.PUSH_BOOL, [Bool])
add_instruction(0x14, InstructionType.PUSH_FLOAT, [Float])
add_instruction(0x15, InstructionType.PUSH_CHAR, [Char])

#  Set/Get from X address N bytes
add_instruction(0x20, InstructionType.ALLOCATE_IN_STACK, [Int])
add_instruction(0x21, InstructionType.SET_GLOBAL, [Int, Int])
add_instruction(0x22, InstructionType.SET_LOCAL, [Int, Int])
add_instruction(0x23, InstructionType.GET_GLOBAL, [Int, Int])
add_instruction(0x24, InstructionType.GET_LOCAL, [Int, Int])

add_instruction(0x30, InstructionType.FN_CALL_BEGIN, [])
add_instruction(0x31, InstructionType.FN_CALL, [Int, Int])
add_instruction(0x32, InstructionType.RET, [])
#  Return N bytes
add_instruction(0x33, InstructionType.RET_VALUE, [Int])
add_instruction(0x34, InstructionType.JZ, [Int])
add_instruction(0x35, InstructionType.JMP, [Int])

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

add_instruction(0x50, InstructionType.NOT, [])
add_instruction(0x51, InstructionType.OR, [])
add_instruction(0x52, InstructionType.AND, [])
add_instruction(0x53, InstructionType.EQ, [Int])
add_instruction(0x54, InstructionType.NE, [Int])
add_instruction(0x55, InstructionType.GT_INT, [])
add_instruction(0x56, InstructionType.GE_INT, [])
add_instruction(0x57, InstructionType.LT_INT, [])
add_instruction(0x58, InstructionType.LE_INT, [])
add_instruction(0x59, InstructionType.GT_FLOAT, [])
add_instruction(0x5A, InstructionType.GE_FLOAT, [])
add_instruction(0x5B, InstructionType.LT_FLOAT, [])
add_instruction(0x5C, InstructionType.LE_FLOAT, [])

#  Pop integer from stack, allocate that much memory and push address of allocated memory to stack
add_instruction(0x60, InstructionType.MEMORY_ALLOCATE, [])
#  Pop integer from stack and free the memory at the address
add_instruction(0x61, InstructionType.MEMORY_FREE, [])
#  Pop integer from stack then pop N bytes from stack and set them at the address provided
add_instruction(0x62, InstructionType.MEMORY_SET, [Int])
#  Same as MEMORY_SET but additionally pushes the address back into memory
add_instruction(0x63, InstructionType.MEMORY_SET_PUSH, [Int, Int])
#  Pop address from stack and push N bytes from that address
add_instruction(0x64, InstructionType.MEMORY_GET, [Int])

add_instruction(0x70, InstructionType.TO_STDOUT_INT, [])
add_instruction(0x71, InstructionType.TO_STDOUT_FLOAT, [])
add_instruction(0x72, InstructionType.TO_STDOUT_STRING, [])
add_instruction(0x73, InstructionType.TO_STDOUT_CHAR, [])
add_instruction(0x74, InstructionType.TO_STDOUT_BOOL, [])
add_instruction(0x75, InstructionType.FROM_STDIN, [])

# Std functions
add_instruction(0xA0, InstructionType.CLEAR_SCREEN, [])
add_instruction(0xA1, InstructionType.PUT_CHAR_X_Y, [])
add_instruction(0xA2, InstructionType.GET_INPUT, [])
add_instruction(0xA3, InstructionType.SLEEP, [])

add_instruction(0xE0, InstructionType.MARKER_STATIC_START, [])
add_instruction(0xE1, InstructionType.EXIT, [])
