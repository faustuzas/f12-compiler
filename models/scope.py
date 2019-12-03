from models import Token
from utils.error_printer import print_error_from_token as print_error


class Scope:

    def __init__(self, parent_scope) -> None:
        self.parent_scope = parent_scope
        self.members = {}

    def add(self, name_token: Token, node) -> None:
        name = name_token.value

        if name not in self.members:
            self.members[name] = node
        else:
            print_error('Names resolution', f'Item with name "{name}" is already declared', name_token)

    def resolve_name(self, name_token: Token):
        name = name_token.value

        node = self.members.get(name, None)
        if node:
            return node

        if self.parent_scope:
            return self.parent_scope.resolve_name(name_token)

        print_error('Names resolution', f'Item with name "{name}" is not declared', name_token)
