from models.token import Token
from utils.error_printer import print_error_from_token as print_error


def extract_kind(type_):
    from models.ast_nodes import AstTypeUnit, AstTypeArray

    if isinstance(type_, AstTypeUnit):
        return type_.unit_name.value
    if isinstance(type_, AstTypeArray):
        return extract_kind(type_.inner_type)
    return type_.kind.type if isinstance(type_.kind, Token) else type_.kind


def prepare_for_printing(item):
    from models.ast_nodes import AstTypePrimitive, AstTypeUnit, AstTypeArray, AstTypePointer

    if isinstance(item, AstTypePrimitive):
        return primitive_type_tokens_names.get(extract_kind(item))
    if isinstance(item, AstTypeUnit):
        return item.unit_name
    if isinstance(item, AstTypeArray):
        return f'{prepare_for_printing(item.inner_type)}[]'
    if isinstance(item, AstTypePointer):
        of_type_postfix = f' of {prepare_for_printing(item.of_type)}' if item.of_type else ''
        return f'pointer{of_type_postfix}'
    return item.__class__.__name__


def unify_types(reference_token: Token, type_1, type_2, error_message=None):
    from models.ast_nodes import AstTypePrimitive, AstTypeUnit, AstTypePointer

    def p_error(expected, got, cause=None):
        if cause is None:
            cause = f'Expected: {prepare_for_printing(expected)}, got: {prepare_for_printing(got)}'
        print_error('Type mismatch', cause, reference_token)

    if type_1 is None or type_2 is None:
        return

    if type_1.__class__ != type_2.__class__:
        p_error(type_1, type_2, error_message)
    elif isinstance(type_1, AstTypePrimitive):
        if extract_kind(type_1) != extract_kind(type_2):
            p_error(type_1, type_2, error_message)
    elif isinstance(type_1, AstTypePointer):
        if type_1.of_type is None or type_2.of_type is None:
            return
        if extract_kind(type_1.of_type) != extract_kind(type_2.of_type):
            p_error(type_1, type_2, error_message)
    elif isinstance(type_1, AstTypeUnit):
        if type_1.unit_name.value != type_2.unit_name.value:
            p_error(type_1, type_2, error_message)
    else:
        raise Exception("Unreachable code")
