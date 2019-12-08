from models.instructions import InstructionType, instructions_by_type, instructions_by_op_code
from utils.bytes_utils import select_to_bytes_func, op_code_to_bytes

op_code_size_in_bytes = 1
label_placeholder = select_to_bytes_func(int)(0)


class Label:

    def __init__(self) -> None:
        self.offsets = []
        self.value = None

    def add_offset(self, offset):
        self.offsets.append(offset)


class CodeWriter:

    def __init__(self) -> None:
        self.code = []
        self.loops_stack = []

    def start_loop(self, start_label, end_label):
        self.loops_stack.append((start_label, end_label))

    def end_loop(self):
        self.loops_stack.pop()

    def current_loop(self):
        return self.loops_stack[-1]

    def place_label(self, label):
        label.value = select_to_bytes_func(int)(len(self.code))
        for offset in label.offsets:
            for i, byte_val in enumerate(label.value):
                self.code[offset + i] = byte_val

    def write(self, instr_type: InstructionType, *operands):
        instruction = instructions_by_type.get(instr_type)

        if instruction is None:
            raise TypeError(f'Instruction {instr_type} not defined')

        if len(instruction.ops_types) != len(operands):
            raise TypeError(f'Invalid instruction {instruction.type} operand count. '
                            f'Expected: {len(instruction.ops_types)}, got: {len(operands)}')

        self.code.extend(op_code_to_bytes(instruction.op_code))
        for i, op_type in enumerate(instruction.ops_types):
            operand = operands[i]
            if isinstance(operand, Label):
                if operand.value is None:
                    operand.add_offset(len(self.code))
                    self.code.extend(label_placeholder)
                else:
                    self.code.extend(operand.value)
            else:
                self.code.extend(select_to_bytes_func(op_type)(operand))

    def print_instructions(self, output):
        offset = 0
        while offset < len(self.code):
            start_offset = offset
            op_code = self.code[offset]
            offset += op_code_size_in_bytes

            instr = instructions_by_op_code.get(op_code)
            if instr is None:
                raise TypeError(f'There is no instruction with op_code: {op_code}')

            (ops, offset) = instr.fetch_ops(self.code, offset)
            ops = list(map(lambda x: str(x), ops))
            output.out('{:4d}: 0x{:2x} {:>25s}    {:s}'.format(start_offset, op_code, instr.type, ', '.join(ops)))

    def dump_code(self, output):
        str_code = list(map(lambda x: str(x), self.code))
        output.out(''.join(str_code))
