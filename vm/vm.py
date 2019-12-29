from typing import Type

import utils.bytes_utils as codec
from models import types

from utils import FasterSwitcher as Switcher, throw, sizes
from models.instructions import op_code_by_type as op_codes, InstructionType as IType, instructions_by_op_code
from utils.list_utils import resize

total_memory = 1024 * 1024
pointer_size = sizes.int


class VM:

    def __init__(self, opcodes) -> None:
        self.running = True

        self.memory = opcodes.copy()
        resize(self.memory, total_memory, 0)

        # instruction pointer
        self.ip = 0
        # stack frame pointer
        self.fp = len(opcodes)
        # stack pointer
        self.sp = len(opcodes)
        # global variables pointer
        self.gp = len(opcodes)

    def exec(self):
        while self.running:
            self.exec_one()

    op_codes_actions = Switcher.from_dict({
        op_codes.get(IType.POP): lambda ctx: ctx.pop_bytes(ctx.read_int()),
        op_codes.get(IType.POP_PUSH_N): lambda ctx: ctx.pop_push_n(ctx.read_int(), ctx.read_int()),
        op_codes.get(IType.PUSH_INT): lambda ctx: ctx.push_type(ctx.read_int(), types.Int),
        op_codes.get(IType.PUSH_FLOAT): lambda ctx: ctx.push_type(ctx.read_float(), types.Float),
        op_codes.get(IType.PUSH_CHAR): lambda ctx: ctx.push_type(ctx.read_char(), types.Char),
        op_codes.get(IType.PUSH_BOOL): lambda ctx: ctx.push_type(ctx.read_bool(), types.Bool),

        op_codes.get(IType.ALLOCATE_GLOBAL): lambda ctx: ctx.allocate_global(ctx.read_int()),
        op_codes.get(IType.SET_GLOBAL):
            lambda ctx: ctx.set_bytes(ctx.gp + ctx.read_int(), ctx.pop_bytes(ctx.read_int())),
        op_codes.get(IType.SET_LOCAL):
            lambda ctx: ctx.set_bytes(ctx.fp + ctx.read_int(), ctx.pop_bytes(ctx.read_int())),
        op_codes.get(IType.GET_GLOBAL):
            lambda ctx: ctx.push_bytes(ctx.get_bytes(ctx.gp + ctx.read_int(), ctx.read_int())),
        op_codes.get(IType.GET_LOCAL):
            lambda ctx: ctx.push_bytes(ctx.get_bytes(ctx.fp + ctx.read_int(), ctx.read_int())),
        op_codes.get(IType.JZ): lambda ctx: ctx.jump(ctx.read_int(), not ctx.pop_type(types.Bool)),
        op_codes.get(IType.JMP): lambda ctx: ctx.jump(ctx.read_int()),

        op_codes.get(IType.FN_CALL_BEGIN): lambda ctx: ctx.fn_call_begin(),
        op_codes.get(IType.FN_CALL): lambda ctx: ctx.fn_call(ctx.read_int(), ctx.read_int()),
        op_codes.get(IType.RET): lambda ctx: ctx.ret(),
        op_codes.get(IType.RET_VALUE): lambda ctx: ctx.ret_value(ctx.read_int()),

        op_codes.get(IType.EXIT): lambda ctx: ctx.exit(),
        op_codes.get(IType.TO_STDOUT_INT): lambda ctx: ctx.to_stdout(types.Int),
        op_codes.get(IType.TO_STDOUT_FLOAT): lambda ctx: ctx.to_stdout(types.Float),
        op_codes.get(IType.TO_STDOUT_CHAR): lambda ctx: ctx.to_stdout(types.Char),
        op_codes.get(IType.TO_STDOUT_BOOL): lambda ctx: ctx.to_stdout(types.Bool),
        op_codes.get(IType.TO_STDOUT_STRING): lambda ctx: ctx.to_stdout(types.String)
    }).default(lambda ctx: ctx.behaviour_not_defined())

    def exec_one(self):
        op_code = self.read_op_code()
        if instructions_by_op_code.get(op_code) is None:
            self.op_code_not_defined()
        self.op_codes_actions.exec(self, op_code)

    def fn_call_begin(self):
        self.push_type(0)
        self.push_type(0)
        self.push_type(0)

    def fn_call(self, target, args_offset):
        new_ip = target
        new_fp = self.sp - args_offset
        new_sp = new_fp

        self.set_value(new_fp - 3 * pointer_size, self.ip)
        self.set_value(new_fp - 2 * pointer_size, self.fp)
        self.set_value(new_fp - 1 * pointer_size, new_fp - 3 * pointer_size)

        self.ip = new_ip
        self.fp = new_fp
        self.sp = new_sp

    def ret(self):
        old_ip, _ = self.get_value(self.fp - 3 * pointer_size, types.Int)
        old_fp, _ = self.get_value(self.fp - 2 * pointer_size, types.Int)
        old_sp, _ = self.get_value(self.fp - 1 * pointer_size, types.Int)

        self.ip = old_ip
        self.fp = old_fp
        self.sp = old_sp

    def ret_value(self, bytes_count):
        bytes_to_return = self.pop_bytes(bytes_count)
        self.ret()
        self.push_bytes(bytes_to_return)

    def allocate_global(self, bytes_len):
        self.sp += bytes_len

    def jump(self, address, conditional=True):
        if conditional:
            self.ip = address

    def to_stdout(self, type_: Type[types.Type]):
        if type_ is types.String:
            address = self.pop_type(types.Int)
            value_to_print, _ = codec.string_from_bytes(self.memory, address)
        else:
            value_to_print = self.pop_type(type_)
        print(value_to_print, end='')

    def op_code_not_defined(self):
        self.ip -= sizes.op_code
        op_code = self.read_op_code()
        throw(ValueError('Op code 0x{:x} is not defined'.format(op_code)))

    def behaviour_not_defined(self):
        self.ip -= sizes.op_code
        op_code = self.read_op_code()
        instr = instructions_by_op_code.get(op_code)
        throw(ValueError(f'Behaviour for {instr.type} is not defined'))

    def exit(self):
        self.running = False

    """
    Helpers
    """
    def push_type(self, value, type_=None):
        bytes_pushed = self.set_value(self.sp, value, type_)
        self.sp += bytes_pushed

    def push_bytes(self, bytes_):
        self.set_bytes(self.sp, bytes_)
        self.sp += len(bytes_)

    def pop_bytes(self, count):
        self.sp -= count
        return self.get_bytes(self.sp, count)

    def pop_type(self, type_: Type[types.Type]):
        self.sp -= type_.size_in_bytes()
        val, _ = self.get_value(self.sp, type_)
        return val

    def read_op_code(self):
        op_code, self.ip = codec.op_code_from_bytes(self.memory, self.ip)
        return op_code

    def read_int(self):
        int_, self.ip = codec.int_from_bytes(self.memory, self.ip)
        return int_

    def read_float(self):
        float_, self.ip = codec.float_from_bytes(self.memory, self.ip)
        return float_

    def read_char(self):
        char_, self.ip = codec.char_from_bytes(self.memory, self.ip)
        return char_

    def read_bool(self):
        bool_, self.ip = codec.bool_from_bytes(self.memory, self.ip)
        return bool_

    def get_value(self, start, type_):
        return codec.select_from_bytes_func(type_)(self.memory, start)

    def get_bytes(self, offset, bytes_len):
        return self.memory[offset:offset + bytes_len]

    def set_value(self, start, value, type_=None):
        if type_ is None:
            type_ = types.find_type(type(value))
        bytes_ = codec.select_to_bytes_func(type_)(value)
        self.set_bytes(start, bytes_)
        return len(bytes_)

    def set_bytes(self, offset, bytes_):
        for i in range(len(bytes_)):
            self.memory[offset + i] = bytes_[i]