from models import Token, TokenType
from models.ast_nodes import Node


class AstPrinter:
    indent_level: int
    indent_magnifier: int

    def __init__(self) -> None:
        self.indent_level = 0
        self.indent_magnifier = 2

    def print(self, title, obj):
        if obj is None:
            self.print_text(title, 'None')
        if AstPrinter.is_primitive(obj):
            self.print_text(title, obj)
        elif isinstance(obj, list):
            self.print_list(title, obj)
        elif isinstance(obj, Node):
            self.print_node(title, obj)
        elif isinstance(obj, Token):
            self.print_token(title, obj)
        elif isinstance(obj, TokenType):
            self.print_text(title, str(obj))
        else:
            raise ValueError(f'Invalid print argument: {type(obj)}')

    def print_text(self, title, text: str):
        prefix = ' ' * self.indent_level
        print(f'{prefix}{title}: {text}')

    def print_list(self, title, array: list):
        if not array:
            self.print_text(title, '[]')
            return

        self.print_text(title, '')
        self.indent_level += self.indent_magnifier
        for (i, item) in enumerate(array):
            self.print(f'[{i}]', item)
        self.indent_level -= self.indent_magnifier

    def print_node(self, title, node: Node):
        self.print_text(title, f'{type(node).__name__}')
        self.indent_level += self.indent_magnifier
        node.print(self)
        self.indent_level -= self.indent_magnifier

    def print_token(self, title, token: Token):
        self.print_text(title, f'{token.value} ({token.file_name}:{token.line_number})')

    @staticmethod
    def is_primitive(obj):
        return type(obj) in (int, float, bool, str)
