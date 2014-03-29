__author__ = 'Owein'

import unittest
from quilt import *
from pattern import GuardedFunction, pattern, class_pattern
from guard import guard


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
            @class_pattern(guard < 0)
            def yo(self, x):
                return x*x

            @class_pattern(guard == 0)
            def yo(self, x):
                return 0

            @class_pattern(1)
            def yo(self, x):
                return 11

            @class_pattern(x=2)
            def yo(self, x):
                return -7

            @class_pattern(guard > 2)
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