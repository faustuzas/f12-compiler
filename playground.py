from blessed import Terminal
from time import sleep

t = Terminal()

x = int(t.width / 2)


def get_symbol():
    with t.raw():
        return t.inkey(timeout=0)


def read_all_chars():
    buffer = ''

    char = get_symbol()
    while char:
        buffer += char
        char = get_symbol()

    return buffer


with t.hidden_cursor():
    print(t.clear())
    for i in range(t.height):
        for ch in read_all_chars():
            if ch == 'a':
                x -= 1
            if ch == 'd':
                x += 1

        with t.location(x, i):
            print('a')

        sleep(2)
        print(t.clear())

"""
    IDET --> ! <--

    Ko man reikia is cia?
    
    Funkciju:
    
    void clear_screen();
    void put_char_x_y(char c, int x, int y);
    int commands_got = get_input(int[] buffer);
    void sleep(int ms);

"""