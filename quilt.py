__author__ = 'Owein Reese'

from pattern import GuardedFunction, FunctionProxy


class ProxyCache(object):
    def __init__(self, initial_func):
        self.cache = [initial_func]
        self.most_recent = initial_func

    def __getattr__(self, item):
        return getattr(self.most_recent, item)

    def __get__(self, instance=None, owner=None):
        return FunctionProxy(self, instance, owner)

    def append(self, value):
        self.cache.append(value)
        self.most_recent = value


class ProxyDict(dict):
    def __setitem__(self, key, value):
        if isinstance(value, GuardedFunction):
            if key not in self:
                super(ProxyDict, self).__setitem__(key, ProxyCache(value))
            else:
                self[key].append(value)
        else:
            super(ProxyDict, self).__setitem__(key, value)


class QuiltType(type):
    @classmethod  # or should be @staticmethod?
    def __prepare__(cls, *args, **kwargs):
        return ProxyDict()

    def __new__(cls, name, bases, namespace):
        return type.__new__(cls, name, bases, dict(namespace))


class Quilt(metaclass=QuiltType):
    pass