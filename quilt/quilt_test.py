from unittest import TestCase
from quilt.guard import *
from quilt.proxy import *
from quilt.exc import MatchError


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


class FooPattern(object):
    @pattern(lt(0))
    def yo(self, x):
        return x*x

    @yo.pattern(0)
    def yo(self, x):
        return 0

    @yo.pattern(1)
    def yo(self, x):
        return 11

    @yo.pattern(x=2)
    def yo(self, x):
        return -7

    @yo.pattern(gt(2))
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


class Experiment(object):
    @pattern(x=0)
    def __init__(self, x):
        self.x = 'equal'

    @__init__.pattern(x=lt(0))
    def __init__(self, x):
        self.x = 'lesser'

    @__init__.pattern(x=gt(0))
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


class Place(object):
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

    @bar.pattern(x=lt(1))
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