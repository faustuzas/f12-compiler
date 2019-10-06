from termcolor import colored


class TerminalPrinter:
    header_len = 50
    header_frame_symbol = '*'

    colour_error = 'red'

    def success(self, main: str, header: str = None) -> None:
        pass

    def error(self, main: str, header: str = None) -> None:
        output = ''
        if header:
            output += colored(self.__header(header), self.colour_error)
        output += colored(main, self.colour_error)

        print(output)

    def info(self, main: str, header: str = None) -> None:
        pass

    def __header(self, header: str) -> str:
        padding_len = (self.header_len - len(header) - 2) // 2
        extra_pad = (self.header_len - len(header) - 2) % 2
        padding_left = ' ' * padding_len
        padding_right = padding_left + ' ' * extra_pad

        return \
            self.header_frame_symbol * self.header_len + '\n' \
            + self.header_frame_symbol + padding_left + header + padding_right + self.header_frame_symbol + '\n' \
            + self.header_frame_symbol * self.header_len + '\n'
