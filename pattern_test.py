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
        @pattern(x=1, y=1)
        def that(x, y):
            return 1

        self.assertEquals(that(1,1), 1)
        self.assertRaises(TypeError, lambda: that(1,2))
        self.assertRaises(TypeError, lambda: that(2,1))

    def test_call4(self):
        @pattern(x=lt(0))
        def that(x):
            return x

        self.assertEquals(that(x=-1), -1)
        self.assertRaises(TypeError, lambda: that(x=2))

    def test_call5(self):
        @pattern(y=1)
        def that(x):
            return 1

        self.assertEquals(that(x=1), 1)
        self.assertEquals(that(x=2), 1)

    def test_call6(self):
        @pattern(3)
        def that(x):
            return 1

        self.assertEquals(that(3), 1)
        self.assertRaises(TypeError, lambda: that(1))

    def test_placement(self):
        @pattern(x=1)
        def yoyo(x, z):
            return x+z

        @yoyo.z
        def arr(z):
            return z < 0

        self.assertEquals(yoyo(x=1, z=-1), 0)
        self.assertRaises(TypeError, lambda: yoyo(x=0, z=-1))
        self.assertRaises(TypeError, lambda: yoyo(x=1, z=1))


class TestMemberFuncPattern(TestCase):
    def setUp(self):
        self.guard = ValueGuard(1, arg_name='foo')
        self.pat = MemberFunctionPattern([], [self.guard])

    def tearDown(self):
        self.guard = None
        self.pat = None

    def test_call_noparams(self):
        @self.pat
        def that():
            return 1

        self.assertIsNone(self.guard.arg_pos)
        self.assertEquals(that(), 1)

    def test_oneparam(self):
        @self.pat
        def that(foo):
            return 1

        self.assertIsNone(self.guard.arg_pos)
        self.assertEquals(that(1), 1)

    def test_several_params(self):
        @self.pat
        def that(x, y):
            return 1

        self.assertIsNone(self.guard.arg_pos)
        self.assertEquals(that(2, 1), 1)

    def test_params(self):
        @self.pat
        def that(x, foo):
            return 1

        self.assertEquals(self.guard.arg_pos, 0)
        self.assertEquals(that(1, 1), 1)
        self.assertEquals(that(x=2, foo=1), 1)
        self.assertRaises(TypeError, lambda: that(2, 1))
        self.assertRaises(TypeError, lambda: that(foo=2, x=1))


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

        @defpattern(x=gt(4))
        def test(x):
            return 2*x

        self.assertEquals(test(1), 1)
        self.assertEquals(test(5), 10)
        self.assertRaises(TypeError, lambda: test(0))

    def test_module(self):
        from importlib import import_module
        @defpattern()
        def la():
            return 1

        module = import_module(la.__module__)
        self.assertTrue(hasattr(module, '__quilt__'))


class TestDefProxy(TestCase):
    def test_name(self):
        def yoyo(x):
            return 1

        proxy = DefProxy([yoyo], yoyo)
        self.assertEquals(proxy.__name__, 'yoyo')

    def test_module(self):
        def yoyo(x):
            return 1

        proxy = DefProxy([yoyo], yoyo)
        self.assertEquals(proxy.__module__, 'pattern_test')

    def test_get_attr(self):
        class Yo(object):
            x = 1
            y = 2

        proxy = DefProxy([], Yo())
        self.assertEquals(proxy.x, 1)
        self.assertEquals(proxy.y, 2)

    def test_call(self):
        class Yo(object):
            def __init__(self):
                self.underlying_func = lambda x: 1
            def validate(self, x):
                return True

        proxy = DefProxy([Yo()], None)
        self.assertEquals(proxy(4), 1)


class TestFunctionProxy(TestCase):
    def test_get_attr(self):
        class Yo(object):
            x = 1
            y = 2
        class MCache(object):
            most_recent = Yo()

        proxy = FunctionProxy(MCache())
        self.assertEquals(proxy.x, 1)
        self.assertEquals(proxy.y, 2)

    def test_call(self):
        class Cont(object):
            def __init__(self, f):
                self.f = f
            def __get__(self, instance, owner):
                return self.f

        class VV(object):
            def __init__(self, f, that=True):
                self.underlying_func = Cont(f)
                self.that = that
            def validate(self, x):
                return self.that

        one = VV(lambda x: 2, False)
        two = VV(lambda x: 1)
        proxy = FunctionProxy([one, two])
        self.assertEquals(proxy(1), 1)


#TODO:
# 1. Test the actual classes, not just the functions
# 2. Come up with decent mocks