__author__ = 'Owein'

import unittest
from quilt import *
from pattern import GuardedFunction, pattern
from guard import *


class ProxyCacheTest(unittest.TestCase):
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


class ProxyDictTest(unittest.TestCase):
    def test_setguarded(self):
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


class QuiltTest(unittest.TestCase):
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


class TestConstructor(unittest.TestCase):
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