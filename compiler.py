from sys import argv

from lexer.lexer import Lexer
from parse.parser import Parser

from utils.ast_printer import AstPrinter

file_to_compile = 'not_main.f12'
if len(argv) == 2:
    file_to_compile = argv[1]

with open(file_to_compile) as f:
    content = ''.join(f.readlines())

    try:
        lexer = Lexer(content, file_to_compile)
        lexer.lex_all()

        parser = Parser(lexer.tokens)
        ast_root = parser.parse()

        ast_printer = AstPrinter()
        ast_printer.print('root', ast_root)

    except ValueError as e:
        print("EXCEPTION CAUGHT:")
        print(e)