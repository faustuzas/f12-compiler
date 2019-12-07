default_int_size = 4
default_int_order = 'big'

string_encoding = 'UTF-8'


def op_code_to_bytes(op_code):
    return int_to_bytes(int(op_code), int_size=1)


def op_code_from_bytes(code, offset):
    return int_from_bytes(code, offset, int_size=1)


def select_from_bytes_func(type_):
    if type_ is int:
        return int_from_bytes
    if type_ is str:
        return string_from_bytes
    if type_ is bool:
        return bool_from_bytes
    raise TypeError(f'There is no from bytes function for: {type_}')


def select_to_bytes_func(type_):
    if type_ is int:
        return int_to_bytes
    if type_ is str:
        return string_to_bytes
    if type_ is bool:
        return bool_to_bytes
    raise TypeError(f'There is no to bytes function for: {type_}')


def int_to_bytes(value: int, int_size=default_int_size, int_order=default_int_order):
    return list(value.to_bytes(int_size, int_order, signed=True))


def int_from_bytes(code, offset, int_size=default_int_size, int_order=default_int_order):
    int_bytes = code[offset: offset + int_size]
    offset += int_size
    value = int.from_bytes(int_bytes, int_order, signed=True)
    return value, offset


def bool_to_bytes(value: bool):
    return int_to_bytes(1 if value else 0, int_size=1)


def bool_from_bytes(code, offset):
    val, offset = int_from_bytes(code, offset, int_size=1)
    return val == 1, offset


def string_to_bytes(value: str):
    bytes_ = int_to_bytes(len(value))
    bytes_.extend(bytes(value, string_encoding))
    return bytes_


def string_from_bytes(code, offset):
    string_size, offset = int_from_bytes(code, offset)
    string = str(bytes(code[offset: offset + string_size]), string_encoding)
    offset += string_size
    return string, offset
