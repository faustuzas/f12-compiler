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

    def test_multi_comment_start(self):
        lexer = Lexer('\n / \n + /* test \n + test - \n * test */ \n - \n')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_DIV, lexer.tokens[0].type)
        self.assertEqual(2, lexer.tokens[0].line_number)
        self.assertEqual(TokenType.OP_PLUS, lexer.tokens[1].type)
        self.assertEqual(3, lexer.tokens[1].line_number)
        self.assertEqual(TokenType.OP_MINUS, lexer.tokens[2].type)
        self.assertEqual(6, lexer.tokens[2].line_number)
        self.assertEqual(TokenType.EOF, lexer.tokens[3].type)

    def test_op_mul(self):
        lexer = Lexer('* /* + */ *')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_MUL, lexer.tokens[0].type)
        self.assertEqual(TokenType.OP_MUL, lexer.tokens[1].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[2].type)

    def test_op_pov(self):
        lexer = Lexer('^')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_POV, lexer.tokens[0].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[1].type)

    def test_op_mod(self):
        lexer = Lexer('%')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_MOD, lexer.tokens[0].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[1].type)

    def test_op_ne_and_op_not(self):
        lexer = Lexer('!=!!!=!')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_NE, lexer.tokens[0].type)
        self.assertEqual(TokenType.OP_NOT, lexer.tokens[1].type)
        self.assertEqual(TokenType.OP_NOT, lexer.tokens[2].type)
        self.assertEqual(TokenType.OP_NE, lexer.tokens[3].type)
        self.assertEqual(TokenType.OP_NOT, lexer.tokens[4].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[5].type)

    def test_op_eq_and_op_assign(self):
        lexer = Lexer('=====')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_EQ, lexer.tokens[0].type)
        self.assertEqual(TokenType.OP_EQ, lexer.tokens[1].type)
        self.assertEqual(TokenType.OP_ASSIGN, lexer.tokens[2].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[3].type)

    def test_op_eq_and_op_assign_2(self):
        lexer = Lexer('!= != == = ! != != => == =>')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_NE, lexer.tokens[0].type)
        self.assertEqual(TokenType.OP_NE, lexer.tokens[1].type)
        self.assertEqual(TokenType.OP_EQ, lexer.tokens[2].type)
        self.assertEqual(TokenType.OP_ASSIGN, lexer.tokens[3].type)
        self.assertEqual(TokenType.OP_NOT, lexer.tokens[4].type)
        self.assertEqual(TokenType.OP_NE, lexer.tokens[5].type)
        self.assertEqual(TokenType.OP_NE, lexer.tokens[6].type)
        self.assertEqual(TokenType.KW_FAT_ARROW, lexer.tokens[7].type)
        self.assertEqual(TokenType.OP_EQ, lexer.tokens[8].type)
        self.assertEqual(TokenType.KW_FAT_ARROW, lexer.tokens[9].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[10].type)

    def test_bunch_of_single_chars(self):
        lexer = Lexer(',:;({[]})')

        lexer.lex_all()

        self.assertEqual(TokenType.C_COMMA, lexer.tokens[0].type)
        self.assertEqual(TokenType.C_COLON, lexer.tokens[1].type)
        self.assertEqual(TokenType.C_SEMI, lexer.tokens[2].type)
        self.assertEqual(TokenType.C_ROUND_L, lexer.tokens[3].type)
        self.assertEqual(TokenType.C_CURLY_L, lexer.tokens[4].type)
        self.assertEqual(TokenType.C_SQUARE_L, lexer.tokens[5].type)
        self.assertEqual(TokenType.C_SQUARE_R, lexer.tokens[6].type)
        self.assertEqual(TokenType.C_CURLY_R, lexer.tokens[7].type)
        self.assertEqual(TokenType.C_ROUND_R, lexer.tokens[8].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[9].type)

    def test_op_and(self):
        lexer = Lexer('&&')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_AND, lexer.tokens[0].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[1].type)

    def test_op_and_error(self):
        lexer = Lexer('&')
        self.assertRaises(ValueError, lexer.lex_all)

    def test_op_or(self):
        lexer = Lexer('||')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_OR, lexer.tokens[0].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[1].type)

    def test_op_or_error(self):
        lexer = Lexer('|')
        self.assertRaises(ValueError, lexer.lex_all)

    def test_op_lt(self):
        lexer = Lexer('<')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_LT, lexer.tokens[0].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[1].type)

    def test_op_le(self):
        lexer = Lexer('<=')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_LE, lexer.tokens[0].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[1].type)

    def test_kw_from_stdin(self):
        lexer = Lexer('<-- <- <')

        lexer.lex_all()

        self.assertEqual(TokenType.KW_FROM_STDIN, lexer.tokens[0].type)
        self.assertEqual(TokenType.OP_LT, lexer.tokens[1].type)
        self.assertEqual(TokenType.OP_MINUS, lexer.tokens[2].type)
        self.assertEqual(TokenType.OP_LT, lexer.tokens[3].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[4].type)

    def test_op_access(self):
        lexer = Lexer('..')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_ACCESS, lexer.tokens[0].type)
        self.assertEqual(TokenType.OP_ACCESS, lexer.tokens[1].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[2].type)

    def test_lit_int(self):
        lexer = Lexer('1234567890')

        lexer.lex_all()

        self.assertEqual(TokenType.LIT_INT, lexer.tokens[0].type)
        self.assertEqual('1234567890', lexer.tokens[0].value)
        self.assertEqual(TokenType.EOF, lexer.tokens[1].type)

    def test_lit_int_2(self):
        lexer = Lexer('123 456 789 0')

        lexer.lex_all()

        self.assertEqual(TokenType.LIT_INT, lexer.tokens[0].type)
        self.assertEqual(TokenType.LIT_INT, lexer.tokens[1].type)
        self.assertEqual(TokenType.LIT_INT, lexer.tokens[2].type)
        self.assertEqual(TokenType.LIT_INT, lexer.tokens[3].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[4].type)

        self.assertEqual('123', lexer.tokens[0].value)
        self.assertEqual('456', lexer.tokens[1].value)
        self.assertEqual('789', lexer.tokens[2].value)
        self.assertEqual('0', lexer.tokens[3].value)

    def test_lit_int_no_leading_zero(self):
        lexer = Lexer('0123')
        self.assertRaises(ValueError, lexer.lex_all)

    def test_lit_float(self):
        lexer = Lexer('123 12. 12.45 78.80E5 789.4e7 852.78E+50 369.78e-789 .789 .789E-70')

        lexer.lex_all()

        self.assertEqual(TokenType.LIT_INT, lexer.tokens[0].type)
        self.assertEqual(TokenType.LIT_FLOAT, lexer.tokens[1].type)
        self.assertEqual(TokenType.LIT_FLOAT, lexer.tokens[2].type)
        self.assertEqual(TokenType.LIT_FLOAT, lexer.tokens[3].type)
        self.assertEqual(TokenType.LIT_FLOAT, lexer.tokens[4].type)
        self.assertEqual(TokenType.LIT_FLOAT, lexer.tokens[5].type)
        self.assertEqual(TokenType.LIT_FLOAT, lexer.tokens[6].type)
        self.assertEqual(TokenType.LIT_FLOAT, lexer.tokens[7].type)
        self.assertEqual(TokenType.LIT_FLOAT, lexer.tokens[8].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[9].type)

        self.assertEqual('123', lexer.tokens[0].value)
        self.assertEqual('12.', lexer.tokens[1].value)
        self.assertEqual('12.45', lexer.tokens[2].value)
        self.assertEqual('78.80E5', lexer.tokens[3].value)
        self.assertEqual('789.4e7', lexer.tokens[4].value)
        self.assertEqual('852.78E+50', lexer.tokens[5].value)
        self.assertEqual('369.78e-789', lexer.tokens[6].value)
        self.assertEqual('.789', lexer.tokens[7].value)
        self.assertEqual('.789E-70', lexer.tokens[8].value)

    def test_op_gt(self):
        lexer = Lexer('>>')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_GT, lexer.tokens[0].type)
        self.assertEqual(TokenType.OP_GT, lexer.tokens[1].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[2].type)

    def test_op_ge(self):
        lexer = Lexer('>==>>')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_GE, lexer.tokens[0].type)
        self.assertEqual(TokenType.KW_FAT_ARROW, lexer.tokens[1].type)
        self.assertEqual(TokenType.OP_GT, lexer.tokens[2].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[3].type)

    def test_lit_str(self):
        lexer = Lexer('"hello"')

        lexer.lex_all()

        self.assertEqual(TokenType.LIT_STR, lexer.tokens[0].type)
        self.assertEqual('hello', lexer.tokens[0].value)
        self.assertEqual(TokenType.EOF, lexer.tokens[1].type)

    def test_lit_str_multiline(self):
        lexer = Lexer('"hello\nmy\nname\nis"')

        lexer.lex_all()

        self.assertEqual(TokenType.LIT_STR, lexer.tokens[0].type)
        self.assertEqual('hello\nmy\nname\nis', lexer.tokens[0].value)
        self.assertEqual(4, lexer.line_number)
        self.assertEqual(TokenType.EOF, lexer.tokens[1].type)

    def test_lit_str_escape(self):
        lexer = Lexer('"hello \\n \\t \\\" ha"')

        lexer.lex_all()

        self.assertEqual(TokenType.LIT_STR, lexer.tokens[0].type)
        self.assertEqual('hello \n \t \" ha', lexer.tokens[0].value)
        self.assertEqual(TokenType.EOF, lexer.tokens[1].type)

    def test_identifier(self):
        lexer = Lexer('_function_name')

        lexer.lex_all()

        self.assertEqual(TokenType.IDENTIFIER, lexer.tokens[0].type)
        self.assertEqual('_function_name', lexer.tokens[0].value)
        self.assertEqual(TokenType.EOF, lexer.tokens[1].type)

    def test_identifier_2(self):
        lexer = Lexer('int hello null true while')

        lexer.lex_all()

        self.assertEqual(TokenType.PRIMITIVE_INT, lexer.tokens[0].type)
        self.assertEqual(TokenType.IDENTIFIER, lexer.tokens[1].type)
        self.assertEqual(TokenType.CONSTANT_NULL, lexer.tokens[2].type)
        self.assertEqual(TokenType.CONSTANT_TRUE, lexer.tokens[3].type)
        self.assertEqual(TokenType.KW_WHILE, lexer.tokens[4].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[5].type)

        self.assertEqual('hello', lexer.tokens[1].value)

    def test_helper(self):
        lexer = Lexer('>include')

        lexer.lex_all()

        self.assertEqual(TokenType.HELPER_INCLUDE, lexer.tokens[0].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[1].type)

    def test_helper_2(self):
        lexer = Lexer('>includ 5>0 >123include')

        lexer.lex_all()

        self.assertEqual(TokenType.OP_GT, lexer.tokens[0].type)
        self.assertEqual(TokenType.IDENTIFIER, lexer.tokens[1].type)
        self.assertEqual(TokenType.LIT_INT, lexer.tokens[2].type)
        self.assertEqual(TokenType.OP_GT, lexer.tokens[3].type)
        self.assertEqual(TokenType.LIT_INT, lexer.tokens[4].type)
        self.assertEqual(TokenType.OP_GT, lexer.tokens[5].type)
        self.assertEqual(TokenType.LIT_INT, lexer.tokens[6].type)
        self.assertEqual(TokenType.IDENTIFIER, lexer.tokens[7].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[8].type)

        self.assertEqual('includ', lexer.tokens[1].value)
        self.assertEqual('5', lexer.tokens[2].value)
        self.assertEqual('0', lexer.tokens[4].value)
        self.assertEqual('123', lexer.tokens[6].value)
        self.assertEqual('include', lexer.tokens[7].value)

    def test_i_array_access(self):
        lexer = Lexer('x[0]')

        lexer.lex_all()

        self.assertEqual(TokenType.IDENTIFIER, lexer.tokens[0].type)
        self.assertEqual(TokenType.C_SQUARE_L, lexer.tokens[1].type)
        self.assertEqual(TokenType.LIT_INT, lexer.tokens[2].type)
        self.assertEqual(TokenType.C_SQUARE_R, lexer.tokens[3].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[4].type)

    def test_i_fun_declaration(self):
        lexer = Lexer('fun add(int x[], int y) => int {\nret x[0] + y;\n}')

        lexer.lex_all()

        self.assertEqual(TokenType.KW_FUN, lexer.tokens[0].type)
        self.assertEqual(TokenType.IDENTIFIER, lexer.tokens[1].type)
        self.assertEqual(TokenType.C_ROUND_L, lexer.tokens[2].type)
        self.assertEqual(TokenType.PRIMITIVE_INT, lexer.tokens[3].type)
        self.assertEqual(TokenType.IDENTIFIER, lexer.tokens[4].type)
        self.assertEqual(TokenType.C_SQUARE_L, lexer.tokens[5].type)
        self.assertEqual(TokenType.C_SQUARE_R, lexer.tokens[6].type)
        self.assertEqual(TokenType.C_COMMA, lexer.tokens[7].type)
        self.assertEqual(TokenType.PRIMITIVE_INT, lexer.tokens[8].type)
        self.assertEqual(TokenType.IDENTIFIER, lexer.tokens[9].type)
        self.assertEqual(TokenType.C_ROUND_R, lexer.tokens[10].type)
        self.assertEqual(TokenType.KW_FAT_ARROW, lexer.tokens[11].type)
        self.assertEqual(TokenType.PRIMITIVE_INT, lexer.tokens[12].type)
        self.assertEqual(TokenType.C_CURLY_L, lexer.tokens[13].type)
        self.assertEqual(TokenType.KW_RETURN, lexer.tokens[14].type)
        self.assertEqual(TokenType.IDENTIFIER, lexer.tokens[15].type)
        self.assertEqual(TokenType.C_SQUARE_L, lexer.tokens[16].type)
        self.assertEqual(TokenType.LIT_INT, lexer.tokens[17].type)
        self.assertEqual(TokenType.C_SQUARE_R, lexer.tokens[18].type)
        self.assertEqual(TokenType.OP_PLUS, lexer.tokens[19].type)
        self.assertEqual(TokenType.IDENTIFIER, lexer.tokens[20].type)
        self.assertEqual(TokenType.C_SEMI, lexer.tokens[21].type)
        self.assertEqual(TokenType.C_CURLY_R, lexer.tokens[22].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[23].type)

    def test_i_addition(self):
        lexer = Lexer('5 + 5')

        lexer.lex_all()

        self.assertEqual(TokenType.LIT_INT, lexer.tokens[0].type)
        self.assertEqual(TokenType.OP_PLUS, lexer.tokens[1].type)
        self.assertEqual(TokenType.LIT_INT, lexer.tokens[2].type)
        self.assertEqual(TokenType.EOF, lexer.tokens[3].type)
