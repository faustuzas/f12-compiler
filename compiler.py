from sys import argv

from lexer.lexer import Lexer

file_to_lex = 'main.f12'
if len(argv) == 2:
    file_to_lex = argv[1]

with open(file_to_lex) as f:
    content = ''.join(f.readlines())

    try:
        lexer = Lexer(content, file_to_lex)
        lexer.lex_all()

        lexer.print_tokens()
    except ValueError:
        pass
