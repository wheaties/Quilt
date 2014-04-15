from quilt.pattern import Pattern
from quilt.proxy import ProxyCache
from inspect import getargspec
from ast import NodeTransformer, parse, copy_location, FunctionDef
from random import random


def _mangle_name(guarded):
    old_name = guarded.__name__
    transform = MethodNameTransformer(old_name, '__quilt__' + str(random()))
    code = parse(guarded)
    modified = transform.visit(code)
    compiled = compile(modified, '<string>', 'eval')
    guard = eval(compiled)
    setattr(guard, '__oldname__', old_name)

    return guard


class MemberFunctionPattern(Pattern):
    def __init__(self, arg_guards, kwarg_guards):
        super(MemberFunctionPattern, self).__init__(arg_guards, kwarg_guards)

    def __call__(self, func):
        (arg_names, varg_name, kwarg_name, _) = getargspec(func)
        arg_names = arg_names[1:]
        found_names = set()
        found_names.update(self._name_arg_guards(arg_names))
        found_names.update(self._position_kwarg_guards(arg_names))

        func = _mangle_name(func)
        guarded = self._create_guarded(arg_names, found_names, func)
        setattr(guarded, '__oldname__', func.__oldname__)

        return guarded


def _update_proxy(guarded, attributes):
    guarded.__name__ = guarded.__oldname__
    delattr(guarded, '__oldname__')
    if guarded.__name__ in attributes:
        attributes[guarded.__name__].append(guarded)
    else:
        attributes[guarded.__name__] = ProxyCache(guarded)


class QuitMeta(type):
    def __new__(cls, name, bases, namespace):
        updated = dict()
        for (attr_name, attr_value) in namespace:
            if attr_name.startswith('__quilt__'):
                _update_proxy(attr_value, updated)
            else:
                updated[attr_name] = attr_value

        return super(QuitMeta, cls).__new__(cls, name, bases, updated)


class Quilt(object):
    __metaclass__ = QuitMeta


class MethodNameTransformer(NodeTransformer):
    def __init__(self, name, rename):
        self.name = name
        self.rename = rename

    def visit_FunctionDef(self, node):
        if node.id == self.name:
            return copy_location(FunctionDef(self.rename, node.args, node.body, node.decorator_list))
        else:
            return node