__author__ = 'Owein Reese'

import operator
import re


class Guard(object):
    """Guards are used to test properties of function arguments when pattern matching.

    Guards are a multi-purpose utility employed in several distinct ways within Quilt. As part of a pattern on a def
    defined within a module, Guards validate using either the argument name or the argument position within the argument
    list of the function. As part of a pattern on a def defined within a class, Guards validate using both the instance
    and type of class as well as the argument name or the argument position. When used as part of an argument pattern,
    Guards validate against the named attribute of the argument.

    :param arg_name: the name of the argument, defaults to None
    :param arg_pos: the position of the argument within the argument list, defaults to None
    """

    def __init__(self, arg_name=None, arg_pos=None):
        self.arg_name = arg_name
        self.arg_pos = arg_pos

    def and_(self, guard):
        """Chains this Guard with another producing a Guard that is satisfies if and only if both Guards validate."""
        return AndGuard(self, guard)

    def or_(self, guard):
        """Chains this Guard with another producing a Guard that is satisfied if either Guard validates."""
        return OrGuard(self, guard)

    def validate(self, value):
        """Returns a boolean indicating if the passed in value satisfies the conditions of the Guard.

        All Guards must implement this method as it lacks a default implementation. It is expected that this method not
        raise any exceptions, instead returning a False.
        """
        raise NotImplementedError

    def __str__(self):
        return self.__print__(str)

    def __repr__(self):
        return self.__print__(repr)

    def __print__(self, f):
        return self.__name__ + '(arg_name=' + f(self.arg_name) + ', arg_pos=' + f(self.arg_pos) + ')'

    @property
    def __name__(self):
        return 'Guard'

    def validate_object(self, obj):
        """Returns a boolean indicating if the named attribute of the passed in object satisfied the conditions of the
        Guard."""
        try:
            attr = getattr(obj, self.arg_name)

            return self.validate(attr)
        except (AttributeError, TypeError):
            return False

    def validate_iterable(self, it):
        try:
            value = it[self.arg_pos]

            return self.validate(value)
        except (KeyError, IndexError, TypeError):
            return False

    def validate_instance(self, value, instance=None, owner=None):
        """Validates the passed in value using the instance and class of the parent object."""
        return self.validate(value)


class ReverseGuard(Guard):
    """A Guard that invalidates the opposite of all values that the wrapped Guard would validate.

    The arg_name and arg_pos parameters are assigned the same values as the wrapped Guard. Disguises itself as the
    wrapped Guard, passing attribute access and assignment transparently between the two.

    :param guard: A Guard
    """

    def __init__(self, guard):
        super(ReverseGuard, self).__init__(guard.arg_name, guard.arg_pos)
        self.inner = guard

    def validate(self, value):
        return not self.inner.validate(value)

    @property
    def __class__(self):
        return self.inner.__class__

    @property
    def __name__(self):
        return self.inner.__name__

    def __print__(self, f):
        return 'Reversed' + f(self.inner)

    def __getattr__(self, item):
        return getattr(self.inner, item)

    def __setattr__(self, key, value):
        return setattr(self.inner, key, value)


class AndGuard(Guard):
    """A Guard that validates if and only if both contained Guards validate the supplied value.

    The arg_name and arg_pos are inherited from the contained Guards. If they disagree in value, the first guard takes
    precedence.

    :param first: The first contained Guard
    :param second: The second contained Guard
    """

    def __init__(self, first, second):
        super(AndGuard, self).__init__(first.arg_name or second.arg_name, first.arg_pos or second.arg_pos)
        self.first = first
        self.second = second

    def validate(self, value):
        return self.first.validate(value) and self.second.validate(value)

    @property
    def __name__(self):
        return 'And[' + self.first.__name__ + ',' + self.second.__name__ + ']'

    def __print__(self, f):
        return 'And[' + f(self.first) + ', ' + f(self.second) + '](arg_name=' + f(self.arg_name) + ', arg_pos=' + \
            f(self.arg_pos) + ')'


class OrGuard(Guard):
    """A Guard that validates if either contained Guards validate the supplied value.

    The arg_name and arg_pos are inherited from the contained Guards. If they disagree in value, the first guard takes
    precedence.

    :param first: The first contained Guard
    :param second: The second contained Guard
    """

    def __init__(self, first, second):
        super(OrGuard, self).__init__(first.arg_name or second.arg_name, first.arg_pos or second.arg_pos)
        self.first = first
        self.second = second

    def validate(self, value):
        return self.first.validate(value) or self.second.validate(value)

    @property
    def __name__(self):
        return 'Or[' + self.first.__name__ + ',' + self.second.__name__ + ']'

    def __print__(self, f):
        return 'Or[' + f(self.first) + ', ' + f(self.second) + '](arg_name=' + f(self.arg_name) + ', arg_pos=' + \
            f(self.arg_pos) + ')'


class OperatorGuard(Guard):
    """A Guard that validates a supplied value against a predetermined value using the supplied 2 parameter predicate,
    generally one of the operator module's functions: lt, gt, etc.

    :param op: The operator to use in comparing the two values. Must return a boolean value.
    :param value: The supplied value for comparison
    :param arg_name: the name of the argument, defaults to None
    :param arg_pos: the position of the argument within the argument list, defaults to None
    """

    def __init__(self, op, value, arg_name=None, arg_pos=None):
        super(OperatorGuard, self).__init__(arg_name, arg_pos)
        self.op = op
        self.value = value

    def __print__(self, f):
        return self.__name__ + '(op=' + f(self.op) + ', value=' + f(self.value) + ', arg_name=' + f(self.arg_name) + \
            ', arg_pos=' + f(self.arg_pos) + ')'

    def validate(self, value):
        return self.op(value, self.value)


class ValueGuard(Guard):
    """A Guard that validates if the supplied value is the same as that of the Guard.

    :param value: The supplied valud to validate against.
    :param arg_name: the name of the argument, defaults to None
    :param arg_pos: the position of the argument within the argument list, defaults to None
    """

    def __init__(self, value, arg_name=None, arg_pos=None):
        super(ValueGuard, self).__init__(arg_name, arg_pos)
        self.value = value

    @property
    def __name__(self):
        return 'ValueGuard'

    def __print__(self, f):
        return self.__name__ + '(value=' + f(self.value) + ', arg_name=' + f(self.arg_name) + ', arg_pos=' + \
            f(self.arg_pos) + ')'

    def validate(self, value):
        return self.value == value


def less_than(value):
    return OperatorGuard(operator.lt, value)


lt = less_than


def less_than_or_equal(value):
    return OperatorGuard(operator.le, value)


le = less_than_or_equal
lte = le


def greater_than(value):
    return OperatorGuard(operator.gt, value)


gt = greater_than


def greater_than_or_equal(value):
    return OperatorGuard(operator.ge, value)


ge = greater_than_or_equal
gte = ge
not_less_than = greater_than_or_equal
not_greater_than = less_than_or_equal


def equal_to(value):
    return ValueGuard(value)


eq = equal_to


def not_equal_to(value):
    return ReverseGuard(equal_to(value))


ne = not_equal_to


class OneOfGuard(Guard):
    """A Guard that validates by checking for inclusion within user supplied set of values.

    :param iterable: A list, set, dict or some other iterable set that can be traversed multiple times.
    :param arg_name: the name of the argument, defaults to None
    :param arg_pos: the position of the argument within the argument list, defaults to None
    """

    def __init__(self, iterable, arg_name=None, arg_pos=None):
        super(OneOfGuard, self).__init__(arg_name, arg_pos)
        self.iterable = iterable

    def validate(self, value):
        return value in self.iterable

    @property
    def __name__(self):
        return 'OneOfGuard'

    def __print__(self, f):
        return self.__name__ + '(values=[' + ', '.join(map(f, self.iterable)) + '], arg_name=' + f(self.arg_name) + \
            ', arg_pos=' + f(self.arg_pos) + ')'


def one_of(*args):
    if len(args) == 1 and hasattr(args[0], '__iter__'):
        return OneOfGuard(args[0])
    else:
        return OneOfGuard(args)


def not_one_of(*args):
    return ReverseGuard(one_of(*args))


class ContainsGuard(Guard):
    """A Guard that validates a given iterable contains all of the supplied collection.

    :param iterable: A list, set, dict or some other iterable set that can be traversed multiple times.
    :param arg_name: the name of the argument, defaults to None
    :param arg_pos: the position of the argument within the argument list, defaults to None
    """

    def __init__(self, iterable, arg_name=None, arg_pos=None):
        super(ContainsGuard, self).__init__(arg_name, arg_pos)
        self.iterable = iterable

    def validate(self, value):
        return all(x in value for x in self.iterable)

    @property
    def __name__(self):
        return 'ContainsGuard'

    def __print__(self, f):
        return self.__name__ + '(values=[' + ', '.join(map(f, self.iterable)) + '], arg_name=' + f(self.arg_name) + \
            ', arg_pos=' + f(self.arg_pos) + ')'


class ContainsNOfGuard(Guard):
    """A Guard that validates a given iterable contains N of the supplied collection.

    :param iterable: A list, set or some other iterable collection that can be traversed multiple times.
    :param arg_name: the name of the argument, defaults to None
    :param arg_pos: the position of the argument within the argument list, defaults to None
    """

    def __init__(self, iterable, number, arg_name=None, arg_pos=None):
        super(ContainsNOfGuard, self).__init__(arg_name, arg_pos)
        self.iterable = iterable
        self.number = number

    def validate(self, value):
        count = 0
        for x in self.iterable:
            if x in value:
                count += 1
            if count == self.number:
                return True

        return False

    @property
    def __name__(self):
        return 'ContainsNOfGuard'

    def __print__(self, f):
        return self.__name__ + '(values=[' + ', '.join(map(f, self.iterable)) + '], arg_name=' + f(self.arg_name) + \
            ', arg_pos=' + f(self.arg_pos) + ')'


def contains(*args):
    if len(args) == 1 and hasattr(args[0], '__iter__'):
        return ContainsGuard(args[0])
    else:
        return ContainsGuard(args)


def not_contains(*args):
    return ReverseGuard(contains(*args))


class LengthGuard(Guard):
    def __init__(self, length, op, arg_name=None, arg_pos=None):
        super(LengthGuard, self).__init__(arg_name, arg_pos)
        self.length = length
        self.op = op

    def validate(self, value):
        return self.op(len(value), self.length)

    @property
    def __name__(self):
        return 'LengthGuard'

    def __print__(self, f):
        return self.__name__ + '(length=' + f(self.length) + ', op=' + f(self.op) + ', arg_name=' + f(self.arg_name) + \
            ', arg_pos=' + f(self.arg_pos) + ')'


def has_length(x):
    return LengthGuard(x, operator.eq)


def longer_than(x):
    return LengthGuard(x, operator.gt)


def shorter_than(x):
    return LengthGuard(x, operator.lt)


def not_longer_than(x):
    return LengthGuard(x, operator.le)


def not_shorter_than(x):
    return LengthGuard(x, operator.ge)


def not_empty():
    return longer_than(0)


class TypeOfGuard(Guard):
    def __init__(self, obj_type, arg_name=None, arg_pos=None):
        super(TypeOfGuard, self).__init__(arg_name, arg_pos)
        self.obj_type = obj_type

    @property
    def __name__(self):
        return 'TypeOf[' + str(self.obj_type) + ']'

    def validate(self, value):
        return isinstance(value, self.obj_type)


def type_of(obj_type):
    return TypeOfGuard(obj_type)


class CloseToGuard(Guard):
    def __init__(self, value, epsilon, arg_name=None, arg_pos=None):
        super(CloseToGuard, self).__init__(arg_name, arg_pos)
        self.value = value
        self.epsilon = epsilon

    def validate(self, value):
        return (self.value - self.epsilon) < value < (self.value + self.epsilon)

    @property
    def __name__(self):
        return 'CloseToGuard'

    def __print__(self, f):
        return self.__name__ + '(value=' + f(self.value) + ', epsilon=' + f(self.epsilon) + ', arg_name=' + \
            f(self.arg_name) + ', arg_pos=' + f(self.arg_pos) + ')'


def close_to(value, epsilon):
    return CloseToGuard(value, epsilon)


class NotNoneGuard(Guard):
    def __init__(self, arg_name=None, arg_pos=None):
        super(NotNoneGuard, self).__init__(arg_name, arg_pos)

    def validate(self, value):
        return value is not None

    @property
    def __name__(self):
        return 'NotNoneGuard'


def not_none():
    return NotNoneGuard()


class RegexGuard(Guard):
    def __init__(self, phrase, flag=0, arg_name=None, arg_pos=None):
        super(RegexGuard, self).__init__(arg_name, arg_pos)
        self.regex = re.compile(phrase, flag)
        self.phrase = phrase

    @property
    def __name__(self):
        return 'RegexGuard[' + self.phrase + ']'

    def validate(self, value):
        return self.regex.search(value) is not None


def regex(phrase, flag=0):
    return RegexGuard(phrase, flag)


class PlaceholderGuard(Guard):
    def __init__(self, wrapped_func=None, arg_name=None, arg_pos=None):
        super(PlaceholderGuard, self).__init__(arg_name, arg_pos)
        self.wrapped_func = wrapped_func

    @property
    def __name__(self):
        if self.wrapped_func:
            return 'BoundGuard'
        else:
            return 'UnboundGuard'

    def validate(self, value):
        if self.wrapped_func:
            return self.wrapped_func(value)
        else:
            return True

    def validate_instance(self, value, instance=None, owner=None):
        if self.wrapped_func:
            return self.wrapped_func.__get__(instance, owner)(value)
        else:
            return True

    def __call__(self, func):
        self.wrapped_func = func