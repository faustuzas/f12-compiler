from typing import List
from models import LexingState, Token, TokenType, TokenError
from models.builtins import keywords, primitive_types, constants, helpers
from utils import FasterSwitcher as Switcher, throw, ranges, printer


class StaticLexer:
    state: LexingState
    token_buffer: str
    line_number: int
    offset: int
    offset_in_line: int
    tokens: List[Token]
    token_start_line_number: int
    current_char: str

    @staticmethod
    def init(text: str) -> None:
        assert len(text)

        StaticLexer.state = LexingState.START
        StaticLexer.token_buffer = ''
        StaticLexer.line_number = 1
        StaticLexer.offset = 0
        StaticLexer.offset_in_line = 0
        StaticLexer.tokens: List[Token] = []
        StaticLexer.token_start_line_number = 0
        StaticLexer.text = text
        StaticLexer.current_char = ''

    _s_all = Switcher.from_dict({
                (LexingState.START, LexingState.SL_COMMENT): lambda: StaticLexer.add_token(TokenType.EOF),
                (LexingState.ML_COMMENT, LexingState.ML_COMMENT_END): lambda: throw(TokenError("Unterminanted multiline comment")),
                LexingState.LIT_STR: lambda: throw(TokenError('Unterminated string'))
            })

    @staticmethod
    def lex_all():
        try:
            while StaticLexer.offset < len(StaticLexer.text):
                StaticLexer.current_char = StaticLexer.text[StaticLexer.offset]
                StaticLexer.lex()
                StaticLexer.offset += 1
                StaticLexer.offset_in_line += 1

            StaticLexer.current_char = ' '
            StaticLexer.lex()

            StaticLexer._s_all.exec(StaticLexer.state)
        except TokenError as e:
            StaticLexer.print_error(str(e))
            raise ValueError()

        return StaticLexer.tokens

    _s_lex = Switcher.from_dict({
            LexingState.START: StaticLexer.lex_start,
            LexingState.OP_MINUS: StaticLexer.lex_op_minus,
            LexingState.OP_MINUS_2: StaticLexer.lex_op_minus_2,
            LexingState.OP_DIV: StaticLexer.lex_op_div,
            LexingState.SL_COMMENT: StaticLexer.lex_sl_comment,
            LexingState.ML_COMMENT: StaticLexer.lex_ml_comment,
            LexingState.ML_COMMENT_END: StaticLexer.lex_ml_comment_end,
            LexingState.OP_NOT: StaticLexer.lex_op_not,
            LexingState.OP_ASSIGN: StaticLexer.lex_op_assign,
            LexingState.OP_AND: StaticLexer.lex_op_and,
            LexingState.OP_OR: StaticLexer.lex_op_or,
            LexingState.OP_LT: StaticLexer.lex_op_lt,
            LexingState.KW_FROM_STDIN: StaticLexer.lex_kw_from_stdin,
            LexingState.OP_ACCESS: StaticLexer.lex_op_access,
            LexingState.LIT_INT_FIRST_ZERO: StaticLexer.lex_lit_int_first_zero,
            LexingState.LIT_INT: StaticLexer.lex_lit_int,
            LexingState.LIT_FLOAT_START: StaticLexer.lex_lit_float_start,
            LexingState.LIT_FLOAT: StaticLexer.lex_lit_float,
            LexingState.LIT_FLOAT_EXP: StaticLexer.lex_lit_float_exp,
            LexingState.LIT_FLOAT_PRE_END: StaticLexer.lex_lit_float_pre_end,
            LexingState.LIT_FLOAT_END: StaticLexer.lex_lit_float_end,
            LexingState.OP_GT: StaticLexer.lex_op_gt,
            LexingState.AFTER_GT: StaticLexer.lex_after_gt,
            LexingState.LIT_STR: StaticLexer.lex_lit_str,
            LexingState.LIT_STR_ESCAPE: StaticLexer.lex_lit_str_escape,
            LexingState.IDENTIFIER: StaticLexer.lex_identifier
        })

    @staticmethod
    def lex():
        StaticLexer._s_lex.exec(StaticLexer.state)

    _s_lex_start = Switcher.from_dict({
            '+': lambda: StaticLexer.add_token(TokenType.OP_PLUS),
            '*': lambda: StaticLexer.add_token(TokenType.OP_MUL),
            '^': lambda: StaticLexer.add_token(TokenType.OP_POV),
            '%': lambda: StaticLexer.add_token(TokenType.OP_MOD),
            ';': lambda: StaticLexer.add_token(TokenType.C_SEMI),
            ':': lambda: StaticLexer.add_token(TokenType.C_COLON),
            ',': lambda: StaticLexer.add_token(TokenType.C_COMMA),
            '(': lambda: StaticLexer.add_token(TokenType.C_ROUND_L),
            ')': lambda: StaticLexer.add_token(TokenType.C_ROUND_R),
            '{': lambda: StaticLexer.add_token(TokenType.C_CURLY_L),
            '}': lambda: StaticLexer.add_token(TokenType.C_CURLY_R),
            '[': lambda: StaticLexer.add_token(TokenType.C_SQUARE_L),
            ']': lambda: StaticLexer.add_token(TokenType.C_SQUARE_R),
            '-': lambda: StaticLexer.begin_tokenizing(LexingState.OP_MINUS),
            '/': lambda: StaticLexer.begin_tokenizing(LexingState.OP_DIV),
            '!': lambda: StaticLexer.begin_tokenizing(LexingState.OP_NOT),
            '=': lambda: StaticLexer.begin_tokenizing(LexingState.OP_ASSIGN),
            '&': lambda: StaticLexer.begin_tokenizing(LexingState.OP_AND),
            '|': lambda: StaticLexer.begin_tokenizing(LexingState.OP_OR),
            '<': lambda: StaticLexer.begin_tokenizing(LexingState.OP_LT),
            '.': lambda: StaticLexer.begin_tokenizing(LexingState.OP_ACCESS),
            '>': lambda: StaticLexer.begin_tokenizing(LexingState.OP_GT),
            '"': lambda: StaticLexer.begin_tokenizing(LexingState.LIT_STR),
            '0': lambda: StaticLexer.begin_tokenizing(LexingState.LIT_INT_FIRST_ZERO, to_buffer=True),
            ranges.digits: lambda: StaticLexer.begin_tokenizing(LexingState.LIT_INT, to_buffer=True),
            '_': lambda: StaticLexer.begin_tokenizing(LexingState.IDENTIFIER, to_buffer=True),
            ranges.letters: lambda: StaticLexer.begin_tokenizing(LexingState.IDENTIFIER, to_buffer=True),
            '\n': StaticLexer.inc_new_line,
            ' ': lambda: ()  # ignore
        }).default(lambda: throw(TokenError('Unrecognised token')))

    @staticmethod
    def lex_start():
        StaticLexer._s_lex_start.exec(StaticLexer.current_char)

    _s_lex_op_minus = Switcher.from_dict({
            '-': lambda: StaticLexer.to_state(LexingState.OP_MINUS_2)
        })

    @staticmethod
    def lex_op_minus():
        StaticLexer._s_lex_op_minus.exec(StaticLexer.current_char)

    _s_lex_op_minus_2 = Switcher.from_dict({
            '>': lambda: StaticLexer.add_token(TokenType.KW_TO_STDOUT),
            '-': lambda: StaticLexer.add_token(TokenType.OP_MINUS, keep_state=True)
        }).default(lambda: (StaticLexer.add_token(TokenType.OP_MINUS),
                            StaticLexer.add_token(TokenType.OP_MINUS)))

    @staticmethod
    def lex_op_minus_2():
        StaticLexer._s_lex_op_minus_2.exec(StaticLexer.current_char)

    _s_lex_op_div = Switcher.from_dict({
            '/': lambda: StaticLexer.to_state(LexingState.SL_COMMENT),
            '*': lambda: StaticLexer.to_state(LexingState.ML_COMMENT)
        }).default(lambda: StaticLexer.add_token(TokenType.OP_DIV, rollback=True))

    @staticmethod
    def lex_op_div():
        StaticLexer._s_lex_op_div.exec(StaticLexer.current_char)

    _s_lex_sl_comment = Switcher.from_dict({
            '\n': lambda: (StaticLexer.to_state(LexingState.START), StaticLexer.inc_new_line())
        })

    @staticmethod
    def lex_sl_comment():
        StaticLexer._s_lex_sl_comment.exec(StaticLexer.current_char)

    _s_lex_ml_comment = Switcher.from_dict({
            '\n': StaticLexer.inc_new_line,
            '*': lambda: StaticLexer.to_state(LexingState.ML_COMMENT_END)
        })

    @staticmethod
    def lex_ml_comment():
        StaticLexer._s_lex_ml_comment.exec(StaticLexer.current_char)

    _s_lex_ml_comment_end = Switcher.from_dict({
            '/': lambda: StaticLexer.to_state(LexingState.START)
        }).default(lambda: StaticLexer.to_state(LexingState.ML_COMMENT))

    @staticmethod
    def lex_ml_comment_end():
        StaticLexer._s_lex_ml_comment_end.exec(StaticLexer.current_char)

    _s_lex_op_not = Switcher.from_dict({
            '=': lambda: StaticLexer.add_token(TokenType.OP_NE)
        }).default(lambda: StaticLexer.add_token(TokenType.OP_NOT, rollback=True))

    @staticmethod
    def lex_op_not():
        StaticLexer._s_lex_op_not.exec(StaticLexer.current_char)

    _s_lex_op_assign = Switcher.from_dict({
            '=': lambda: StaticLexer.add_token(TokenType.OP_EQ),
            '>': lambda: StaticLexer.add_token(TokenType.KW_FAT_ARROW)
        }).default(lambda: StaticLexer.add_token(TokenType.OP_ASSIGN, rollback=True))

    @staticmethod
    def lex_op_assign():
        StaticLexer._s_lex_op_assign.exec(StaticLexer.current_char)

    _s_lex_op_and = Switcher.from_dict({
            '&': lambda: StaticLexer.add_token(TokenType.OP_AND)
        }).default(lambda: throw(TokenError('Missing &')))

    @staticmethod
    def lex_op_and():
        StaticLexer._s_lex_op_and.exec(StaticLexer.current_char)

    _s_lex_op_or = Switcher.from_dict({
            '|': lambda: StaticLexer.add_token(TokenType.OP_OR)
        }).default(lambda: throw(TokenError('Missing |')))

    @staticmethod
    def lex_op_or():
        StaticLexer._s_lex_op_or.exec(StaticLexer.current_char)

    _s_lex_op_lt = Switcher.from_dict({
            '=': lambda: StaticLexer.add_token(TokenType.OP_LE),
            '-': lambda: StaticLexer.to_state(LexingState.KW_FROM_STDIN)
        }).default(lambda: StaticLexer.add_token(TokenType.OP_LT, rollback=True))

    @staticmethod
    def lex_op_lt():
        StaticLexer._s_lex_op_lt.exec(StaticLexer.current_char)

    _s_lex_kw_from_stdin = Switcher.from_dict({
            '-': lambda: StaticLexer.add_token(TokenType.KW_FROM_STDIN)
        }).default(lambda: (StaticLexer.add_token(TokenType.OP_LT),
                            StaticLexer.add_token(TokenType.OP_MINUS, rollback=True)))

    @staticmethod
    def lex_kw_from_stdin():
        StaticLexer._s_lex_kw_from_stdin.exec(StaticLexer.current_char)

    _s_lex_op_access = Switcher.from_dict({
            ranges.digits: lambda: (StaticLexer.add_to_buff('.'), StaticLexer.add_to_buff(), StaticLexer.to_state(LexingState.LIT_FLOAT))
        }).default(lambda: StaticLexer.add_token(TokenType.OP_ACCESS, rollback=True))

    @staticmethod
    def lex_op_access():
        StaticLexer._s_lex_op_access.exec(StaticLexer.current_char)

    _s_lex_lit_int_first_zero = Switcher.from_dict({
            '.': lambda: (StaticLexer.add_to_buff(), StaticLexer.to_state(LexingState.LIT_FLOAT_START)),
            ranges.digits: lambda: throw(TokenError('Multi digit integer cannot start with 0'))
        }).default(lambda: StaticLexer.add_token(TokenType.LIT_INT, rollback=True))

    @staticmethod
    def lex_lit_int_first_zero():
        StaticLexer._s_lex_lit_int_first_zero.exec(StaticLexer.current_char)

    _s_lex_lit_int = Switcher.from_dict({
            ranges.digits: StaticLexer.add_to_buff,
            '.': lambda: (StaticLexer.add_to_buff(), StaticLexer.to_state(LexingState.LIT_FLOAT_START)),
            '_': lambda: throw(TokenError('Integer with invalid prefix')),
            ranges.letters: lambda: throw(TokenError('Integer with invalid prefix'))
        }).default(lambda: StaticLexer.add_token(TokenType.LIT_INT, rollback=True))

    @staticmethod
    def lex_lit_int():
        StaticLexer._s_lex_lit_int.exec(StaticLexer.current_char)

    _s_lex_lit_float_start = Switcher.from_dict({
            ranges.digits: lambda: (StaticLexer.add_to_buff(), StaticLexer.to_state(LexingState.LIT_FLOAT)),
        }).default(lambda: StaticLexer.add_token(TokenType.LIT_FLOAT, rollback=True))

    @staticmethod
    def lex_lit_float_start():
        StaticLexer._s_lex_lit_float_start.exec(StaticLexer.current_char)

    _s_lex_lit_float = Switcher.from_dict({
            ranges.digits: StaticLexer.add_to_buff,
            ('e', 'E'): lambda: (StaticLexer.add_to_buff(), StaticLexer.to_state(LexingState.LIT_FLOAT_EXP))
        }).default(lambda: StaticLexer.add_token(TokenType.LIT_FLOAT, rollback=True))

    @staticmethod
    def lex_lit_float():
        StaticLexer._s_lex_lit_float.exec(StaticLexer.current_char)

    _s_lex_lit_float_exp = Switcher.from_dict({
            ('+', '-'): lambda: (StaticLexer.add_to_buff(), StaticLexer.to_state(LexingState.LIT_FLOAT_PRE_END)),
            ranges.digits: lambda: (StaticLexer.add_to_buff(), StaticLexer.to_state(LexingState.LIT_FLOAT_END))
        }).default(lambda: throw(TokenError('After exponent has to follow number or sign')))

    @staticmethod
    def lex_lit_float_exp():
        StaticLexer._s_lex_lit_float_exp.exec(StaticLexer.current_char)

    _s_lex_lit_float_pre_end = Switcher.from_dict({
            ranges.digits: lambda: (StaticLexer.add_to_buff(), StaticLexer.to_state(LexingState.LIT_FLOAT_END))
        }).default(lambda: throw(TokenError('Exponent power is missing')))

    @staticmethod
    def lex_lit_float_pre_end():
        StaticLexer._s_lex_lit_float_pre_end.exec(StaticLexer.current_char)

    _s_lex_lit_float_end = Switcher.from_dict({
            ranges.digits: StaticLexer.add_to_buff
        }).default(lambda: StaticLexer.add_token(TokenType.LIT_FLOAT, rollback=True))

    @staticmethod
    def lex_lit_float_end():
        StaticLexer._s_lex_lit_float_end.exec(StaticLexer.current_char)

    _s_lex_op_gt = Switcher.from_dict({
            '=': lambda: StaticLexer.add_token(TokenType.OP_GE),
            ranges.letters: lambda: (StaticLexer.add_to_buff(), StaticLexer.to_state(LexingState.AFTER_GT))
        }).default(lambda: StaticLexer.add_token(TokenType.OP_GT, rollback=True))

    @staticmethod
    def lex_op_gt():
        StaticLexer._s_lex_op_gt.exec(StaticLexer.current_char)

    _s_lex_after_gt = Switcher.from_dict({
            ranges.letters: StaticLexer.add_to_buff
        }).default(StaticLexer.complete_helper)

    @staticmethod
    def lex_after_gt():
        StaticLexer._s_lex_after_gt.exec(StaticLexer.current_char)

    _s_lex_lit_str = Switcher.from_dict({
            '"': lambda: StaticLexer.add_token(TokenType.LIT_STR),
            '\\': lambda: StaticLexer.to_state(LexingState.LIT_STR_ESCAPE),
            '\n': lambda: (StaticLexer.add_to_buff(), StaticLexer.inc_new_line())
        }).default(StaticLexer.add_to_buff)

    @staticmethod
    def lex_lit_str():
        StaticLexer._s_lex_lit_str.exec(StaticLexer.current_char)

    _s_lex_lit_str_escape = Switcher.from_dict({
            '"': lambda: StaticLexer.add_to_buff('\"'),
            't': lambda: StaticLexer.add_to_buff('\t'),
            'n': lambda: StaticLexer.add_to_buff('\n')
        }).default(lambda: throw(TokenError('Unrecognized escaped character')))

    @staticmethod
    def lex_lit_str_escape():
        StaticLexer._s_lex_lit_str_escape.exec(StaticLexer.current_char)
        StaticLexer.to_state(LexingState.LIT_STR)

    _s_lex_identifier = Switcher.from_dict({
            ranges.letters: StaticLexer.add_to_buff,
            ranges.digits: StaticLexer.add_to_buff,
            '_': StaticLexer.add_to_buff,
        }).default(StaticLexer.complete_identifier)

    @staticmethod
    def lex_identifier():
        StaticLexer._s_lex_identifier.exec(StaticLexer.current_char)

    """
    Helper methods
    """
    @staticmethod
    def complete_identifier():
        kw = keywords.get(StaticLexer.token_buffer, None)
        if kw:
            StaticLexer.add_token(kw, with_value=False, line_number=StaticLexer.line_number, rollback=True)
            return
        primitive_type = primitive_types.get(StaticLexer.token_buffer, None)
        if primitive_type:
            StaticLexer.add_token(primitive_type, with_value=False, line_number=StaticLexer.line_number, rollback=True)
            return
        constant = constants.get(StaticLexer.token_buffer, None)
        if constant:
            StaticLexer.add_token(constant, with_value=False, line_number=StaticLexer.line_number, rollback=True)
            return

        StaticLexer.add_token(TokenType.IDENTIFIER, line_number=StaticLexer.line_number, rollback=True)

    @staticmethod
    def complete_helper():
        helper = helpers.get(StaticLexer.token_buffer, None)
        if helper:
            StaticLexer.add_token(helper, with_value=False)
        else:
            StaticLexer.add_token(TokenType.OP_GT, with_value=False, keep_buffer=True)
            StaticLexer.complete_identifier()

    @staticmethod
    def begin_tokenizing(new_state: LexingState, to_buffer=False):
        StaticLexer.token_start_line_number = StaticLexer.line_number
        StaticLexer.to_state(new_state)

        if to_buffer:
            StaticLexer.add_to_buff()

    @staticmethod
    def add_token(token_type: TokenType, line_number=None, rollback=False,
                  keep_state=False, with_value=True, keep_buffer=False):
        StaticLexer.tokens.append(Token(token_type, line_number if line_number else StaticLexer.line_number,
                                 StaticLexer.token_buffer if with_value else ''))
        if not keep_buffer:
            StaticLexer.token_buffer = ''
        if not keep_state:
            StaticLexer.state = LexingState.START
        if rollback:
            StaticLexer.offset -= 1
            StaticLexer.offset_in_line -= 1

    @staticmethod
    def add_to_buff(symbol=None):
        if symbol is None:
            StaticLexer.token_buffer += StaticLexer.current_char
        else:
            StaticLexer.token_buffer += symbol

    @staticmethod
    def to_state(state: LexingState):
        assert state is not None
        StaticLexer.state = state

    @staticmethod
    def inc_new_line():
        StaticLexer.line_number += 1
        StaticLexer.offset_in_line = 0

    @staticmethod
    def print_tokens():
        template = '{:>5} | {:>5} | {:>17} | {:>17}'
        header = template.format('ID', 'LINE', 'TYPE', 'VALUE')
        body = ''
        for (i, token) in enumerate(StaticLexer.tokens):
            body += template.format(i + 1, token.line_number, token.type, token.value) + '\n'

        printer.success(body, header)

    @staticmethod
    def print_error(cause):
        all_lines = StaticLexer.text.split('\n')
        lines_to_show = []
        line_in_array = StaticLexer.line_number - 1
        if StaticLexer.line_number - 1 >= 1 and len(all_lines[line_in_array - 1].strip()) > 0:
            lines_to_show.append(f'{StaticLexer.line_number_prefix(StaticLexer.line_number - 1)}{all_lines[line_in_array - 1]}')

        lines_to_show.append(f'{StaticLexer.line_number_prefix(StaticLexer.line_number)}{all_lines[line_in_array]}')
        lines_to_show.append(' ' * (StaticLexer.offset_in_line + len(StaticLexer.line_number_prefix(StaticLexer.line_number)) - 1) + '^')

        if StaticLexer.line_number + 1 <= len(all_lines) and len(all_lines[line_in_array + 1].strip()) > 0:
            lines_to_show.append(f'{StaticLexer.line_number_prefix(StaticLexer.line_number + 1)}{all_lines[line_in_array + 1]}')

        printer.error('\n'.join(lines_to_show), f'Lexing error [{StaticLexer.line_number}:{StaticLexer.offset_in_line}] : {cause}')

    @staticmethod
    def line_number_prefix(number):
        return f'{number}. '

