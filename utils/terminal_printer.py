from termcolor import colored


class TerminalPrinter:
    header_len = 50
    header_frame_symbol = '*'

    colour_error = 'red'
    colour_success = 'green'

    def success(self, main: str, header: str = None) -> None:
        self.print(main, header, self.colour_success)

    def error(self, main: str, header: str = None) -> None:
        self.print(main, header, self.colour_error)

    def info(self, main: str, header: str = None) -> None:
        self.print(main, header)

    def print(self, main: str, header: str = None, colour = None):
        output = ''
        if header:
            if colour:
                output += colored(self.header_format(header), colour)
            else:
                output += self.header_format(header)

        if colour:
            output += colored(main, self.colour_error)
        else:
            output += main

        print(output)

    def header_format(self, header: str) -> str:
        padding_len = (self.header_len - len(header) - 2) // 2
        extra_pad = (self.header_len - len(header) - 2) % 2
        padding_left = ' ' * padding_len
        padding_right = padding_left + ' ' * extra_pad

        return \
            self.header_frame_symbol * self.header_len + '\n' \
            + self.header_frame_symbol + padding_left + header + padding_right + self.header_frame_symbol + '\n' \
            + self.header_frame_symbol * self.header_len + '\n'
