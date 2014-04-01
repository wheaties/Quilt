__author__ = 'Owein'

from unittest import TestCase
from guard import *


class _Yo(Guard):
    def __init__(self, name):
        super(_Yo, self).__init__(arg_name=name)

    def validate(self, value):
        return True


class GuardTest(TestCase):
    def test_validate_obj_no_attr(self):
        g = _Yo('y')
        self.assertFalse(g.validate_object(object()))

    def test_validate_obj(self):
        g = _Yo('x')
        class Foo(object):
            x = 1

        self.assertTrue(g.validate_object(Foo()))

    # def test_neg(self):
    #     g = _Yo('y')
    #     self.assertTrue(g.validate_object(object()))
    #
    # def test_neg_no_attr(self):
    #     g = not _Yo('x')
    #     class Foo(object):
    #         x = 1
    #
    #     self.assertTrue(g.validate_object(Foo()))


class OperatorGuardTest(TestCase):
    def test_less(self):
        g = lt(1)

        self.assertTrue(g.validate(0))
        self.assertFalse(g. validate(1))

    def test_less_or_equal(self):
        g = lte(1)

        self.assertTrue(g.validate(0))
        self.assertTrue(g.validate(1))
        self.assertFalse(g. validate(2))

    def test_greater(self):
        g = gt(0)

        self.assertTrue(g.validate(1))
        self.assertFalse(g. validate(0))

    def test_greater_or_equal(self):
        g = gte(0)

        self.assertTrue(g.validate(1))
        self.assertTrue(g.validate(0))
        self.assertFalse(g. validate(-1))

    # def test_range(self):
    #     g = 0 < guard < 3
    #
    #     print(g)
    #
    #     self.assertTrue(g.validate(2))
    #     self.assertFalse(g.validate(0))
    #     self.assertFalse(g.validate(3))