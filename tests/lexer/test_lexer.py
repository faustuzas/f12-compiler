from unittest import TestCase

from models import LexingState, Token, TokenType
from lexer.lexer import Lexer


class LexerTests(TestCase):

    def test_add_token_no_rollback(self):
        lexer = Lexer('123')
        lexer.token_buffer = '12345'
        lexer.state = LexingState.LIT_STR
        lexer.offset = 4

        lexer.add_token(Token(TokenType.OP_PLUS, 4))

        self.assertEqual(1, len(lexer.tokens))
        self.assertEqual('', lexer.token_buffer)
        self.assertEqual(LexingState.START, lexer.state)
        self.assertEqual(lexer.offset, 4)

    def test_add_token_rollback(self):
        lexer = Lexer('123')
        lexer.offset = 4

        lexer.add_token(Token(TokenType.OP_PLUS, 4), rollback=True)

        self.assertEqual(lexer.offset, 3)
