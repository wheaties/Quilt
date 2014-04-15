from quilt.proxy import ProxyCache
from quilt.pattern import GuardedFunction, Pattern
from inspect import getargspec


class MemberFunctionPattern(Pattern):
    def __init__(self, arg_guards, kwarg_guards):
        super(MemberFunctionPattern, self).__init__(arg_guards, kwarg_guards)

    def __call__(self, func):
        (arg_names, varg_name, kwarg_name, _) = getargspec(func)
        arg_names = arg_names[1:]
        found_names = set()
        found_names.update(self._name_arg_guards(arg_names))
        found_names.update(self._position_kwarg_guards(arg_names))

        return self._create_guarded(arg_names, found_names, func)


class ProxyDict(dict):
    def __setitem__(self, key, value):
        if isinstance(value, GuardedFunction):
            if key not in self:
                super(ProxyDict, self).__setitem__(key, ProxyCache(value))
            else:
                self[key].append(value)
        else:
            super(ProxyDict, self).__setitem__(key, value)


class QuiltMeta(type):
    @classmethod
    def __prepare__(cls, *args, **kwargs):
        return ProxyDict()

    def __new__(cls, name, bases, namespace):
        return type.__new__(cls, name, bases, dict(namespace))


class Quilt(metaclass=QuiltMeta):
    pass