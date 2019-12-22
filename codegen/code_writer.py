from models.instructions import InstructionType, instructions_by_type, instructions_by_op_code
import utils.bytes_utils as codec

op_code_size_in_bytes = 1
label_placeholder = codec.select_to_bytes_func(int)(0)


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
        self.static_strings = []

    def start_loop(self, start_label, end_label):
        self.loops_stack.append((start_label, end_label))

    def end_loop(self):
        self.loops_stack.pop()

    def current_loop(self):
        return self.loops_stack[-1]

    def place_label(self, label):
        label.value = codec.select_to_bytes_func(int)(len(self.code))
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

        self.code.extend(codec.op_code_to_bytes(instruction.op_code))
        for i, op_type in enumerate(instruction.ops_types):
            operand = operands[i]
            if isinstance(operand, Label):
                if operand.value is None:
                    operand.add_offset(len(self.code))
                    self.code.extend(label_placeholder)
                else:
                    self.code.extend(operand.value)
            else:
                self.code.extend(codec.select_to_bytes_func(op_type)(operand))

    def write_raw(self, item, type_):
        self.code.extend(codec.select_to_bytes_func(type_)(item))

    def print_instructions(self, output):
        output.out('{:s} | {:s} | {:>25s} |  {:s}'.format('Offset', 'Op code', 'Instruction', 'Operands'))
        offset = 0
        while offset < len(self.code):
            start_offset = offset
            op_code, offset = codec.op_code_from_bytes(self.code, offset)

            instr = instructions_by_op_code.get(op_code)
            if instr is None:
                raise TypeError(f'There is no instruction with op_code: {op_code}')

            if instr.type == InstructionType.MARKER_STATIC_START:
                offset = self.print_static_strings(output, offset)
                continue

            (ops, offset) = instr.fetch_ops(self.code, offset)
            ops = list(map(lambda x: str(x), ops))
            output.out('{:6d}      0x{:x} {:>27s}    {:3s}'.format(start_offset, op_code, instr.type, ', '.join(ops)))

    def print_static_strings(self, output, offset):
        padding = '*' * 20
        output.out(f'\n{padding} STATIC STRINGS {padding}')
        start_offset = offset
        value, offset = codec.select_from_bytes_func(str)(self.code, offset)
        output.out('{:6d}      {:s}'.format(start_offset, value))
        return offset

    def dump_code(self, output):
        str_code = list(map(lambda x: str(x), self.code))
        output.out(''.join(str_code))
