__author__ = 'Owein'

from pattern import *
from guard import guard
from unittest import TestCase


class PatternTest(TestCase):
    def prun(self, pat):
        class Foo(object):
            x = 1

        class Bar(object):
            x = 2

        self.assertTrue(pat.validate(Foo()))
        self.assertFalse(pat.validate(Bar()))

    def test_validate1(self):
        self.prun(pattern(x=1))

    def test_validate2(self):
        self.prun(pattern(guard == 1))

    def test_validate3(self):
        pat = pattern(1)

        self.assertRaises(TypeError, lambda: pat.validate(object()))

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