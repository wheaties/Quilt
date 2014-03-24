__author__ = 'Owein Reese'

from guard import Guard, ValueGuard, PlaceholderGuard
from itertools import chain
from inspect import getargspec
from functools import update_wrapper

def _guard_type(guard):
    if type(Guard) == type(guard):
        return guard
    else:
        return ValueGuard(guard)


def pattern(*args, **kwargs):
    pass


class Pattern(Guard):
    def __init__(self, arg_guards, kwarg_guards, arg_name=None, arg_pos=None):
        super(Pattern, self).__init__(arg_name, arg_pos)
        self.arg_guards = arg_guards
        self.kwarg_guards = kwarg_guards

    @property
    def guards(self):
        return chain(self.arg_guards, self.kwarg_guards)

    def validate(self, value):
        return all(guard.validate_object(value) for guard in self.guards)

    def __call__(self, func):
        (arg_names, varg_name, kwarg_name, _) = getargspec(func)
        found_names = set()
        for (name, guard) in zip(arg_names, self.arg_guards):
            guard.arg_name = name
            found_names.add(name)

        for guard in self.kwarg_guards:
            if guard.arg_name in arg_names:
                guard.arg_pos = arg_names.index(guard.arg_name)
                found_names.add(guard.arg_name)

        guarded = GuardedFunction(self.arg_guards, self.kwarg_guards, func)
        for i, name in enumerate(arg_names):
            if name not in found_names:
                holder = PlaceholderGuard(arg_name=name, arg_pos=i)
                setattr(guard, name, holder)

        cache = ProxyCache(guarded)
        update_wrapper(guarded, func) #TODO: which one again?
        update_wrapper(cache, func)

        return cache


class GuardedFunction(object):
    def __init__(self, arg_guard, kwarg_guards, underlying_func):
        self.arg_guards = sorted(chain(arg_guard, kwarg_guards), 'arg_pos')
        self.kwarg_guards = {(g.arg_name, g) for g in chain(arg_guard, kwarg_guards) if g.arg_name}
        self.underlying_func = underlying_func

    @property
    def __class__(self):
        return self.underlying_func.__class__

    def __str__(self):
        return str(self.underlying_func)

    def validate(self, *args, **kwargs):
        return all(guard.validate(arg) for (arg, guard) in zip(args, self.arg_guards)) and \
            all(self.kwarg_guards[kw].validate(arg) for (kw, arg) in kwargs) #TODO: bug in here, not all kw have guards!


class ProxyCache(object):
    def __init__(self, initial_func):
        self.cache = [initial_func]
        self.most_recent = initial_func

    def __get__(self, instance=None, owner=None):
        return FunctionProxy(self, instance, owner)

    def __getattr__(self, item):
        return getargspec(self.most_recent, item)

    def __set__(self, instance, value):
        self.cache.append(value)
        self.most_recent = value


class FunctionProxy(object):
    def __init__(self, proxy_cache, instance=None, owner=None):
        self.proxy_cache = proxy_cache
        self.instance = instance
        self.owner = owner

    def __getattr__(self, item):
        if item != '__call__':
            return getattr(self.proxy_cache.most_recent, item)
        else:
            return self.__call__

    def __call__(self, *args, **kwargs):
        for guarded_func in self.proxy_cache.cache:
            if guarded_func.validate(*args, **kwargs):
                return guarded_func.underlying_func.__get__(self.instance, self.owner)(*args, **kwargs)
        raise TypeError('Better error message')