from unittest import TestCase

from lexer import Lexer


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
        lexer.proceed(True)
        lexer.proceed(True)
        lexer.proceed(True)
        self.assertEqual(3, lexer.offset)
        self.assertEqual(1, lexer.line_number)

    def test_check_future(self):
        lexer = Lexer("12345678")
        self.assertTrue(lexer.check_future("123"))
        self.assertTrue(not lexer.check_future("23"))