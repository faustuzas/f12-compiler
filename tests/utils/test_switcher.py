from unittest import TestCase

from utils import Switcher, ranges


class SwitcherTests(TestCase):
    switch = Switcher.from_dict({
        't': lambda: 'char',
        4: lambda: 'number',
        ranges.digits: lambda: 'str number',
        range(6, 10): lambda: 'number range',
        ranges.letters: lambda: 'letters range'
    }).default(lambda: 'default')

    def test_matches_number(self):
        self.assertEqual('number', self.switch.exec(4))

    def test_matches_char(self):
        self.assertEqual('char', self.switch.exec('t'))

    def test_matches_str_number(self):
        self.assertEqual('str number', self.switch.exec('2'))

    def test_matches_number_range(self):
        self.assertEqual('number range', self.switch.exec(8))

    def test_matches_letter_range(self):
        self.assertEqual('letters range', self.switch.exec('z'))

    def test_returns_default(self):
        self.assertEqual('default', self.switch.exec('@'))
