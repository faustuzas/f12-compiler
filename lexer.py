from models import LexingState


"""
What can I found? 
    - "+"
    - "-"
        + "-"
            + ">"
    - "/"
        + ""
        + "/"
        + "*"
    - "*"
        + ""
        + "/"
    - "%"
    - "^"
    - "."
        + "[0-9]*"
            + ""
            + "E" or "e"
                + "" or "+" or "-"
                    + "[0-9]*"
    - "!"
        + ""
        + "="
    - "="
        + ""
        + "="
    - ">"
        + ""
        + "="
        + "include"
    - "<"
        + ""
        + "="
        + "-"
            + "-"
    - "&"
        + "&"
    - "|"
        + "|"
    - ";"
    - ":"
    - ","
    - "("
    - ")"
    - "{"
    - "}"
    - "["
    - "]"
    - "[0-9]*"
        + "" // int
        + "."
            + ""
            + "[0-9]*"
                + ""
                + "E" or "e"
                    + "" or "+" or "-"
                        + "[0-9]*"
    - "\""
        + ".*"
            + "\""
        + "\\"
            + "n" or "t" or "\"" or "r"
                + back to string
    - [a-zA-z]
        + [a-zA-z1-9_]
            = keyword
            = identifier
            = type
    
"""

class Lexer:
    token_buffer: str = ''
    line_number: int = 1
    offset: int = 0
    state: LexingState = LexingState.START
    tokens: list = []
    token_start_line_number: int = 0
    current_char: str = None

    def __init__(self, text: str) -> None:
        assert len(text)

        self.text = text
        self.current_char = text[0]

    def proceed(self, string=False) -> None:
        """
        If string is set to true, then don't increase line number on new line symbol
        """
        if string:
            self.offset += 1
        else:
            if self.current_char == '\n':
                self.line_number += 1
                self.offset = 0
            else:
                self.offset += 1

        self.current_char = self.text[self.offset]


if __name__ == '__main__':
    with open("main.f12") as main_file:
        source_text = ''.join(main_file.readlines())

        lexer = Lexer(source_text)



