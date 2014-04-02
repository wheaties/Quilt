__author__ = 'Owein'

from pattern import *
from unittest import TestCase
from guard import lt, gt


#You know, this is really not testing @pattern!
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
        pat = pattern(1)

        self.assertFalse(pat.validate(object()))

    def test_validate3(self):
        pat = pattern(1)

        self.assertFalse(pat.validate(object()))

    def test_validate4(self):
        pat = pattern(x=1)
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
        @pattern(x=lt(0))
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
        @pattern(3)
        def that(x):
            return 1

        self.assertEquals(that(3), 1)
        self.assertRaises(TypeError, lambda: that(1))


class TestDefPattern(TestCase):
    def test_call1(self):
        @defpattern(x=1)
        def test(x):
            return x

        self.assertEquals(test(1), 1)
        self.assertRaises(TypeError, lambda: test(2))

    def test_stacked_call(self):
        @defpattern(1)
        def test(x):
            return 1

        @defpattern(x=4)
        def test(x=gt(4)):
            return 2*x

        self.assertEquals(test(1), 1)
        self.assertEquals(test(5), 10)
        self.assertRaises(TypeError, lambda: test(0))