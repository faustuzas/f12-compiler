from models import Token
from utils.error_printer import print_error


class Scope:

    def __init__(self, parent_scope) -> None:
        self.parent_scope = parent_scope
        self.members = {}

    def add(self, name_token: Token, node) -> None:
        name = name_token.value

        if name not in self.members:
            self.members[name] = node
        else:
            print_error(
                'Names resolution',
                f'Item with identifier "{name}" is already declared',
                name_token.line_number,
                name_token.offset_in_line,
                name_token.file_name)

    def resolve_name(self, name_token: Token):
        name = name_token.value

        node = self.members.get(name, None)
        if node:
            return node

        if self.parent_scope:
            return self.parent_scope.resolve_name(name_token)

        print_error(
            'Names resolution',
            f'Item with identifier "{name}" is not declared',
            name_token.line_number,
            name_token.offset_in_line,
            name_token.file_name)
