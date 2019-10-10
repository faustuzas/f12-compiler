from unittest import TestCase
from models import ExtendedEnum


class TestEnum(ExtendedEnum):
    VALUE_1 = 'VALUE_1'
    VALUE_2 = 'VALUE_2'
    VALUE_3 = 'VALUE_3'


class ExtendedEnumTest(TestCase):

    def test_enum_eq_value_eq_static(self):
        enum = TestEnum.VALUE_1

        self.assertEqual(TestEnum.VALUE_1, enum)

    def test_enum_eq_value_neq_static(self):
        enum = TestEnum.VALUE_1

        self.assertNotEqual(TestEnum.VALUE_2, enum)

    def test_enum_eq_value_eq_value(self):
        enum = TestEnum.VALUE_1
        enum2 = TestEnum.VALUE_1

        self.assertEqual(enum, enum2)

    def test_enum_eq_value_neq_value(self):
        enum = TestEnum.VALUE_1
        enum2 = TestEnum.VALUE_2

        self.assertNotEqual(enum, enum2)
