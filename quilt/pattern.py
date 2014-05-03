from .guard import PlaceholderGuard
from .exc import MatchError
from itertools import chain, tee
from inspect import getargspec
from functools import update_wrapper


class Pattern(object):
    """Base callable object responsible for creating GuardedFunction and assigning argument names and argument positions
    to Guards.

    Pattern should not be used on its own. It is designed to be used as a base class with inheriting classes defining
    the scope of useage. Instances of Pattern are designed to be returned from a decorator function/class and used once
    due to the side-effecting nature of the __call__ method.

    :param arg_guards: A sorted list of Guard that have had the arg_pos variable set to something other than None.
    Sorting is by arg_pos.
    :param kwarg_guards: A list of Guard that have had the arg_name variable set to something other than None.
    """

    def __init__(self, arg_guards, kwarg_guards):
        self.arg_guards = arg_guards
        self.kwarg_guards = kwarg_guards

    @property
    def guards(self):
        return chain(self.arg_guards, self.kwarg_guards)

    @property
    def __name__(self):
        return 'Pattern'

    def __str__(self):
        return self.__print__(str)

    def __repr__(self):
        return self.__print__(repr)

    def __print__(self, f):
        return self.__name__ + '(guards=[' + ', '.join(map(f, self.guards)) + '])'

    def __call__(self, func):
        (arg_names, varg_name, kwarg_name, _) = getargspec(func)
        found_names = set()
        found_names.update(self._name_arg_guards(arg_names))
        found_names.update(self._position_kwarg_guards(arg_names))

        return self._create_guarded(arg_names, found_names, func)

    def _name_arg_guards(self, arg_names):
        """Assigns the argument name to the arg_guards list in the order of appearance in the function's argument list.
        """
        names = []
        for (name, guard) in zip(arg_names, self.arg_guards):
            guard.arg_name = name
            names.append(name)

        return names

    def _position_kwarg_guards(self, arg_names):
        """Assigns the argument position to the kwarg_guards as they are found within the function's argument list."""
        names = []
        for guard in self.kwarg_guards:
            if guard.arg_name in arg_names:
                guard.arg_pos = arg_names.index(guard.arg_name)
                names.append(guard.arg_name)

        return names

    def _create_guarded(self, arg_names, found_names, func):
        """Creates the GuardedFunction. For any function argument not found within the arg_guards or kwarg_guards lists
        creates and sets a new PlaceholderGuard on a attribute with matching name."""
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


class GuardedFunction(object):
    """Callable function wrapper. Contains all Guard objects needed to validate the argument list and if successful call
    the wrapped function.

    GuardedFunction can be used on it's own, although it is recommended not to expose
    """
    def __init__(self, underlying_func, arg_guards=None, kwarg_guards=None):
        self.underlying_func = underlying_func
        self.arg_guards = arg_guards or []
        self.kwarg_guards = kwarg_guards or dict()

    @property
    def __class__(self):
        return self.underlying_func.__class__

    def __str__(self):
        return self.__print__(str)

    def __repr__(self):
        return self.__print__(repr)

    def __print__(self, f):
        return 'GuardedFunction(func=' + f(self.underlying_func) + ', guards=[' + ', '.join(map(f, self.guards)) + '])'

    @property
    def guards(self):
        return chain(self.arg_guards, self.kwarg_guards.values())

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