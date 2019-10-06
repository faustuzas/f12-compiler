from termcolor import colored


class TerminalPrinter:
    HEADER_LEN = 50
    HEADER_FRAME_SYMBOL = '*'

    COLOUR_ERROR = 'red'

    def success(self, main: str, header: str = None) -> None:
        pass

    def error(self, main: str, header: str = None) -> None:
        output = ''
        if header:
            output += colored(self.__header(header), self.COLOUR_ERROR)
        output += colored(main, self.COLOUR_ERROR)

        print(output)

    def info(self, main: str, header: str = None) -> None:
        pass

    def __header(self, header: str) -> str:
        padding_len = (self.HEADER_LEN - len(header) - 2) // 2
        extra_pad = (self.HEADER_LEN - len(header) - 2) % 2
        padding_left = ' ' * padding_len
        padding_right = padding_left + ' ' * extra_pad

        return \
            self.HEADER_FRAME_SYMBOL * self.HEADER_LEN + '\n' \
            + self.HEADER_FRAME_SYMBOL + padding_left + header + padding_right + self.HEADER_FRAME_SYMBOL + '\n' \
            + self.HEADER_FRAME_SYMBOL * self.HEADER_LEN + '\n'
