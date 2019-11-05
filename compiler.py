from sys import argv

from lexer.lexer import Lexer
from parse.parser import Parser

from utils.ast_printer import AstPrinter, FileOutput

file_to_compile = 'main.f12'
if len(argv) == 2:
    file_to_compile = argv[1]

with open(file_to_compile) as f:
    content = ''.join(f.readlines())

    try:
        lexer = Lexer(content, file_to_compile)
        lexer.lex_all()

        parser = Parser(lexer.tokens, content)
        ast_root = parser.parse()

        with FileOutput('parser-output.yaml') as output:
            ast_printer = AstPrinter(output)
            ast_printer.print('root', ast_root)
    except ValueError as e:
        pass
