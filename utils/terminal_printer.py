from termcolor import colored


class TerminalPrinter:
    header_frame_symbol = '*'

    colour_error = 'red'
    colour_success = 'green'

    def success(self, main: str, header: str = None, header_len=None) -> None:
        self.print(main, header, self.colour_success, header_len=header_len)

    def error(self, main: str, header: str = None, header_len=None) -> None:
        self.print(main, header, self.colour_error, header_len=header_len)

    def info(self, main: str, header: str = None, header_len=None) -> None:
        self.print(main, header, header_len=header_len)

    def print(self, main: str, header: str = None, colour=None, header_len=None):
        output = ''
        if header:
            h_len = header_len
            if not h_len:
                h_len = len(main.split('\n')[0])

            if colour:
                output += colored(self.header_format(header, h_len), colour)
            else:
                output += self.header_format(header, h_len)

        if colour:
            output += colored(main, colour)
        else:
            output += main

        print(output)

    def header_format(self, header: str, header_len) -> str:
        header_frame = self.header_frame_symbol * header_len + '\n'
        return header_frame + ('{:^' + str(header_len) + '}\n').format(header) + header_frame
