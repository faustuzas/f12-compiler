import struct

from models.types import Char, Int, String, Bool, Float
import utils.sizes as sizes


def op_code_to_bytes(op_code):
    return int_to_bytes(int(op_code), size=sizes.op_code)


def op_code_from_bytes(code, offset):
    return int_from_bytes(code, offset, size=sizes.op_code)


def select_from_bytes_func(type_):
    if type_ is Int:
        return int_from_bytes
    if type_ is String:
        return string_from_bytes
    if type_ is Bool:
        return bool_from_bytes
    if type_ is Float:
        return float_from_bytes
    if type_ is Char:
        return char_from_bytes
    raise TypeError(f'There is no from bytes function for: {type_}')


def select_to_bytes_func(type_):
    if type_ is Int:
        return int_to_bytes
    if type_ is String:
        return string_to_bytes
    if type_ is Bool:
        return bool_to_bytes
    if type_ is Float:
        return float_to_bytes
    if type_ is Char:
        return char_to_bytes
    raise TypeError(f'There is no to bytes function for: {type_}')


def int_to_bytes(value: int, size=sizes.int, order=sizes.int_order):
    return list(value.to_bytes(size, order, signed=True))


def int_from_bytes(code, offset, size=sizes.int, order=sizes.int_order):
    int_bytes = code[offset: offset + size]
    value = int.from_bytes(int_bytes, order, signed=True)
    return value, offset + size


def float_to_bytes(value: float):
    return list(struct.pack(f'<{sizes.float_type}', value))


def float_from_bytes(code, offset):
    float_bytes = bytes(code[offset: offset + sizes.float])
    value = struct.unpack(f'<{sizes.float_type}', float_bytes)
    return value[0], offset + sizes.float


def bool_to_bytes(value: bool):
    return int_to_bytes(1 if value else 0, size=1)


def bool_from_bytes(code, offset):
    val, offset = int_from_bytes(code, offset, size=1)
    return val == 1, offset


def string_to_bytes(value: str):
    bytes_ = int_to_bytes(len(value))
    bytes_.extend(bytes(value, sizes.string_encoding))
    return bytes_


def string_from_bytes(code, offset):
    string_size, offset = int_from_bytes(code, offset)
    string = str(bytes(code[offset: offset + string_size]), sizes.string_encoding)
    return string, offset + string_size


def char_to_bytes(char):
    return int_to_bytes(ord(char), sizes.char)


def char_from_bytes(code, offset):
    char = str(bytes(code[offset: offset + sizes.char]), sizes.string_encoding)
    return char, offset + sizes.char
