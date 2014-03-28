__author__ = 'Owein'

import unittest
from quilt import *
from pattern import GuardedFunction


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

    def test_get_attr

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