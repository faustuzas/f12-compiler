def init_functions():
    import models.ast_nodes as ast
    from models import types
    from models.token import TokenType
    from models.token import Token
    from models.instructions import InstructionType

    return [
        ast.DeclFun(
            Token(TokenType.IDENTIFIER, 0, 'std', 0, value='clear_screen'),
            [],
            ast.AstTypePrimitive(types.Void),
            ast.StmntBlock([]),
            InstructionType.CLEAR_SCREEN
        ),

        ast.DeclFun(
            Token(TokenType.IDENTIFIER, 0, 'std', 0, value='put_char_x_y'),
            [
                ast.FunParam(
                    ast.AstTypePrimitive(types.Char),
                    Token(TokenType.IDENTIFIER, 0, 'std', 0, value='c'),
                ),
                ast.FunParam(
                    ast.AstTypePrimitive(types.Int),
                    Token(TokenType.IDENTIFIER, 0, 'std', 0, value='x'),
                ),
                ast.FunParam(
                    ast.AstTypePrimitive(types.Int),
                    Token(TokenType.IDENTIFIER, 0, 'std', 0, value='y'),
                )
            ],
            ast.AstTypePrimitive(types.Void),
            ast.StmntBlock([]),
            InstructionType.PUT_CHAR_X_Y
        ),

        ast.DeclFun(
            Token(TokenType.IDENTIFIER, 0, 'std', 0, value='get_input'),
            [
                ast.FunParam(
                    ast.AstTypePointer(ast.AstTypeArray(ast.AstTypePrimitive(types.Char))),
                    Token(TokenType.IDENTIFIER, 0, 'std', 0, value='buff'),
                )
            ],
            ast.AstTypePrimitive(types.Int),
            ast.StmntBlock([]),
            InstructionType.GET_INPUT
        ),

        ast.DeclFun(
            Token(TokenType.IDENTIFIER, 0, 'std', 0, value='sleep'),
            [
                ast.FunParam(
                    ast.AstTypePrimitive(types.Int),
                    Token(TokenType.IDENTIFIER, 0, 'std', 0, value='ms'),
                )
            ],
            ast.AstTypePrimitive(types.Void),
            ast.StmntBlock([]),
            InstructionType.SLEEP
        )
    ]
