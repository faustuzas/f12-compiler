from models.token import Token
from utils.error_printer import print_error_from_token as print_error


def select_compare_func(type_):
    from models.ast_nodes import AstTypePrimitive, AstTypePointer, AstTypeArray

    if isinstance(type_, AstTypePrimitive):
        return compare_primitives
    elif isinstance(type_, AstTypePointer):
        return compare_pointers
    elif isinstance(type_, AstTypeArray):
        return compare_array
    else:
        raise NotImplementedError(str(type_))


def compare_pointers(pointer1, pointer2) -> bool:
    of_type1 = pointer1.of_type
    of_type2 = pointer2.of_type

    if of_type1 is None or of_type2 is None:
        return True

    if type(of_type1) != type(of_type2):
        return False

    return select_compare_func(of_type1)(of_type1, of_type2)


def compare_primitives(primitive1, primitive2) -> bool:
    return primitive1.type == primitive2.type


def compare_array(array1, array2) -> bool:
    inner_type1 = array1.inner_type
    inner_type2 = array2.inner_type

    if inner_type1 is None or inner_type2 is None:
        return True

    if type(inner_type1) != type(inner_type2):
        return False

    return select_compare_func(inner_type1)(inner_type1, inner_type2)


def prepare_for_printing(item):
    from models.ast_nodes import AstTypePrimitive, AstTypeUnit, AstTypeArray, AstTypePointer

    if isinstance(item, AstTypePrimitive):
        return item.type.name_in_code()
    if isinstance(item, AstTypeUnit):
        return item.name.value
    if isinstance(item, AstTypeArray):
        return f'{prepare_for_printing(item.inner_type)}[]'
    if isinstance(item, AstTypePointer):
        of_type_postfix = f' of {prepare_for_printing(item.of_type)}' if item.of_type else ''
        return f'pointer{of_type_postfix}'
    return item.__class__.__name__


def unify_types(reference_token: Token, type_1, type_2, error_message=None):

    def p_error(expected, got, cause=None):
        if cause is None:
            cause = f'Expected: {prepare_for_printing(expected)}, got: {prepare_for_printing(got)}'
        print_error('Type mismatch', cause, reference_token)

    if type_1 is None or type_2 is None:
        return
    elif type_1.__class__ != type_2.__class__:
        p_error(type_1, type_2, error_message)
    else:
        if not select_compare_func(type_1)(type_1, type_2):
            p_error(type_1, type_2, error_message)
