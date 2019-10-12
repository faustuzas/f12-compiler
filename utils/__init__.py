from .terminal_printer import TerminalPrinter
from .switcher import Switcher
import utils.ranges as ranges


def throw(ex):
    raise ex


def get(dictionary: dict, key):
    try:
        return dictionary[key]
    except KeyError:
        return None


printer = TerminalPrinter()
