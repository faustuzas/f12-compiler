from unittest import TestCase

from lexer.lexer import Lexer


class LexerTests(TestCase):

    def test_proceed_new_line(self):
        lexer = Lexer("12\n3")
        lexer.proceed()
        lexer.proceed()
        lexer.proceed()
        self.assertEqual(0, lexer.offset)
        self.assertEqual(2, lexer.line_number)

    def test_proceed_new_line_in_string(self):
        lexer = Lexer("12\n3")
        lexer.proceed(string=True)
        lexer.proceed(string=True)
        lexer.proceed(string=True)
        self.assertEqual(3, lexer.offset)
        self.assertEqual(1, lexer.line_number)

    def test_proceed_keep_token_buffer(self):
        lexer = Lexer("12\n3")
        lexer.token_buffer = '123'
        lexer.proceed()
        self.assertEqual('123', lexer.token_buffer)

    def test_proceed_clear_token_buffer(self):
        lexer = Lexer("12\n3")
        lexer.token_buffer = '123'
        lexer.proceed(clear_buffer=True)
        self.assertEqual('', lexer.token_buffer)
