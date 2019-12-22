import struct

from models.types import Char

bool_size = 1
char_size = 1
address_size = 4
op_code_size = 2

int_size = 4
int_order = 'big'

float_size = 8
float_type = 'd'

string_encoding = 'UTF-8'


def op_code_to_bytes(op_code):
    return int_to_bytes(int(op_code), size=op_code_size)


def op_code_from_bytes(code, offset):
    return int_from_bytes(code, offset, size=op_code_size)


def select_from_bytes_func(type_):
    if type_ is int:
        return int_from_bytes
    if type_ is str:
        return string_from_bytes
    if type_ is bool:
        return bool_from_bytes
    if type_ is float:
        return float_from_bytes
    if type_ is Char:
        return char_from_bytes
    raise TypeError(f'There is no from bytes function for: {type_}')


def select_to_bytes_func(type_):
    if type_ is int:
        return int_to_bytes
    if type_ is str:
        return string_to_bytes
    if type_ is bool:
        return bool_to_bytes
    if type_ is float:
        return float_to_bytes
    if type_ is Char:
        return char_to_bytes
    raise TypeError(f'There is no to bytes function for: {type_}')


def int_to_bytes(value: int, size=int_size, order=int_order):
    return list(value.to_bytes(size, order, signed=True))


def int_from_bytes(code, offset, size=int_size, order=int_order):
    int_bytes = code[offset: offset + size]
    value = int.from_bytes(int_bytes, order, signed=True)
    return value, offset + size


def float_to_bytes(value: float):
    return list(struct.pack(f'<{float_type}', value))


def float_from_bytes(code, offset):
    float_bytes = bytes(code[offset: offset + float_size])
    value = struct.unpack(f'<{float_type}', float_bytes)
    return value[0], offset + float_size


def bool_to_bytes(value: bool):
    return int_to_bytes(1 if value else 0, size=1)


def bool_from_bytes(code, offset):
    val, offset = int_from_bytes(code, offset, size=1)
    return val == 1, offset


def string_to_bytes(value: str):
    bytes_ = int_to_bytes(len(value))
    bytes_.extend(bytes(value, string_encoding))
    return bytes_


def string_from_bytes(code, offset):
    string_size, offset = int_from_bytes(code, offset)
    string = str(bytes(code[offset: offset + string_size]), string_encoding)
    return string, offset + string_size


def char_to_bytes(char):
    return int_to_bytes(ord(char), char_size)


def char_from_bytes(code, offset):
    char = str(bytes(code[offset: offset + char_size]), string_encoding)
    return char, offset + char_size
