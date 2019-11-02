from unittest import TestCase

from models import LexingState, TokenType
from lexer.lexer import Lexer


class LexerGeneralTests(TestCase):

    def test_add_token_no_rollback(self):
        lexer = Lexer('123')
        lexer.token_buffer = '12345'
        lexer.state = LexingState.LIT_STR
        lexer.offset = 4

        lexer.add_token(TokenType.OP_PLUS)

        self.assertEqual(1, len(lexer.tokens))
        self.assertEqual('', lexer.token_buffer)
        self.assertEqual(LexingState.START, lexer.state)
        self.assertEqual(4, lexer.offset)

    def test_add_token_rollback(self):
        lexer = Lexer('123')
        lexer.offset = 4

        lexer.add_token(TokenType.OP_PLUS, rollback=True)

        self.assertEqual(lexer.offset, 3)

    def test_add_token_keep_state(self):
        lexer = Lexer('123')

        lexer.add_token(TokenType.OP_PLUS, keep_state=True)

        self.assertEqual(LexingState.START, lexer.state)

    def test_add_token_without_value(self):
        lexer = Lexer('123')
        lexer.token_buffer = '12345'

        lexer.add_token(TokenType.IDENTIFIER, with_value=False)

        self.assertEqual(TokenType.IDENTIFIER, lexer.tokens[0].type)
        self.assertEqual('', lexer.tokens[0].value)
        self.assertEqual('', lexer.token_buffer)

    def test_begin_tokenizing_new_state(self):
        lexer = Lexer('123')
        lexer.current_char = '1'

        lexer.begin_tokenizing(LexingState.LIT_STR)

        self.assertEqual(LexingState.LIT_STR, lexer.state)
        self.assertEqual('', lexer.token_buffer)

    def test_begin_tokenizing_new_state_to_buffer(self):
        lexer = Lexer('123')
        lexer.current_char = '1'

        lexer.begin_tokenizing(LexingState.LIT_STR, to_buffer=True)

        self.assertEqual(LexingState.LIT_STR, lexer.state)
        self.assertEqual('1', lexer.token_buffer)

    def test_to_state(self):
        lexer = Lexer('123')

        lexer.to_state(LexingState.OP_MINUS)

        self.assertEqual(LexingState.OP_MINUS, lexer.state)

    def test_file_name_is_set(self):
        lexer = Lexer('2 + 2', 'main.f12')

        lexer.lex_all()

        for t in lexer.tokens:
            self.assertEqual('main.f12', t.file_name)
