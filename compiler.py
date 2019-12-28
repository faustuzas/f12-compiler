from sys import argv

from codegen.code_writer import CodeWriter
from lexer.lexer import Lexer
from models.errors import error_counter
from models.scope import Scope
from parse.parser import Parser
from utils import printer

from utils.ast_printer import AstPrinter, FileOutput


def compile_file(file_to_compile):
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

            is_parsing_successful = error_counter.counter == 0
            if not is_parsing_successful:
                printer.error('', f'{error_counter.counter} errors found', header_len=80)
                return
            else:
                printer.success('', f'Compilation successful', header_len=80)

            with FileOutput('ast_tree.yaml') as output:
                ast_printer = AstPrinter(output)
                ast_printer.print('root', ast_root)

            code_writer = CodeWriter()
            ast_root.write_code(code_writer)

            with FileOutput('instructions.f12b') as output:
                code_writer.print_instructions(output)

            with FileOutput('output.f12b') as output:
                code_writer.dump_code(output)
        except ValueError as e:
            print(e)
            pass


if __name__ == '__main__':
    file = 'example_source/not2_main.f12'
    if len(argv) == 2:
        file = argv[1]
    compile_file(file)
