from unittest import TestCase

from utils import FasterSwitcher, ranges
from models import ExtendedEnum


class TestEnum(ExtendedEnum):
    KEY_1 = 'KEY_1'
    KEY_2 = 'KEY_2'
    KEY_3 = 'KEY_3'


class SwitcherTests(TestCase):
    switch = FasterSwitcher.from_dict({
        (TestEnum.KEY_1, TestEnum.KEY_2): lambda ctx: 'tuple of enums',
        '-': lambda ctx: 'char',
        ranges.digits: lambda ctx: 'str number',
        ranges.letters: lambda ctx: 'letters range',
        TestEnum.KEY_3: lambda ctx: 'enum'
    }).default(lambda ctx: 'default')

    def test_matches_char(self):
        self.assertEqual('char', self.switch.exec(self, '-'))

    def test_matches_str_number(self):
        self.assertEqual('str number', self.switch.exec(self, '2'))

    def test_matches_letter_range(self):
        self.assertEqual('letters range', self.switch.exec(self, 'z'))

    def test_returns_tuple(self):
        self.assertEqual('tuple of enums', self.switch.exec(self, TestEnum.KEY_1))
        self.assertEqual('tuple of enums', self.switch.exec(self, TestEnum.KEY_2))

    def test_returns_enum(self):
        self.assertEqual('enum', self.switch.exec(self, TestEnum.KEY_3))

    def test_returns_default(self):
        self.assertEqual('default', self.switch.exec(self, '@'))