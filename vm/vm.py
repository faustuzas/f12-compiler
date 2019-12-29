import utils.bytes_utils as codec
from models import types

from utils import FasterSwitcher as Switcher, throw, sizes
from models.instructions import op_code_by_type as op_codes, InstructionType as IType, instructions_by_op_code
from utils.list_utils import resize

total_memory = 1024 * 1024
total_memory = 50
pointer_size = sizes.int


class VM:

    def __init__(self, opcodes) -> None:
        self.running = True

        self.memory = opcodes.copy()
        resize(self.memory, total_memory, 0)

        self.ip = 0
        self.fp = len(opcodes)
        self.sp = len(opcodes)

    def exec(self):
        while self.running:
            self.exec_one()

    op_codes_actions = Switcher.from_dict({
        op_codes.get(IType.FN_CALL_BEGIN): lambda ctx: ctx.fn_call_begin(),
        op_codes.get(IType.FN_CALL): lambda ctx: ctx.fn_call(ctx.read_int(), ctx.read_int()),
        op_codes.get(IType.EXIT): lambda ctx: exit(0),
        op_codes.get(IType.PUSH_CHAR): lambda ctx: ctx.push(ctx.read_char(), types.Char),
        op_codes.get(IType.TO_STDOUT_CHAR): lambda ctx: ctx.to_stdout(types.Char),
        op_codes.get(IType.RET): lambda ctx: ctx.ret()
    }).default(lambda ctx: throw(ValueError('OP code does not exist')))

    def exec_one(self):
        op_code = self.read_op_code()
        if instructions_by_op_code.get(op_code) is None:
            print('a')
        self.op_codes_actions.exec(self, op_code)

    def fn_call_begin(self):
        self.push(0)
        self.push(0)
        self.push(0)

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

    def to_stdout(self, type_: types.Type):
        print(self.pop(type_), end='')

    """
    Helpers
    """
    def push(self, value, type_=None):
        bytes_pushed = self.set_value(self.sp, value, type_)
        self.sp += bytes_pushed

    def pop(self, type_: types.Type):
        self.sp -= type_.size_in_bytes()
        val, _ = self.get_value(self.sp, type_)
        return val

    def read_op_code(self):
        op_code, self.ip = codec.op_code_from_bytes(self.memory, self.ip)
        return op_code

    def read_int(self):
        int_, self.ip = codec.int_from_bytes(self.memory, self.ip)
        return int_

    def read_char(self):
        char_, self.ip = codec.char_from_bytes(self.memory, self.ip)
        return char_

    def get_value(self, start, type_):
        return codec.select_from_bytes_func(type_)(self.memory, start)

    def set_value(self, start, value, type_=None):
        if type_ is None:
            type_ = types.find_type(type(value))
        bytes_ = codec.select_to_bytes_func(type_)(value)
        self.set_bytes(start, bytes_)
        return len(bytes_)

    def set_bytes(self, offset, bytes_):
        for i in range(len(bytes_)):
            self.memory[offset + i] = bytes_[i]
