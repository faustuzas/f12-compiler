from sys import argv

from lexer.lexer import Lexer
from models import error_counter
from models.scope import Scope
from parse.parser import Parser
from utils import printer

from utils.ast_printer import AstPrinter, FileOutput

file_to_compile = 'example_source/not_main.f12'
if len(argv) == 2:
    file_to_compile = argv[1]

with open(file_to_compile) as f:
    try:
        lexer = Lexer(''.join(f.readlines()), file_to_compile)
        lexer.lex_all()

        parser = Parser(lexer.tokens)
        ast_root = parser.parse()

        ast_root.resolve_includes()

        error_counter.reset()
        ast_root.resolve_names(Scope(None))
        ast_root.resolve_types()
        ast_root.check_for_entry_point()

        is_parsing_successful = error_counter.counter != 0

        if is_parsing_successful != 0:
            printer.error('', f'{error_counter.counter} errors found', header_len=80)
        else:
            printer.success('', f'Compilation successful', header_len=80)

        with FileOutput('parser-output.yaml') as output:
            ast_printer = AstPrinter(output)
            ast_printer.print('root', ast_root)
    except ValueError as e:
        pass
