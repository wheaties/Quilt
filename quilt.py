__author__ = 'Owein Reese'

from pattern import GuardedFunction, ProxyCache


class ProxyDict(dict):
    def __setitem__(self, key, value):
        if key in self:
            self[key] = value #isn't this just infinitely recursive?
        elif isinstance(value, GuardedFunction):
            self[key] = ProxyCache(value)
        else:
            self[key] = value


class QuiltType(type):
    @classmethod #or should be @staticmethod?
    def __prepare__(cls, *args, **kwargs):
        return ProxyDict()

    def __new__(cls, name, bases):
        super(QuiltType).__new__(cls, name, bases, {})


class Quilt(metaclass=QuiltType):
    pass