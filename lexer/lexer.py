from typing import List
from models import LexingState, Token, TokenType, TokenError
from models.builtins import keywords, primitive_types, constants, helpers
from utils import Switcher, throw, ranges, printer


class Lexer:
    state: LexingState
    token_buffer: str
    line_number: int
    offset: int
    offset_in_line: int
    tokens: List[Token]
    token_start_line_number: int
    current_char: str

    def __init__(self, text: str) -> None:
        assert len(text)

        self.state = LexingState.START
        self.token_buffer = ''
        self.line_number = 1
        self.offset = 0
        self.offset_in_line = 0
        self.tokens: List[Token] = []
        self.token_start_line_number = 0
        self.text = text
        self.current_char = ''

    def lex_all(self):
        try:
            while self.offset < len(self.text):
                self.current_char = self.text[self.offset]
                self.lex()
                self.offset += 1
                self.offset_in_line += 1

            self.current_char = ' '
            self.lex()

            Switcher.from_dict({
                (LexingState.START, LexingState.SL_COMMENT): lambda: self.add_token(TokenType.EOF),
                LexingState.LIT_STR: lambda: throw(TokenError('Unterminated string'))
            }).exec(self.state)
        except TokenError as e:
            self.print_error(str(e))
            raise ValueError()

        return self.tokens

    def lex(self):
        Switcher.from_dict({
            LexingState.START: self.lex_start,
            LexingState.OP_MINUS: self.lex_op_minus,
            LexingState.OP_MINUS_2: self.lex_op_minus_2,
            LexingState.OP_DIV: self.lex_op_div,
            LexingState.SL_COMMENT: self.lex_sl_comment,
            LexingState.ML_COMMENT: self.lex_ml_comment,
            LexingState.ML_COMMENT_END: self.lex_ml_comment_end,
            LexingState.OP_NOT: self.lex_op_not,
            LexingState.OP_ASSIGN: self.lex_op_assign,
            LexingState.OP_AND: self.lex_op_and,
            LexingState.OP_OR: self.lex_op_or,
            LexingState.OP_LT: self.lex_op_lt,
            LexingState.KW_FROM_STDIN: self.lex_kw_from_stdin,
            LexingState.OP_ACCESS: self.lex_op_access,
            LexingState.LIT_INT_FIRST_ZERO: self.lex_lit_int_first_zero,
            LexingState.LIT_INT: self.lex_lit_int,
            LexingState.LIT_FLOAT_START: self.lex_lit_float_start,
            LexingState.LIT_FLOAT: self.lex_lit_float,
            LexingState.LIT_FLOAT_EXP: self.lex_lit_float_exp,
            LexingState.LIT_FLOAT_PRE_END: self.lex_lit_float_pre_end,
            LexingState.LIT_FLOAT_END: self.lex_lit_float_end,
            LexingState.OP_GT: self.lex_op_gt,
            LexingState.AFTER_GT: self.lex_after_gt,
            LexingState.LIT_STR: self.lex_lit_str,
            LexingState.LIT_STR_ESCAPE: self.lex_lit_str_escape,
            LexingState.IDENTIFIER: self.lex_identifier
        }).exec(self.state)

    def lex_start(self):
        Switcher.from_dict({
            '+': lambda: self.add_token(TokenType.OP_PLUS),
            '*': lambda: self.add_token(TokenType.OP_MUL),
            '^': lambda: self.add_token(TokenType.OP_POV),
            '%': lambda: self.add_token(TokenType.OP_MOD),
            ';': lambda: self.add_token(TokenType.C_SEMI),
            ':': lambda: self.add_token(TokenType.C_COLON),
            ',': lambda: self.add_token(TokenType.C_COMMA),
            '(': lambda: self.add_token(TokenType.C_ROUND_L),
            ')': lambda: self.add_token(TokenType.C_ROUND_R),
            '{': lambda: self.add_token(TokenType.C_CURLY_L),
            '}': lambda: self.add_token(TokenType.C_CURLY_R),
            '[': lambda: self.add_token(TokenType.C_SQUARE_L),
            ']': lambda: self.add_token(TokenType.C_SQUARE_R),
            '-': lambda: self.begin_tokenizing(LexingState.OP_MINUS),
            '/': lambda: self.begin_tokenizing(LexingState.OP_DIV),
            '!': lambda: self.begin_tokenizing(LexingState.OP_NOT),
            '=': lambda: self.begin_tokenizing(LexingState.OP_ASSIGN),
            '&': lambda: self.begin_tokenizing(LexingState.OP_AND),
            '|': lambda: self.begin_tokenizing(LexingState.OP_OR),
            '<': lambda: self.begin_tokenizing(LexingState.OP_LT),
            '.': lambda: self.begin_tokenizing(LexingState.OP_ACCESS),
            '>': lambda: self.begin_tokenizing(LexingState.OP_GT),
            '"': lambda: self.begin_tokenizing(LexingState.LIT_STR),
            '0': lambda: self.begin_tokenizing(LexingState.LIT_INT_FIRST_ZERO, to_buffer=True),
            ranges.digits: lambda: self.begin_tokenizing(LexingState.LIT_INT, to_buffer=True),
            '_': lambda: self.begin_tokenizing(LexingState.IDENTIFIER, to_buffer=True),
            ranges.letters: lambda: self.begin_tokenizing(LexingState.IDENTIFIER, to_buffer=True),
            '\n': self.inc_new_line,
            ' ': lambda: ()  # ignore
        }).default(lambda: throw(TokenError('Unrecognised token'))).exec(self.current_char)

    def lex_op_minus(self):
        Switcher.from_dict({
            '-': lambda: self.to_state(LexingState.OP_MINUS_2)
        }).default(lambda: self.add_token(TokenType.OP_MINUS, rollback=True)).exec(self.current_char)

    def lex_op_minus_2(self):
        Switcher.from_dict({
            '>': lambda: self.add_token(TokenType.KW_TO_STDOUT),
            '-': lambda: self.add_token(TokenType.OP_MINUS, keep_state=True)
        }).default(lambda: (self.add_token(TokenType.OP_MINUS),
                            self.add_token(TokenType.OP_MINUS))).exec(self.current_char)

    def lex_op_div(self):
        Switcher.from_dict({
            '/': lambda: self.to_state(LexingState.SL_COMMENT),
            '*': lambda: self.to_state(LexingState.ML_COMMENT)
        }).default(lambda: self.add_token(TokenType.OP_DIV, rollback=True)).exec(self.current_char)

    def lex_sl_comment(self):
        Switcher.from_dict({
            '\n': lambda: (self.to_state(LexingState.START), self.inc_new_line())
        }).exec(self.current_char)

    def lex_ml_comment(self):
        Switcher.from_dict({
            '\n': self.inc_new_line,
            '*': lambda: self.to_state(LexingState.ML_COMMENT_END)
        }).exec(self.current_char)

    def lex_ml_comment_end(self):
        Switcher.from_dict({
            '/': lambda: self.to_state(LexingState.START)
        }).default(lambda: self.to_state(LexingState.ML_COMMENT)).exec(self.current_char)

    def lex_op_not(self):
        Switcher.from_dict({
            '=': lambda: self.add_token(TokenType.OP_NE)
        }).default(lambda: self.add_token(TokenType.OP_NOT, rollback=True)).exec(self.current_char)

    def lex_op_assign(self):
        Switcher.from_dict({
            '=': lambda: self.add_token(TokenType.OP_EQ),
            '>': lambda: self.add_token(TokenType.KW_FAT_ARROW)
        }).default(lambda: self.add_token(TokenType.OP_ASSIGN, rollback=True)).exec(self.current_char)

    def lex_op_and(self):
        Switcher.from_dict({
            '&': lambda: self.add_token(TokenType.OP_AND)
        }).default(lambda: throw(TokenError('Missing &'))).exec(self.current_char)

    def lex_op_or(self):
        Switcher.from_dict({
            '|': lambda: self.add_token(TokenType.OP_OR)
        }).default(lambda: throw(TokenError('Missing |'))).exec(self.current_char)

    def lex_op_lt(self):
        Switcher.from_dict({
            '=': lambda: self.add_token(TokenType.OP_LE),
            '-': lambda: self.to_state(LexingState.KW_FROM_STDIN)
        }).default(lambda: self.add_token(TokenType.OP_LT, rollback=True)).exec(self.current_char)

    def lex_kw_from_stdin(self):
        Switcher.from_dict({
            '-': lambda: self.add_token(TokenType.KW_FROM_STDIN)
        }).default(lambda: (self.add_token(TokenType.OP_LT),
                            self.add_token(TokenType.OP_MINUS, rollback=True))).exec(self.current_char)

    def lex_op_access(self):
        Switcher.from_dict({
            ranges.digits: lambda: (self.add_to_buff('.'), self.add_to_buff(), self.to_state(LexingState.LIT_FLOAT))
        }).default(lambda: self.add_token(TokenType.OP_ACCESS, rollback=True)).exec(self.current_char)

    def lex_lit_int_first_zero(self):
        Switcher.from_dict({
            '.': lambda: (self.add_to_buff(), self.to_state(LexingState.LIT_FLOAT_START)),
            ranges.digits: lambda: throw(TokenError('Multi digit integer cannot start with 0'))
        }).default(lambda: self.add_token(TokenType.LIT_INT, rollback=True)).exec(self.current_char)

    def lex_lit_int(self):
        Switcher.from_dict({
            ranges.digits: self.add_to_buff,
            '.': lambda: (self.add_to_buff(), self.to_state(LexingState.LIT_FLOAT_START))
        }).default(lambda: self.add_token(TokenType.LIT_INT, rollback=True)).exec(self.current_char)

    def lex_lit_float_start(self):
        Switcher.from_dict({
            ranges.digits: lambda: (self.add_to_buff(), self.to_state(LexingState.LIT_FLOAT)),
        }).default(lambda: self.add_token(TokenType.LIT_FLOAT, rollback=True)).exec(self.current_char)

    def lex_lit_float(self):
        Switcher.from_dict({
            ranges.digits: self.add_to_buff,
            ('e', 'E'): lambda: (self.add_to_buff(), self.to_state(LexingState.LIT_FLOAT_EXP))
        }).default(lambda: self.add_token(TokenType.LIT_FLOAT, rollback=True)).exec(self.current_char)

    def lex_lit_float_exp(self):
        Switcher.from_dict({
            ('+', '-'): lambda: (self.add_to_buff(), self.to_state(LexingState.LIT_FLOAT_PRE_END)),
            ranges.digits: lambda: (self.add_to_buff(), self.to_state(LexingState.LIT_FLOAT_END))
        }).default(lambda: throw(TokenError('After exponent has to follow number or sign'))).exec(self.current_char)

    def lex_lit_float_pre_end(self):
        Switcher.from_dict({
            ranges.digits: lambda: (self.add_to_buff(), self.to_state(LexingState.LIT_FLOAT_END))
        }).default(lambda: throw(TokenError('Exponent power is missing'))).exec(self.current_char)

    def lex_lit_float_end(self):
        Switcher.from_dict({
            ranges.digits: self.add_to_buff
        }).default(lambda: self.add_token(TokenType.LIT_FLOAT, rollback=True)).exec(self.current_char)

    def lex_op_gt(self):
        Switcher.from_dict({
            '=': lambda: self.add_token(TokenType.OP_GE),
            ranges.letters: lambda: (self.add_to_buff(), self.to_state(LexingState.AFTER_GT))
        }).default(lambda: self.add_token(TokenType.OP_GT, rollback=True)).exec(self.current_char)

    def lex_after_gt(self):
        Switcher.from_dict({
            ranges.letters: self.add_to_buff
        }).default(self.complete_helper).exec(self.current_char)

    def lex_lit_str(self):
        Switcher.from_dict({
            '"': lambda: self.add_token(TokenType.LIT_STR),
            '\\': lambda: self.to_state(LexingState.LIT_STR_ESCAPE),
            '\n': lambda: (self.add_to_buff(), self.inc_new_line())
        }).default(self.add_to_buff).exec(self.current_char)

    def lex_lit_str_escape(self):
        Switcher.from_dict({
            '"': lambda: self.add_to_buff('\"'),
            't': lambda: self.add_to_buff('\t'),
            'n': lambda: self.add_to_buff('\n')
        }).default(lambda: throw(TokenError('Unrecognized escaped character'))).exec(self.current_char)

        self.to_state(LexingState.LIT_STR)

    def lex_identifier(self):
        Switcher.from_dict({
            ranges.letters: self.add_to_buff,
            ranges.digits: self.add_to_buff,
            '_': self.add_to_buff,
        }).default(self.complete_identifier).exec(self.current_char)

    """
    Helper methods
    """
    def complete_identifier(self):
        kw = keywords.get(self.token_buffer, None)
        if kw:
            self.add_token(kw, with_value=False, line_number=self.line_number, rollback=True)
            return
        primitive_type = primitive_types.get(self.token_buffer, None)
        if primitive_type:
            self.add_token(primitive_type, with_value=False, line_number=self.line_number, rollback=True)
            return
        constant = constants.get(self.token_buffer, None)
        if constant:
            self.add_token(constant, with_value=False, line_number=self.line_number, rollback=True)
            return

        self.add_token(TokenType.IDENTIFIER, line_number=self.line_number, rollback=True)

    def complete_helper(self):
        helper = helpers.get(self.token_buffer, None)
        if helper:
            self.add_token(helper, with_value=False)
        else:
            self.add_token(TokenType.OP_GT, with_value=False, keep_buffer=True)
            self.complete_identifier()

    def begin_tokenizing(self, new_state: LexingState, to_buffer=False):
        self.token_start_line_number = self.line_number
        self.to_state(new_state)

        if to_buffer:
            self.add_to_buff()

    def add_token(self, token_type: TokenType, line_number=None, rollback=False,
                  keep_state=False, with_value=True, keep_buffer=False):
        self.tokens.append(Token(token_type, line_number if line_number else self.line_number,
                                 self.token_buffer if with_value else ''))
        if not keep_buffer:
            self.token_buffer = ''
        if not keep_state:
            self.state = LexingState.START
        if rollback:
            self.offset -= 1
            self.offset_in_line -= 1

    def add_to_buff(self, symbol=None):
        if symbol is None:
            self.token_buffer += self.current_char
        else:
            self.token_buffer += symbol

    def to_state(self, state: LexingState):
        assert state is not None
        self.state = state

    def inc_new_line(self):
        self.line_number += 1
        self.offset_in_line = 0

    def print_tokens(self):
        template = '{:>5} | {:>5} | {:>17} | {:>17}'
        header = template.format('ID', 'LINE', 'TYPE', 'VALUE')
        body = ''
        for (i, token) in enumerate(self.tokens):
            body += template.format(i + 1, token.line_number, token.type, token.value) + '\n'

        printer.success(body, header)

    def print_error(self, cause):
        all_lines = self.text.split('\n')
        lines_to_show = []
        line_in_array = self.line_number - 1
        if self.line_number - 1 >= 1 and len(all_lines[line_in_array - 1].strip()) > 0:
            lines_to_show.append(f'{self.line_number_prefix(self.line_number - 1)}{all_lines[line_in_array - 1]}')

        lines_to_show.append(f'{self.line_number_prefix(self.line_number)}{all_lines[line_in_array]}')
        lines_to_show.append(' ' * (self.offset_in_line + len(self.line_number_prefix(self.line_number)) - 1) + '^')

        if self.line_number + 1 <= len(all_lines) and len(all_lines[line_in_array + 1].strip()) > 0:
            lines_to_show.append(f'{self.line_number_prefix(self.line_number + 1)}{all_lines[line_in_array + 1]}')

        printer.error('\n'.join(lines_to_show), f'Lexing error: {cause}')

    @staticmethod
    def line_number_prefix(number):
        return f'{number}. '

