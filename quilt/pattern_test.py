from quilt.pattern import *
from quilt.proxy import *
from unittest import TestCase
from quilt.guard import lt, gt
from quilt.exc import *


class Foo(object):
    x = 1


class PatternTest(TestCase):
    def test_call(self):
        class Bar(object):
            @pattern(1)
            def that(self, x):
                return x
        item = Bar()

        self.assertEquals(item.that(1), 1)
        self.assertRaises(MatchError, lambda: item.that(2))

    def test_call2(self):
        class Bar(object):
            @pattern()
            def that(self, x):
                return x

        item = Bar()
        self.assertEquals(item.that(1), 1)

    def test_call3(self):
        class Bar(object):
            @pattern(x=1, y=1)
            def that(self, x, y):
                return 1
        item = Bar()

        self.assertEquals(item.that(x=1, y=1), 1)
        self.assertRaises(MatchError, lambda: item.that(x=2, y=1))
        self.assertRaises(MatchError, lambda: item.that(y=2, x=1))

    def test_call4(self):
        class Bar(object):
            @pattern(x=lt(0))
            def that(self, x):
                return x
        item = Bar()

        self.assertEquals(item.that(x=-1), -1)
        self.assertRaises(MatchError, lambda: item.that(x=2))

    def test_call5(self):
        class Bar(object):
            @pattern(y=1)
            def that(self, x):
                return 1
        item = Bar()

        self.assertEquals(item.that(x=1), 1)
        self.assertEquals(item.that(x=2), 1)

    def test_placement(self):
        class Bar(object):
            @pattern(x=1)
            def yoyo(self, x, z):
                return x+z

            @yoyo.z
            def arr(self, z):
                return z < 0

        item = Bar()
        self.assertEquals(item.yoyo(x=1, z=-1), 0)
        self.assertRaises(MatchError, lambda: item.yoyo(x=0, z=-1))
        self.assertRaises(MatchError, lambda: item.yoyo(x=1, z=1))

    def test_stacked(self):
        class Bar(object):
            @pattern(x=1)
            def yoyo(self, x):
                return 0

            @yoyo.pattern(y=3)
            def yoyo(self, y):
                return 42
        item = Bar()

        self.assertEquals(item.yoyo(1), 0)
        self.assertEquals(item.yoyo(3), 42)
        self.assertRaises(MatchError, lambda: item.yoyo(2))


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

    def test_one_param(self):
        @self.pat
        def that(foo):
            return 1

        self.assertIsNone(self.guard.arg_pos)
        self.assertEquals(that(1), 1)
        self.assertRaises(MatchError, lambda: that(foo=3))  # problem!

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
        self.assertRaises(MatchError, lambda: that(2, foo=1))  # yup, arg_name='foo' will also have arg_pos=0
        self.assertRaises(MatchError, lambda: that(2, 1))  # same issue here
        self.assertRaises(MatchError, lambda: that(foo=2, x=1))


class TestDefPattern(TestCase):
    def test_call1(self):
        @defpattern(x=1)
        def test(x):
            return x

        self.assertEquals(test(1), 1)
        self.assertRaises(MatchError, lambda: test(2))

    def test_stacked_call(self):
        @defpattern(1)
        def test(x):
            return 1

        @test.pattern(x=gt(4))
        def test(x):
            return 2*x

        self.assertEquals(test(1), 1)
        self.assertEquals(test(5), 10)
        self.assertRaises(MatchError, lambda: test(0))

    def test_placeholders(self):
        @defpattern(x=1)
        def foo(x, y):
            return x+y

        @foo.y
        def that(value):
            return value != 0

        self.assertEquals(foo(1, 1), 2)
        self.assertRaises(MatchError, lambda: foo(1, 0))
        self.assertRaises(MatchError, lambda: foo(0, 1))


class TestDefProxy(TestCase):
    def test_name(self):
        def yoyo(x):
            return 1

        proxy = DefProxy(yoyo)
        self.assertEquals(proxy.__name__, 'yoyo')

    def test_get_attr(self):
        class Yo(object):
            x = 1
            y = 2

        proxy = DefProxy(Yo())
        self.assertEquals(proxy.x, 1)
        self.assertEquals(proxy.y, 2)

    def test_call(self):
        class Yo(object):
            def __init__(self):
                self.underlying_func = lambda x: 1
            def validate(self, x):
                return True

        proxy = DefProxy(Yo())
        self.assertEquals(proxy(4), 1)


class TestFunctionProxy(TestCase):
    def test_get_attr(self):
        class Yo(object):
            x = 1
            y = 2
        class MCache(object):
            most_recent = Yo()

            def __getattr__(self, item):
                return getattr(self.most_recent, item)

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
            def validate_instance(self, *args, **kwargs):
                return self.that

        one = VV(lambda x: 2, False)
        two = VV(lambda x: 1)
        proxy = FunctionProxy([one, two])
        self.assertEquals(proxy(1), 1)


class TestGuardedFunction(TestCase):
    def test_unguarded(self):
        def f(x):
            return x
        guard = GuardedFunction(f)

        self.assertEquals(len(guard.arg_guards), 0)
        self.assertEquals(len(guard.kwarg_guards), 0)
        self.assertEquals(guard(1), 1)
        self.assertEquals(guard(x=1), 1)

    def test_one_arg_guard(self):
        def f(x):
            return x
        value = ValueGuard(1, arg_pos=0)
        guard = GuardedFunction(f, [value])

        self.assertIsNone(value.arg_name)
        self.assertEquals(guard(1), f(1))
        self.assertTrue(guard.validate(1))
        self.assertFalse(guard.validate(2))
        self.assertRaises(MatchError, lambda: guard(2))

    def test_one_kw_guard(self):
        def f(x):
            return x
        value = ValueGuard(1, arg_name='x')
        guard = GuardedFunction(f, [], {value.arg_name: value})

        self.assertIsNone(value.arg_pos)
        self.assertEquals(guard(x=1), f(x=1))
        self.assertTrue(guard.validate(x=1))
        self.assertFalse(guard.validate(x=2))
        self.assertRaises(MatchError, lambda: guard(x=2))

    def test_multi_guard(self):
        def f(x, y):
            return x+y
        value1 = ValueGuard(1, arg_name='x', arg_pos=0)
        value2 = ValueGuard(1, arg_name='y', arg_pos=1)
        guard = GuardedFunction(f, [value1, value2], {value1.arg_name: value1, value2.arg_name: value2})

        self.assertEquals(guard(1, 1), f(1, 1))
        self.assertEquals(guard(1, y=1), f(1, y=1))
        self.assertEquals(guard(x=1, y=1), f(x=1, y=1))
        self.assertRaises(MatchError, lambda: guard(2, 1))
        self.assertRaises(MatchError, lambda: guard(1, 2))
        self.assertRaises(MatchError, lambda: guard(1, y=2))
        self.assertRaises(MatchError, lambda: guard(2, y=1))
        self.assertRaises(MatchError, lambda: guard(x=1, y=2))
        self.assertRaises(MatchError, lambda: guard(x=2, y=1))
