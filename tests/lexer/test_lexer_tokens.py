from unittest import TestCase

from models import TokenType
from lexer.lexer import Lexer


class LexerTokensTests(TestCase):

    def test_last_token_eof(self):
        lexer = Lexer('+++')

        lexer.lex_all()

        self.assertEquals(TokenType.EOF, lexer.tokens[len(lexer.tokens) - 1].type)

    def test_op_plus(self):
        lexer = Lexer('+')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_PLUS, lexer.tokens[0].type)
        self.assertEqual(1, lexer.tokens[0].line_number)
