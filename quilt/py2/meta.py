from quilt.pattern import Pattern
from quilt.proxy import ProxyCache
from inspect import getargspec, getsource
from ast import NodeTransformer, parse, copy_location, FunctionDef
from random import random


def _mangle_name(guarded):
    old_name = guarded.__name__
    transform = MethodNameTransformer(old_name, '__quilt__' + str(random()))
    source = getsource(guarded)
    code = parse(source, mode='eval')
    modified = transform.visit(code)
    compiled = compile(modified, '<string>', 'eval')
    guard = eval(compiled)

    return guard, old_name


class MemberFunctionPattern(Pattern):
    def __call__(self, func):
        (arg_names, varg_name, kwarg_name, _) = getargspec(func)
        arg_names = arg_names[1:]
        found_names = set()
        found_names.update(self._name_arg_guards(arg_names))
        found_names.update(self._position_kwarg_guards(arg_names))

        renamed_func, old_name = _mangle_name(func)
        guarded = self._create_guarded(arg_names, found_names, renamed_func)
        setattr(guarded, '__oldname__', old_name)

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
        for (attr_name, attr_value) in namespace.items():
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
        self.visited_node = False

    def visit_FunctionDef(self, node):
        if node.id == self.name and self.visited_node:
            self.visited_node = True
            return copy_location(FunctionDef(self.rename, node.args, node.body, node.decorator_list))
        else:
            return node