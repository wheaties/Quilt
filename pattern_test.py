__author__ = 'Owein'

from pattern import *
from guard import guard
from unittest import TestCase


# class TestGuardType(TestCase):
#     def test_non(self):
#         g = _guard_type(1)
#         self.assertIsInstance(g, Guard)
#
#     def test_pattern(self):
#         g = _guard_type(Pattern([],[]))
#         self.assertIsInstance(g, Guard)
#
#     def test_guard(self):
#         g = _guard_type(guard < 1)
#         self.assertIsInstance(g, Guard)


class PatternTest(TestCase):
    def test_validate1(self):
        pat = pattern(x=1)
        class Foo(object):
            x = 1

        class Bar(object):
            x = 2

        self.assertTrue(pat.validate(Foo()))
        self.assertFalse(pat.validate(Bar()))

    def test_validate2(self):
        pat = pattern(guard == 1)

        self.assertFalse(pat.validate(object()))

    def test_validate3(self):
        pat = pattern(1)

        self.assertFalse(pat.validate(object()))

    def test_validate4(self):
        pat = pattern(x=guard == 1)
        class Foo(object):
            x = 1

        self.assertTrue(pat.validate(Foo()))

    def test_call(self):
        @pattern(1)
        def that(x):
            return x

        self.assertEquals(that(1), 1)
        self.assertRaises(TypeError, lambda: that(2))

    def test_call2(self):
        @pattern()
        def that(x):
            return x

        self.assertEquals(that(1), 1)

    def test_call3(self):
        @pattern(x=1)
        def that(x):
            return 1

        self.assertEquals(that(1), 1)
        self.assertRaises(TypeError, lambda: that(2))

    def test_call4(self):
        @pattern(x=guard < 0)
        def that(x):
            return x

        self.assertEquals(that(-1), -1)
        self.assertRaises(TypeError, lambda: that(2))

    def test_call5(self):
        @pattern(y=1)
        def that(x):
            return 1

        self.assertEquals(that(1), 1) #TODO: how is this passing?
        self.assertEquals(that(2), 1) #but this isn't?

    def test_call6(self):
        @pattern(guard == 3)
        def that(x):
            return 1

        self.assertEquals(that(3), 1)
        self.assertRaises(TypeError, lambda: that(1))