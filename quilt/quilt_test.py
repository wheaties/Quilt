from unittest import TestCase
from quilt.decorators import pattern
from quilt.guard import *
from quilt.proxy import FunctionProxy
from quilt.exc import MatchError
import sys

if sys.version_info[0] > 2:
    from quilt.py3.meta import *
else:
    from quilt.py2.meta import *


class ProxyCacheTest(TestCase):
    def test_getattr(self):
        class Foo(object):
            x = 1
            y = 2

        cache = ProxyCache(Foo())
        self.assertEquals(cache.x, 1)

    def test_get(self):
        class Foo(object):
            cache = ProxyCache(1)
        foo = Foo()
        proxy = foo.cache

        self.assertIsInstance(proxy, FunctionProxy)

    def test_get_attr(self):
        class T(object):
            x = 1

        item = T()
        cache = ProxyCache(item)
        self.assertEquals(cache.x, 1)


class ProxyDictTest(TestCase):
    def test_set_guarded(self):
        cache = ProxyDict()
        cache[1] = GuardedFunction(1)
        cache[1] = GuardedFunction(2)

        self.assertEquals(len(cache[1].cache), 2)

    def test_unguarded(self):
        cache = ProxyDict()
        cache[2] = 4
        cache[2] = 5

        self.assertEquals(cache[2], 5)


class FooPattern(Quilt):
    @pattern(lt(0))
    def yo(self, x):
        return x*x

    @pattern(0)
    def yo(self, x):
        return 0

    @pattern(1)
    def yo(self, x):
        return 11

    @pattern(x=2)
    def yo(self, x):
        return -7

    @pattern(gt(2))
    def yo(self, x):
        return x


class QuiltTest(TestCase):
    def setUp(self):
        self.foo = FooPattern()

    def test_pattern1(self):
        self.assertEquals(self.foo.yo(0), 0)

    def test_pattern2(self):
        self.assertEquals(self.foo.yo(-2), 4)

    def test_pattern3(self):
        self.assertEquals(self.foo.yo(3), 3)

    def test_pattern4(self):
        self.assertEquals(self.foo.yo(2), -7)

    def test_pattern5(self):
        self.assertEquals(self.foo.yo(1), 11)


class Experiment(Quilt):
    @pattern(x=0)
    def __init__(self, x):
        self.x = 'equal'

    @pattern(x=lt(0))
    def __init__(self, x):
        self.x = 'lesser'

    @pattern(x=gt(0))
    def __init__(self, x):
        self.x = 'greater'


class TestConstructor(TestCase):
    def test_init(self):
        x = Experiment(-1)

        self.assertEquals(x.x, 'lesser')

    def test_init2(self):
        x = Experiment(x=-1)

        self.assertEquals(x.x, 'lesser')

    def test_init3(self):
        x = Experiment(0)

        self.assertEquals(x.x, 'equal')

    def test_init4(self):
        x = Experiment(x=0)

        self.assertEquals(x.x, 'equal')

    def test_init5(self):
        x = Experiment(1)

        self.assertEquals(x.x, 'greater')

    def test_init6(self):
        x = Experiment(x=1)

        self.assertEquals(x.x, 'greater')


class Place(Quilt):
    def __init__(self, value):
        self.value = value

    @pattern(x=1)
    def foo(self, x, y):
        return x+y

    @foo.y
    def g(self, that):
        return self.value < that

    @pattern(1)
    def bar(self, x, y):
        return x+y

    @bar.y
    def g(self, that):
        return self.value < that

    @pattern(x=lt(1))
    def bar(self, x, y):
        return 0


class PlaceholderTest(TestCase):
    def setUp(self):
        self.that = Place(1)

    def test_one(self):
        self.assertEquals(self.that.foo(1, 2), 3)
        self.assertRaises(MatchError, lambda: self.that.foo(2, 0))
        self.assertRaises(MatchError, lambda: self.that.foo(1, 1))

    def test_stacked(self):
        self.assertEquals(self.that.bar(1, 2), 3)
        self.assertEquals(self.that.bar(0, 4), 0)
        self.assertRaises(MatchError, lambda: self.that.bar(1, 0))