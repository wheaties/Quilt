__author__ = 'Owein Reese'

from guard import Guard, ValueGuard, PlaceholderGuard
from itertools import chain
from inspect import getargspec
from functools import update_wrapper
from types import MethodType


def _guard_type(guard):
    if type(Guard) == type(guard):
        return guard
    else:
        return ValueGuard(guard)


def pattern(*args, **kwargs):
    arg_guards = []
    for i, guard in enumerate(args):
        guarded = _guard_type(guard)
        guarded.arg_pos = i
        arg_guards.append(guarded)

    kwarg_guards = []
    for kw, guard in kwargs:
        guarded = _guard_type(guard)
        guarded.arg_name = kw
        kwarg_guards.append(guarded)

    return Pattern(arg_guards, kwarg_guards)


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

        guarded = GuardedFunction(func)
        held_guards = []
        for i, name in enumerate(arg_names):
            if name not in found_names:
                holder = PlaceholderGuard(arg_name=name, arg_pos=i)
                setattr(guarded, name, holder)
                held_guards.append(holder)

        guarded.arg_guards = sorted(chain(self.arg_guards, self.kwarg_guards, held_guards), 'arg_pos')
        guarded.kwarg_guards = {(g.arg_name, g) for g in chain(self.arg_guards, self.kwarg_guards, held_guards)}
        update_wrapper(guarded, func)
        cache = ProxyCache(guarded)

        return cache


class GuardedFunction(object):
    def __init__(self, underlying_func, arg_guards=None, kwarg_guards=None):
        self.underlying_func = underlying_func
        self.arg_guards = arg_guards or []
        self.kwarg_guards = kwarg_guards or {}

    @property
    def __class__(self):
        return self.underlying_func.__class__

    def __str__(self):
        return str(self.underlying_func)

    def __repr__(self):
        return repr(self.underlying_func)

    def validate(self, *args, **kwargs):
        return all(guard.validate(arg) for (arg, guard) in zip(args, self.arg_guards)) and \
            all(self.kwarg_guards[kw].validate(arg) for (kw, arg) in kwargs if kw in self.kwarg_guards)


class ProxyCache(object):
    def __init__(self, initial_func):
        self.cache = [initial_func]
        self.most_recent = initial_func

    def __getattr__(self, item):
        return getattr(self.most_recent, item)

    def __get__(self, instance=None, owner=None):
        return FunctionProxy(self, instance, owner)

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

    def __str__(self):
        return 'FunctionProxy' + str(self.proxy_cache.cache)

    def __repr__(self):
        return 'FunctionProxy' + repr(self.proxy_cache.cache)

    def __call__(self, *args, **kwargs):
        for guarded_func in self.proxy_cache.cache:
            if guarded_func.validate(*args, **kwargs):
                return guarded_func.underlying_func.__get__(self.instance, self.owner)(*args, **kwargs)
        raise TypeError('Better error message')


#Test code for the console
class Foo(object):
    @pattern(3)
    def yo(self, x):
        return x

    @pattern(1)
    def la(self, x):
        return 2

    @pattern(2)
    def la(self, x):
        return 4

    #@pattern()
    #def la(self, x):
    #    return -1

    #@la.x
    #def mesa(self, x):
    #    return x > 0


@pattern(1)
def bar(x):
    return 14

@pattern(2)
def bar(y):
    return 3


a = Foo()
def that(x):
    try:
        print(a.la(x))
    except Exception as ex:
        print(x, ex)

class Fake:
    cache = 1

class Exp(object):
    la = FunctionProxy(Fake())


bb = Exp()
print(bb.la)
print('bb', dir(bb.la))

that(1)
that(2)
that(3)
that(-1)
print(a.la)
print(bar)
#print('bar', bar(1))
#print('bar', bar(2))