from sys import argv

from lexer.lexer import Lexer
from models.scope import Scope
from parse.parser import Parser

from utils.ast_printer import AstPrinter, FileOutput

file_to_compile = 'example_source/main.f12'
if len(argv) == 2:
    file_to_compile = argv[1]

with open(file_to_compile) as f:
    try:
        lexer = Lexer(''.join(f.readlines()), file_to_compile)
        lexer.lex_all()

        parser = Parser(lexer.tokens)
        ast_root = parser.parse()

        ast_root.resolve_includes()
        ast_root.resolve_names(Scope(None))
        ast_root.resolve_types()
        ast_root.check_for_entry_point()

        with FileOutput('parser-output.yaml') as output:
            ast_printer = AstPrinter(output)
            ast_printer.print('root', ast_root)
    except ValueError as e:
        pass
