__author__ = 'Owein'

from guard import Guard, ValueGuard, PlaceholderGuard
from exc import *
from itertools import chain, tee
from inspect import getargspec
from functools import update_wrapper
from collections import defaultdict
from importlib import import_module


def _guard_type(guard):
    if isinstance(guard, Guard):
        return guard
    else:
        return ValueGuard(guard)


def _arg_pattern(args):
    arg_guards = []
    for i, guard in enumerate(args):
        guarded = _guard_type(guard)
        guarded.arg_pos = i
        arg_guards.append(guarded)

    return arg_guards


def _kwarg_pattern(kwargs):
    kwarg_guards = []
    for kw, guard in kwargs.items():
        guarded = _guard_type(guard)
        guarded.arg_name = kw
        kwarg_guards.append(guarded)

    return kwarg_guards


def matches(**kwargs):
    kw_guards = _kwarg_pattern(**kwargs)

    return MatchesGuard(kw_guards)


#TODO: Move to guard.py
class MatchesGuard(Guard):
    def __init__(self, kwarg_guards, arg_name=None, arg_pos=None):
        super(MatchesGuard, self).__init__(arg_name, arg_pos)
        self.guards = kwarg_guards

    def validate(self, value):
        return all(guard.validate_object(value) for guard in self.guards)

    @property
    def __name__(self):
        return 'MatchesGuard'

    def __print__(self, f):
        return self.__name__ + '(guards=[' + ', '.join(map(f, self.guards)) + '], arg_name=' + f(self.arg_name) + \
            ', arg_pos=' + f(self.arg_pos) + ')'


#TODO: Split this into Pattern and Matches(Guard)
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

    @property
    def __name__(self):
        return 'Pattern'

    def __call__(self, func):
        (arg_names, varg_name, kwarg_name, _) = getargspec(func) # This returns the self argument as well as the others!
        found_names = set()
        found_names.update(self._name_arg_guards(arg_names))
        found_names.update(self._position_kwarg_guards(arg_names))

        return self._create_guarded(arg_names, found_names, func)

    def _name_arg_guards(self, arg_names):
        names = []
        for (name, guard) in zip(arg_names, self.arg_guards):
            guard.arg_name = name
            names.append(name)

        return names

    def _position_kwarg_guards(self, arg_names):
        names = []
        for guard in self.kwarg_guards:
            if guard.arg_name in arg_names:
                guard.arg_pos = arg_names.index(guard.arg_name)
                names.append(guard.arg_name)

        return names

    def _create_guarded(self, arg_names, found_names, func):
        guarded = GuardedFunction(func)
        held_guards = []
        for i, name in enumerate(arg_names):
            if name not in found_names:
                holder = PlaceholderGuard(arg_name=name, arg_pos=i)
                setattr(guarded, name, holder)
                held_guards.append(holder)

        (arg, kw) = tee(chain(self.arg_guards, self.kwarg_guards, held_guards))
        guarded.arg_guards = sorted((x for x in arg if x.arg_pos is not None), key=lambda x: x.arg_pos)
        guarded.kwarg_guards = dict((g.arg_name, g) for g in kw if g.arg_name is not None)
        update_wrapper(guarded, func)

        return guarded


def defpattern(*args, **kwargs):
    arg_guards = _arg_pattern(args)
    kwarg_guards = _kwarg_pattern(kwargs)

    return FuncPattern(arg_guards, kwarg_guards)


def _register_proxy(func, guarded):
    module = import_module(func.__module__)
    if not hasattr(module, '__quilt__'):
        setattr(module, '__quilt__', defaultdict(list))
    module_func_reg = module.__quilt__[func.__name__]
    module_func_reg.append(guarded)

    return DefProxy(module_func_reg, guarded)


class FuncPattern(Pattern):
    def __init__(self, arg_guards, kwarg_guards):
        super(FuncPattern, self).__init__(arg_guards, kwarg_guards)

    def __call__(self, func):
        guarded = super(FuncPattern, self).__call__(func)
        return _register_proxy(func, guarded)


def pattern(*args, **kwargs):
    arg_guards = _arg_pattern(args)
    kwarg_guards = _kwarg_pattern(kwargs)

    return MemberFunctionPattern(arg_guards, kwarg_guards)


class MemberFunctionPattern(Pattern):
    def __init__(self, arg_guards, kwarg_guards):
        super(MemberFunctionPattern, self).__init__(arg_guards, kwarg_guards)

    def __call__(self, func):
        (arg_names, varg_name, kwarg_name, _) = getargspec(func)
        arg_names = arg_names[1:]
        found_names = set()
        found_names.update(self._name_arg_guards(arg_names))
        found_names.update(self._position_kwarg_guards(arg_names))

        #This is not correctly lableling arg_pos and arg_name if it can be deduced from arg_names!
        return self._create_guarded(arg_names, found_names, func)


class GuardedFunction(object):
    def __init__(self, underlying_func, arg_guards=None, kwarg_guards=None):
        self.underlying_func = underlying_func
        self.arg_guards = arg_guards or []
        self.kwarg_guards = kwarg_guards or dict()

    @property
    def __class__(self):
        return self.underlying_func.__class__

    def __str__(self):
        return str(self.underlying_func)

    def __repr__(self):
        return repr(self.underlying_func) + ' guarded by ' + ','.join(map(repr, self.guards))

    @property
    def guards(self):
        return chain(self.arg_guards, self.kwarg_guards)

    def validate(self, *args, **kwargs):
        return all(guard.validate(value) for value, guard in zip(args, self.arg_guards)) and \
            all(guard.validate(kwargs[kw]) for kw, guard in self.kwarg_guards.items() if kw in kwargs)

    def validate_instance(self, instance=None, owner=None, *args, **kwargs):
        return all(guard.validate_instance(value, instance, owner) for value, guard in zip(args, self.arg_guards)) and \
            all(guard.validate_instance(kwargs[kw], instance, owner) for kw, guard in self.kwarg_guards.items()
                if kw in kwargs)

    def __call__(self, *args, **kwargs):
        if self.validate(*args, **kwargs):
            return self.underlying_func(*args, **kwargs)
        raise MatchError(*args, **kwargs)


#TODO: move this to another package.
class FunctionProxy(object):
    def __init__(self, proxy_cache, instance=None, owner=None):
        self.proxy_cache = proxy_cache
        self.instance = instance
        self.owner = owner

    def __getattr__(self, item):
        return getattr(self.proxy_cache, item)

    def __str__(self):
        return self.__print__(str)

    def __repr__(self):
        return self.__print__(repr)

    def __print__(self, f):
        return 'FunctionProxy(' + ', '.join(map(f, self.proxy_cache)) + ')'

    def __call__(self, *args, **kwargs):
        for guarded_func in self.proxy_cache:
            if guarded_func.validate_instance(self.instance, self.owner, *args, **kwargs):
                return guarded_func.underlying_func.__get__(self.instance, self.owner)(*args, **kwargs)
        raise MatchError(*args, **kwargs)


class DefProxy(object):
    def __init__(self, proxy_cache, most_recent):
        self.proxy_cache = proxy_cache
        self.most_recent = most_recent

    @property
    def __name__(self):
        return self.most_recent.__name__

    @property
    def __module__(self):
        return self.most_recent.__module__

    @property
    def __closure__(self):
        return None

    @property
    def __globals__(self):
        return self.most_recent.__globals__

    def __getattr__(self, item):
        return getattr(self.most_recent, item)

    def __str__(self):
        return self.__print__(str)

    def __repr__(self):
        return self.__print__(repr)

    def __print__(self, f):
        return 'DefProxy(' + ''.join(map(f, self.proxy_cache)) + ')'

    def __call__(self, *args, **kwargs):
        for guarded_func in self.proxy_cache:
            if guarded_func.validate(*args, **kwargs):
                return guarded_func.underlying_func(*args, **kwargs)
        raise MatchError(*args, **kwargs)