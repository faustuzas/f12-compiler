from models import Token, primitive_type_tokens_names
from utils.error_printer import print_error_from_token as print_error


def extract_kind(type_):
    from models.ast_nodes import TypeUnit, TypeArray

    if isinstance(type_, TypeUnit):
        return type_.unit_name.value
    if isinstance(type_, TypeArray):
        return extract_kind(type_.inner_type)
    return type_.kind.type if isinstance(type_.kind, Token) else type_.kind


def prepare_for_printing(item):
    from models.ast_nodes import TypePrimitive, TypeUnit, TypeArray, TypePointer

    if isinstance(item, TypePrimitive):
        return primitive_type_tokens_names.get(extract_kind(item))
    if isinstance(item, TypeUnit):
        return item.unit_name
    if isinstance(item, TypeArray):
        return f'{prepare_for_printing(item.inner_type)}[]'
    if isinstance(item, TypePointer):
        of_type_postfix = f' of {prepare_for_printing(item.of_type)}' if item.of_type else ''
        return f'pointer{of_type_postfix}'
    return item.__class__.__name__


def unify_types(reference_token: Token, type_1, type_2, error_message=None):
    from models.ast_nodes import TypePrimitive, TypeUnit, TypePointer

    def p_error(expected, got, cause=None):
        if cause is None:
            cause = f'Expected: {prepare_for_printing(expected)}, got: {prepare_for_printing(got)}'
        print_error('Type mismatch', cause, reference_token)

    if type_1 is None or type_2 is None:
        return

    if type_1.__class__ != type_2.__class__:
        p_error(type_1, type_2, error_message)
    elif isinstance(type_1, TypePrimitive):
        if extract_kind(type_1) != extract_kind(type_2):
            p_error(type_1, type_2, error_message)
    elif isinstance(type_1, TypePointer):
        if type_1.of_type is None or type_2.of_type is None:
            return
        if extract_kind(type_1.of_type) != extract_kind(type_2.of_type):
            p_error(type_1, type_2, error_message)
    elif isinstance(type_1, TypeUnit):
        if type_1.unit_name.value != type_2.unit_name.value:
            p_error(type_1, type_2, error_message)
    else:
        raise Exception("Unreachable code")
