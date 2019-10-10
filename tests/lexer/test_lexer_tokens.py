from unittest import TestCase

from models import TokenType
from lexer.lexer import Lexer


class LexerTokensTests(TestCase):

    def test_op_plus(self):
        lexer = Lexer('+')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_PLUS, lexer.tokens[0].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[1].type)

    def test_op_plus_2(self):
        lexer = Lexer('+ + +')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_PLUS, lexer.tokens[0].type)
        self.assertEqual(TokenType.OP_PLUS, lexer.tokens[1].type)
        self.assertEqual(TokenType.OP_PLUS, lexer.tokens[2].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[3].type)

    def test_op_minus(self):
        lexer = Lexer('-')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_MINUS, lexer.tokens[0].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[1].type)

    def test_op_minus_2(self):
        lexer = Lexer('---')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_MINUS, lexer.tokens[0].type)
        self.assertEqual(TokenType.OP_MINUS, lexer.tokens[1].type)
        self.assertEqual(TokenType.OP_MINUS, lexer.tokens[2].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[3].type)

    def test_op_minus_3(self):
        lexer = Lexer('- - -')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_MINUS, lexer.tokens[0].type)
        self.assertEqual(TokenType.OP_MINUS, lexer.tokens[1].type)
        self.assertEqual(TokenType.OP_MINUS, lexer.tokens[2].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[3].type)

    def test_to_stdout(self):
        lexer = Lexer('-->')

        lexer.lex_all()

        self.assertEqual(TokenType.KW_TO_STDOUT, lexer.tokens[0].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[1].type)

    def test_to_stdout_2(self):
        lexer = Lexer('--->---->-->-')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_MINUS, lexer.tokens[0].type)
        self.assertEqual(TokenType.KW_TO_STDOUT, lexer.tokens[1].type)
        self.assertEqual(TokenType.OP_MINUS, lexer.tokens[2].type)
        self.assertEqual(TokenType.OP_MINUS, lexer.tokens[3].type)
        self.assertEqual(TokenType.KW_TO_STDOUT, lexer.tokens[4].type)
        self.assertEqual(TokenType.KW_TO_STDOUT, lexer.tokens[5].type)
        self.assertEqual(TokenType.OP_MINUS, lexer.tokens[6].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[7].type)

    def test_div(self):
        lexer = Lexer('/ /')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_DIV, lexer.tokens[0].type)
        self.assertEqual(TokenType.OP_DIV, lexer.tokens[1].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[2].type)

    def test_single_comment(self):
        lexer = Lexer('+ // test + test - test')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_PLUS, lexer.tokens[0].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[1].type)

    def test_single_comment_2(self):
        lexer = Lexer('\n / \n + // test + test - test \n - \n')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_DIV, lexer.tokens[0].type)
        self.assertEqual(2, lexer.tokens[0].line_number)
        self.assertEqual(TokenType.OP_PLUS, lexer.tokens[1].type)
        self.assertEqual(3, lexer.tokens[1].line_number)
        self.assertEqual(TokenType.OP_MINUS, lexer.tokens[2].type)
        self.assertEqual(4, lexer.tokens[2].line_number)
        self.assertEqual(TokenType.EOF, lexer.tokens[3].type)

    # def test_multi_comment_start(self):
    #     lexer = Lexer('/* /* /*')
    #
    #     lexer.lex_all()
    #
    #     self.assertEqual(TokenType.MULTI_COMMENT_START, lexer.tokens[0].type)
    #     self.assertEqual(TokenType.MULTI_COMMENT_START, lexer.tokens[1].type)
    #     self.assertEqual(TokenType.MULTI_COMMENT_START, lexer.tokens[2].type)
    #     self.assertEqual(TokenType.EOF, lexer.tokens[3].type)
