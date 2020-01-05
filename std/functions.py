def init_functions():
    import models.ast_nodes as ast
    from models import types, token, instructions

    return [
        ast.DeclFun(
            token.Token(token.TokenType.IDENTIFIER, 0, 'std', 0, value='clear_screen'),
            [],
            ast.AstTypePrimitive(types.Void),
            ast.StmntBlock([]),
            instructions.InstructionType.CLEAR_SCREEN
        )
    ]