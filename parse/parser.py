from typing import List, Union

from models import Token, TokenType, type_tokens, primitive_type_tokens
import models.ast_nodes as ast


class Parser:

    tokens: List[Token]
    offset: int

    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.offset = 0

    def parse(self) -> ast.Program:
        root_elements = []

        while not self.accept(TokenType.EOF):
            root_elements.append(self.parse_root_elem())

        return ast.Program(root_elements)

    def parse_root_elem(self) -> Union[ast.Decl, ast.Helper]:
        if self.next_token_type() == TokenType.HELPER_INCLUDE:
            return self.parse_helper_incl()

        if self.next_token_type() == TokenType.KW_FUN:
            return self.parse_decl_fun()

        if Parser.is_type_token(self.next_token_type()) or self.next_token_type() == TokenType.KW_CONST:
            return self.parse_decl_var()

        if self.next_token_type() == TokenType.KW_UNIT:
            return self.parse_decl_unit()

        raise ValueError(f'Not root elem: {self.next_token_type()}')

    def parse_decl_fun(self) -> ast.DeclFun:
        self.expect(TokenType.KW_FUN)
        name = self.expect(TokenType.IDENTIFIER)

        # function with parameters
        if self.accept(TokenType.C_ROUND_L):
            params = self.parse_fun_params()
            self.expect(TokenType.C_ROUND_R)
        else:
            params = []

        # function with return type
        if self.accept(TokenType.KW_FAT_ARROW):
            return_type = self.expect_type()
        else:
            return_type = ast.TypePrimitive(TokenType.PRIMITIVE_VOID)

        statement_block = self.parse_block()

        return ast.DeclFun(name, params, return_type, statement_block)

    def parse_fun_params(self) -> List[ast.FunParam]:
        params = []

        # function without parameters
        if self.next_token_type() == TokenType.C_ROUND_R:
            return params

        params.append(self.parse_fun_param())
        while self.accept(TokenType.C_COMMA):
            params.append(self.parse_fun_param())

        return params

    def parse_fun_param(self) -> ast.FunParam:
        type_ = self.expect_type()
        name = self.expect(TokenType.IDENTIFIER)
        return ast.FunParam(type_, name)

    def parse_decl_var(self) -> ast.DeclVar:
        is_constant = self.accept(TokenType.KW_CONST) is not None
        type_ = self.expect_type()
        name = self.expect(TokenType.IDENTIFIER)

        if self.accept(TokenType.OP_ASSIGN):
            value = self.parse_expr()
        else:
            value = None

        self.expect(TokenType.C_SEMI)

        return ast.DeclVar(type_, name, value, is_constant)

    def parse_decl_unit(self) -> ast.DeclUnit:
        self.expect(TokenType.KW_UNIT)
        name = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.C_CURLY_L)

        fields = []
        while not self.accept(TokenType.C_CURLY_R):
            fields.append(self.parse_decl_unit_field())

        return ast.DeclUnit(name, fields)

    def parse_decl_unit_field(self) -> ast.DeclUnitField:
        type_ = self.expect_type()
        name = self.expect(TokenType.IDENTIFIER)

        self.expect(TokenType.C_SEMI)

        return ast.DeclUnitField(type_, name)

    def parse_helper_incl(self) -> ast.HelperInclude:
        helper_include = self.expect(TokenType.HELPER_INCLUDE)
        return ast.HelperInclude(helper_include)

    def parse_block(self) -> ast.StatementBlock:
        statements = []

        self.expect(TokenType.C_CURLY_L)
        while not self.accept(TokenType.C_CURLY_R):
            statements.append(self.parse_statement())

        return ast.StatementBlock(statements)

    def parse_statement(self) -> ast.Statement:
        pass

    def parse_expr(self) -> ast.Expr:
        return self.parse_expr_10()

    def parse_expr_10(self) -> ast.Expr:
        result = self.parse_expr_9()

        if self.accept(TokenType.OP_ASSIGN):
            if Parser.is_assignable(result):
                return ast.ExprAssign(result, self.parse_expr_10())
            raise ValueError(f'You cannot assign to {type(result).__name__}')

        return result

    def parse_expr_9(self) -> ast.Expr:
        result = self.parse_expr_8()

        while True:
            if self.accept(TokenType.OP_OR):
                result = ast.ExprOr(result, self.parse_expr_8())
            else:
                break

        return result

    def parse_expr_8(self) -> ast.Expr:
        result = self.parse_expr_7()

        while True:
            if self.accept(TokenType.OP_AND):
                result = ast.ExprAnd(result, self.parse_expr_7())
            else:
                break

        return result

    def parse_expr_7(self) -> ast.Expr:
        result = self.parse_expr_6()

        while True:
            if self.accept(TokenType.OP_EQ):
                result = ast.ExprEq(result, self.parse_expr_6())
            elif self.accept(TokenType.OP_NE):
                result = ast.ExprNe(result, self.parse_expr_6())
            else:
                break

        return result

    def parse_expr_6(self) -> ast.Expr:
        left = self.parse_expr_5()

        if self.accept(TokenType.OP_GT):
            return ast.ExprGt(left, self.parse_expr_5())

        if self.accept(TokenType.OP_GE):
            return ast.ExprGe(left, self.parse_expr_5())

        if self.accept(TokenType.OP_LT):
            return ast.ExprLt(left, self.parse_expr_5())

        if self.accept(TokenType.OP_LE):
            return ast.ExprLe(left, self.parse_expr_5())

        return left

    def parse_expr_5(self) -> ast.Expr:
        result = self.parse_expr_4()

        while True:
            if self.accept(TokenType.OP_PLUS):
                result = ast.ExprAdd(result, self.parse_expr_4())
            elif self.accept(TokenType.OP_MINUS):
                result = ast.ExprSub(result, self.parse_expr_4())
            else:
                break

        return result

    def parse_expr_4(self) -> ast.Expr:
        result = self.parse_expr_3()

        while True:
            if self.accept(TokenType.OP_MUL):
                result = ast.ExprMul(result, self.parse_expr_3())
            elif self.accept(TokenType.OP_DIV):
                result = ast.ExprDiv(result, self.parse_expr_3())
            elif self.accept(TokenType.OP_MOD):
                result = ast.ExprMod(result, self.parse_expr_3())
            else:
                break

        return result

    def parse_expr_3(self) -> ast.Expr:
        if self.accept(TokenType.OP_PLUS):
            return ast.ExprUPlus(self.parse_expr_3())

        elif self.accept(TokenType.OP_MINUS):
            return ast.ExprUMinus(self.parse_expr_3())

        return self.parse_expr_2()

    def parse_expr_2(self) -> ast.Expr:
        result = self.parse_expr_1()

        while True:
            if self.accept(TokenType.OP_POV):
                result = ast.ExprPow(self.parse_expr_1(), result)
            else:
                break

        return result

    def parse_expr_1(self) -> ast.Expr:
        result = self.parse_expr_0()

        while True:
            if self.accept(TokenType.C_SQUARE_L):
                index = self.parse_expr()
                self.expect(TokenType.C_SQUARE_R)
                result = ast.ExprArrayAccess(result, index)
            elif self.accept(TokenType.OP_ACCESS):
                result = ast.ExprAccess(result, self.expect(TokenType.IDENTIFIER))
            else:
                break

        return result

    def parse_expr_0(self):
        curr_token = self.get_next_token()

        if curr_token.type == TokenType.LIT_STR:
            return ast.ExprLitStr(curr_token)

        if curr_token.type == TokenType.LIT_FLOAT:
            return ast.ExprLitFloat(curr_token)

        if curr_token.type == TokenType.LIT_INT:
            return ast.ExprLitInt(curr_token)

        if curr_token.type == TokenType.CONSTANT_TRUE or curr_token.type == TokenType.CONSTANT_FALSE:
            return ast.ExprLitBool(curr_token)

        if curr_token.type == TokenType.CONSTANT_NULL:
            return ast.ExprLitNull(curr_token)

        if curr_token.type == TokenType.C_SQUARE_L:
            items = []
            while not self.accept(TokenType.C_SQUARE_R):
                items.append(self.parse_expr())
                self.accept(TokenType.C_COMMA)
            return ast.ExprLitArray(items)

        if curr_token.type == TokenType.C_ROUND_L:
            result = self.parse_expr()
            self.expect(TokenType.C_ROUND_R)
            return result

        if curr_token.type == TokenType.KW_FROM_STDIN:
            return ast.ExprFromStdin()

        if curr_token.type == TokenType.IDENTIFIER:
            if self.accept(TokenType.C_ROUND_L):
                params = []
                while not self.accept(TokenType.C_ROUND_R):
                    params.append(self.parse_expr())
                    self.accept(TokenType.C_COMMA)
                return ast.ExprFnCall(curr_token, params)

            return ast.ExprVar(curr_token)

    """
    Helper methods
    """
    def accept(self, token_type: TokenType) -> Union[Token, None]:
        curr_token = self.tokens[self.offset]
        if curr_token.type == token_type:
            self.offset += 1
            return curr_token

        return None

    def expect(self, token_type: TokenType) -> Token:
        curr_token = self.tokens[self.offset]
        if curr_token.type == token_type:
            self.offset += 1
            return curr_token

        raise ValueError(f'Expected {token_type}. Got: {curr_token.type}')

    def get_next_token(self):
        token = self.tokens[self.offset]
        self.offset += 1
        return token

    def next_token_type(self) -> TokenType:
        return self.tokens[self.offset].type

    def expect_type(self) -> ast.Type:
        if self.next_token_type() not in type_tokens:
            raise ValueError("Type token expected")

        type_token = self.get_next_token()

        if self.accept(TokenType.C_SQUARE_L):
            self.expect(TokenType.C_SQUARE_R)
            is_array = True
        else:
            is_array = False

        if type_token.type in primitive_type_tokens:
            return ast.TypePrimitive(type_token.type, is_array)
        else:
            return ast.TypeUnit(type_token.value, is_array)

    @staticmethod
    def is_type_token(token_type: TokenType):
        return token_type in type_tokens

    @staticmethod
    def is_assignable(expr: ast.Expr) -> bool:
        return type(expr) in (ast.ExprAccess, ast.ExprArrayAccess, ast.ExprVar)

