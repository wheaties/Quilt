from quilt.guard import Guard, ValueGuard, PatternGuard
from quilt.pattern import FuncPattern
import sys


if sys.version_info[0] > 2:
    from quilt.py3.meta import MemberFunctionPattern
else:
    raise Exception('Sorry, python2 support has yet to be finished')
    #from quilt.py2.meta import MemberFunctionPattern


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

    return PatternGuard(kw_guards)


def defpattern(*args, **kwargs):
    arg_guards = _arg_pattern(args)
    kwarg_guards = _kwarg_pattern(kwargs)

    return FuncPattern(arg_guards, kwarg_guards)


def pattern(*args, **kwargs):
    arg_guards = _arg_pattern(args)
    kwarg_guards = _kwarg_pattern(kwargs)

    return MemberFunctionPattern(arg_guards, kwarg_guards)
