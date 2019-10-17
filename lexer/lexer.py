from typing import List
from models import LexingState, Token, TokenType, TokenError
from models.builtins import keywords, primitive_types, constants, helpers
from utils import FasterSwitcher as Switcher, throw, ranges, printer


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
                (LexingState.START, LexingState.SL_COMMENT): lambda ctx: ctx.add_token(TokenType.EOF),
                (LexingState.ML_COMMENT, LexingState.ML_COMMENT_END): lambda ctx: throw(TokenError('Unterminanted '
                                                                                                   'multiline '
                                                                                                   'comment')),
                LexingState.LIT_STR: lambda ctx: throw(TokenError('Unterminated string'))
            }).exec(self, self.state)
        except TokenError as e:
            self.print_error(str(e))
            raise ValueError()

        return self.tokens

    def lex(self):
        Switcher.from_dict({
            LexingState.START: lambda ctx: ctx.lex_start(),
            LexingState.OP_MINUS: lambda ctx: ctx.lex_op_minus(),
            LexingState.OP_MINUS_2: lambda ctx: ctx.lex_op_minus_2(),
            LexingState.OP_DIV: lambda ctx: ctx.lex_op_div(),
            LexingState.SL_COMMENT: lambda ctx: ctx.lex_sl_comment(),
            LexingState.ML_COMMENT: lambda ctx: ctx.lex_ml_comment(),
            LexingState.ML_COMMENT_END: lambda ctx: ctx.lex_ml_comment_end(),
            LexingState.OP_NOT: lambda ctx: ctx.lex_op_not(),
            LexingState.OP_ASSIGN: lambda ctx: ctx.lex_op_assign(),
            LexingState.OP_AND: lambda ctx: ctx.lex_op_and(),
            LexingState.OP_OR: lambda ctx: ctx.lex_op_or(),
            LexingState.OP_LT: lambda ctx: ctx.lex_op_lt(),
            LexingState.KW_FROM_STDIN: lambda ctx: ctx.lex_kw_from_stdin(),
            LexingState.OP_ACCESS: lambda ctx: ctx.lex_op_access(),
            LexingState.LIT_INT_FIRST_ZERO: lambda ctx: ctx.lex_lit_int_first_zero(),
            LexingState.LIT_INT: lambda ctx: ctx.lex_lit_int(),
            LexingState.LIT_FLOAT_START: lambda ctx: ctx.lex_lit_float_start(),
            LexingState.LIT_FLOAT: lambda ctx: ctx.lex_lit_float(),
            LexingState.LIT_FLOAT_EXP: lambda ctx: ctx.lex_lit_float_exp(),
            LexingState.LIT_FLOAT_PRE_END: lambda ctx: ctx.lex_lit_float_pre_end(),
            LexingState.LIT_FLOAT_END: lambda ctx: ctx.lex_lit_float_end(),
            LexingState.OP_GT: lambda ctx: ctx.lex_op_gt(),
            LexingState.AFTER_GT: lambda ctx: ctx.lex_after_gt(),
            LexingState.LIT_STR: lambda ctx: ctx.lex_lit_str(),
            LexingState.LIT_STR_ESCAPE: lambda ctx: ctx.lex_lit_str_escape(),
            LexingState.IDENTIFIER: lambda ctx: ctx.lex_identifier()
        }).exec(self, self.state)

    def lex_start(self):
        Switcher.from_dict({
            '+': lambda ctx: ctx.add_token(TokenType.OP_PLUS),
            '*': lambda ctx: ctx.add_token(TokenType.OP_MUL),
            '^': lambda ctx: ctx.add_token(TokenType.OP_POV),
            '%': lambda ctx: ctx.add_token(TokenType.OP_MOD),
            ';': lambda ctx: ctx.add_token(TokenType.C_SEMI),
            ':': lambda ctx: ctx.add_token(TokenType.C_COLON),
            ',': lambda ctx: ctx.add_token(TokenType.C_COMMA),
            '(': lambda ctx: ctx.add_token(TokenType.C_ROUND_L),
            ')': lambda ctx: ctx.add_token(TokenType.C_ROUND_R),
            '{': lambda ctx: ctx.add_token(TokenType.C_CURLY_L),
            '}': lambda ctx: ctx.add_token(TokenType.C_CURLY_R),
            '[': lambda ctx: ctx.add_token(TokenType.C_SQUARE_L),
            ']': lambda ctx: ctx.add_token(TokenType.C_SQUARE_R),
            '-': lambda ctx: ctx.begin_tokenizing(LexingState.OP_MINUS),
            '/': lambda ctx: ctx.begin_tokenizing(LexingState.OP_DIV),
            '!': lambda ctx: ctx.begin_tokenizing(LexingState.OP_NOT),
            '=': lambda ctx: ctx.begin_tokenizing(LexingState.OP_ASSIGN),
            '&': lambda ctx: ctx.begin_tokenizing(LexingState.OP_AND),
            '|': lambda ctx: ctx.begin_tokenizing(LexingState.OP_OR),
            '<': lambda ctx: ctx.begin_tokenizing(LexingState.OP_LT),
            '.': lambda ctx: ctx.begin_tokenizing(LexingState.OP_ACCESS),
            '>': lambda ctx: ctx.begin_tokenizing(LexingState.OP_GT),
            '"': lambda ctx: ctx.begin_tokenizing(LexingState.LIT_STR),
            '0': lambda ctx: ctx.begin_tokenizing(LexingState.LIT_INT_FIRST_ZERO, to_buffer=True),
            ranges.digits_without_zero: lambda ctx: ctx.begin_tokenizing(LexingState.LIT_INT, to_buffer=True),
            '_': lambda ctx: ctx.begin_tokenizing(LexingState.IDENTIFIER, to_buffer=True),
            ranges.letters: lambda ctx: ctx.begin_tokenizing(LexingState.IDENTIFIER, to_buffer=True),
            '\n': lambda ctx: ctx.inc_new_line(),
            ' ': lambda ctx: ()  # ignore
        }).default(lambda ctx: throw(TokenError('Unrecognised token'))).exec(self, self.current_char)

    def lex_op_minus(self):
        Switcher.from_dict({
            '-': lambda ctx: ctx.to_state(LexingState.OP_MINUS_2)
        }).default(lambda ctx: ctx.add_token(TokenType.OP_MINUS, rollback=True)).exec(self, self.current_char)

    def lex_op_minus_2(self):
        Switcher.from_dict({
            '>': lambda ctx: ctx.add_token(TokenType.KW_TO_STDOUT),
            '-': lambda ctx: ctx.add_token(TokenType.OP_MINUS, keep_state=True)
        }).default(lambda ctx: (ctx.add_token(TokenType.OP_MINUS),
                                ctx.add_token(TokenType.OP_MINUS))).exec(self, self.current_char)

    def lex_op_div(self):
        Switcher.from_dict({
            '/': lambda ctx: ctx.to_state(LexingState.SL_COMMENT),
            '*': lambda ctx: ctx.to_state(LexingState.ML_COMMENT)
        }).default(lambda ctx: ctx.add_token(TokenType.OP_DIV, rollback=True)).exec(self, self.current_char)

    def lex_sl_comment(self):
        Switcher.from_dict({
            '\n': lambda ctx: (ctx.to_state(LexingState.START), ctx.inc_new_line())
        }).exec(self, self.current_char)

    def lex_ml_comment(self):
        Switcher.from_dict({
            '\n': lambda ctx: ctx.inc_new_line(),
            '*': lambda ctx: ctx.to_state(LexingState.ML_COMMENT_END)
        }).exec(self, self.current_char)

    def lex_ml_comment_end(self):
        Switcher.from_dict({
            '/': lambda ctx: ctx.to_state(LexingState.START)
        }).default(lambda ctx: ctx.to_state(LexingState.ML_COMMENT)).exec(self, self.current_char)

    def lex_op_not(self):
        Switcher.from_dict({
            '=': lambda ctx: ctx.add_token(TokenType.OP_NE)
        }).default(lambda ctx: ctx.add_token(TokenType.OP_NOT, rollback=True)).exec(self, self.current_char)

    def lex_op_assign(self):
        Switcher.from_dict({
            '=': lambda ctx: ctx.add_token(TokenType.OP_EQ),
            '>': lambda ctx: ctx.add_token(TokenType.KW_FAT_ARROW)
        }).default(lambda ctx: ctx.add_token(TokenType.OP_ASSIGN, rollback=True)).exec(self, self.current_char)

    def lex_op_and(self):
        Switcher.from_dict({
            '&': lambda ctx: ctx.add_token(TokenType.OP_AND)
        }).default(lambda ctx: throw(TokenError('Missing &'))).exec(self, self.current_char)

    def lex_op_or(self):
        Switcher.from_dict({
            '|': lambda ctx: ctx.add_token(TokenType.OP_OR)
        }).default(lambda ctx: throw(TokenError('Missing |'))).exec(self, self.current_char)

    def lex_op_lt(self):
        Switcher.from_dict({
            '=': lambda ctx: ctx.add_token(TokenType.OP_LE),
            '-': lambda ctx: ctx.to_state(LexingState.KW_FROM_STDIN)
        }).default(lambda ctx: ctx.add_token(TokenType.OP_LT, rollback=True)).exec(self, self.current_char)

    def lex_kw_from_stdin(self):
        Switcher.from_dict({
            '-': lambda ctx: ctx.add_token(TokenType.KW_FROM_STDIN)
        }).default(lambda ctx: (ctx.add_token(TokenType.OP_LT),
                                ctx.add_token(TokenType.OP_MINUS, rollback=True))).exec(self, self.current_char)

    def lex_op_access(self):
        Switcher.from_dict({
            ranges.digits: lambda ctx: (ctx.add_to_buff('.'), ctx.add_to_buff(), ctx.to_state(LexingState.LIT_FLOAT))
        }).default(lambda ctx: ctx.add_token(TokenType.OP_ACCESS, rollback=True)).exec(self, self.current_char)

    def lex_lit_int_first_zero(self):
        Switcher.from_dict({
            '.': lambda ctx: (ctx.add_to_buff(), ctx.to_state(LexingState.LIT_FLOAT_START)),
            ranges.digits: lambda ctx: throw(TokenError('Multi digit integer cannot start with 0'))
        }).default(lambda ctx: ctx.add_token(TokenType.LIT_INT, rollback=True)).exec(self, self.current_char)

    def lex_lit_int(self):
        Switcher.from_dict({
            ranges.digits: lambda ctx: ctx.add_to_buff(),
            '.': lambda ctx: (ctx.add_to_buff(), ctx.to_state(LexingState.LIT_FLOAT_START)),
            '_': lambda ctx: throw(TokenError('Integer with invalid prefix')),
            ranges.letters: lambda ctx: throw(TokenError('Integer with invalid prefix'))
        }).default(lambda ctx: ctx.add_token(TokenType.LIT_INT, rollback=True)).exec(self, self.current_char)

    def lex_lit_float_start(self):
        Switcher.from_dict({
            ranges.digits: lambda ctx: (ctx.add_to_buff(), ctx.to_state(LexingState.LIT_FLOAT)),
        }).default(lambda ctx: ctx.add_token(TokenType.LIT_FLOAT, rollback=True)).exec(self, self.current_char)

    def lex_lit_float(self):
        Switcher.from_dict({
            ranges.digits: lambda ctx: ctx.add_to_buff(),
            ('e', 'E'): lambda ctx: (ctx.add_to_buff(), ctx.to_state(LexingState.LIT_FLOAT_EXP))
        }).default(lambda ctx: ctx.add_token(TokenType.LIT_FLOAT, rollback=True)).exec(self, self.current_char)

    def lex_lit_float_exp(self):
        Switcher.from_dict({
            ('+', '-'): lambda ctx: (ctx.add_to_buff(), ctx.to_state(LexingState.LIT_FLOAT_PRE_END)),
            ranges.digits: lambda ctx: (ctx.add_to_buff(), ctx.to_state(LexingState.LIT_FLOAT_END))
        }).default(lambda ctx: throw(TokenError('After exponent has to follow number or sign'))) \
            .exec(self, self.current_char)

    def lex_lit_float_pre_end(self):
        Switcher.from_dict({
            ranges.digits: lambda ctx: (ctx.add_to_buff(), ctx.to_state(LexingState.LIT_FLOAT_END))
        }).default(lambda ctx: throw(TokenError('Exponent power is missing'))).exec(self, self.current_char)

    def lex_lit_float_end(self):
        Switcher.from_dict({
            ranges.digits: lambda ctx: ctx.add_to_buff()
        }).default(lambda ctx: ctx.add_token(TokenType.LIT_FLOAT, rollback=True)).exec(self, self.current_char)

    def lex_op_gt(self):
        Switcher.from_dict({
            '=': lambda ctx: ctx.add_token(TokenType.OP_GE),
            ranges.letters: lambda ctx: (ctx.add_to_buff(), ctx.to_state(LexingState.AFTER_GT))
        }).default(lambda ctx: ctx.add_token(TokenType.OP_GT, rollback=True)).exec(self, self.current_char)

    def lex_after_gt(self):
        Switcher.from_dict({
            ranges.letters: lambda ctx: ctx.add_to_buff()
        }).default(lambda ctx: ctx.complete_helper()).exec(self, self.current_char)

    def lex_lit_str(self):
        Switcher.from_dict({
            '"': lambda ctx: ctx.add_token(TokenType.LIT_STR),
            '\\': lambda ctx: ctx.to_state(LexingState.LIT_STR_ESCAPE),
            '\n': lambda ctx: (ctx.add_to_buff(), ctx.inc_new_line())
        }).default(lambda ctx: ctx.add_to_buff()).exec(self, self.current_char)

    def lex_lit_str_escape(self):
        Switcher.from_dict({
            '"': lambda ctx: ctx.add_to_buff('\"'),
            't': lambda ctx: ctx.add_to_buff('\t'),
            'n': lambda ctx: ctx.add_to_buff('\n')
        }).default(lambda ctx: throw(TokenError('Unrecognized escaped character'))).exec(self, self.current_char)

        self.to_state(LexingState.LIT_STR)

    def lex_identifier(self):
        Switcher.from_dict({
            ranges.letters: lambda ctx: ctx.add_to_buff(),
            ranges.digits: lambda ctx: ctx.add_to_buff(),
            '_': lambda ctx: ctx.add_to_buff(),
        }).default(lambda ctx: ctx.complete_identifier()).exec(self, self.current_char)

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

        printer.error('\n'.join(lines_to_show), f'Lexing error [{self.line_number}:{self.offset_in_line}] : {cause}')

    @staticmethod
    def line_number_prefix(number):
        return f'{number}. '

