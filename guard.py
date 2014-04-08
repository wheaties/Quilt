__author__ = 'Owein Reese'

import operator


class Guard(object):
    def __init__(self, arg_name=None, arg_pos=None):
        self.arg_name = arg_name
        self.arg_pos = arg_pos

    def and_(self, guard):
        return AndGuard(self, guard)

    def or_(self, guard):
        return OrGuard(self, guard)

    def validate(self, value):
        raise NotImplementedError

    def __str__(self):
        return self.__name__ + '(arg_name=' + str(self.arg_name) + ', arg_pos=' + str(self.arg_pos) + ')'

    def __repr__(self):
        return self.__str__()

    @property
    def __name__(self):
        return 'Guard'

    def validate_object(self, obj):
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


class ReverseGuard(Guard):
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

    def __str__(self):
        return str(self.inner)

    def __repr__(self):
        return 'Reversed' + repr(self.inner)


class AndGuard(Guard):
    def __init__(self, first, second):
        super(AndGuard, self).__init__(first.arg_name or second.arg_name, first.arg_pos or second.arg_pos)
        self.first = first
        self.second = second

    def validate(self, value):
        return self.first.validate(value) and self.second.validate(value)

    @property
    def __name__(self):
        return 'And[' + self.first.__name__ + ',' + self.second.__name__ + ']'

    def __repr__(self):
        return 'And[' + repr(self.first) + ',' + repr(self.second) + ']'


class OrGuard(Guard):
    def __init__(self, first, second):
        super(OrGuard, self).__init__(first.arg_name or second.arg_name, first.arg_pos or second.arg_pos)
        self.first = first
        self.second = second

    def validate(self, value):
        return self.first.validate(value) or self.second.validate(value)

    @property
    def __name__(self):
        return 'Or[' + self.first.__name__ + ',' + self.second.__name__ + ']'

    def __repr__(self):
        return 'Or[' + repr(self.first) + ',' + repr(self.second) + ']'


class OperatorGuard(Guard):
    def __init__(self, op, value, arg_name=None, arg_pos=None):
        super(OperatorGuard, self).__init__(arg_name, arg_pos)
        self.op = op
        self.value = value

    def __repr__(self):
        return self.__name__ + ' operator: ' + repr(type(self.op)) + ' against: ' + repr(self.value)

    def validate(self, value):
        return self.op(value, self.value)


class ValueGuard(Guard):
    def __init__(self, value, arg_name=None, arg_pos=None):
        super(ValueGuard, self).__init__(arg_name, arg_pos)
        self.value = value

    @property
    def __name__(self):
        return 'ValueGuard'

    def __repr__(self):
        return self.__name__ + '[' + repr(self.value) + '](arg_name=' + str(self.arg_name) \
               + ', arg_pos=' + str(self.arg_pos) + ')'

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
    def __init__(self, iterable):
        self.iterable = iterable

    def validate(self, value):
        return value in self.iterable

    @property
    def __name__(self):
        return 'OneOfGuard'

    def __repr__(self):
        return super(OneOfGuard, self).__repr__() + ' containing ' + ','.join(self.iterable)


def one_of(*args):
    if len(args) == 1 and hasattr(args[0], '__iter__'):
        return OneOfGuard(args[0])
    else:
        return OneOfGuard(args)


def not_one_of(*args):
    return ReverseGuard(one_of(*args))


class ContainsGuard(Guard):
    def __init__(self, iterable):
        self.iterable = iterable

    def validate(self, value):
        return all(x in value for x in self.iterable)

    @property
    def __name__(self):
        return 'ContainsGuard'

    def __repr__(self):
        return super(ContainsGuard, self).__repr__() + ' within ' + ','.join(self.iterable)


def contains(*args):
    if len(args) == 1 and hasattr(args[0], '__iter__'):
        return ContainsGuard(args[0])
    else:
        return ContainsGuard(args)


def not_contains(*args):
    return ReverseGuard(contains(*args))


class LengthGuard(Guard):
    def __init__(self, length, op):
        self.length = length
        self.op = op

    def validate(self, value):
        return self.op(len(value), self.length)


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


def close_to(value, epsilon):
    return CloseToGuard(value, epsilon)


class NotNoneGuard(Guard):
    def __init__(self, arg_name=None, arg_pos=None):
        super(NotNoneGuard, self).__init__(arg_name, arg_pos)

    def validate(self, value):
        return value is not None


def not_none():
    return NotNoneGuard()


#TODO: This should be moved to pattern
#TODO: Make the attribute setting actually work in a class! May need new class specific to instance based
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

    def __call__(self, func):
        self.wrapped_func = func


#TODO: This should all live in a class specific area instead of general guards
class HeldGuard(Guard):
    def __init__(self, instance, owner, wrapped_func, arg_name=None, arg_pos=None):
        super(Guard).__init__(arg_name, arg_pos)
        self.instance = instance
        self.owner = owner
        self.wrapped_func = wrapped_func

    def validate(self, value):
        return self.wrapped_func.__get__(self.instance, self.owner)(value)


#TODO: Need to pass in a reference to an instance and a class like in a descriptor!
class PlaceholderDescriptor(object):
    def __init__(self, wrapped_func=None, arg_name=None, arg_pos=None):
        self.wrapped_func = wrapped_func
        self.arg_name = arg_name
        self.arg_pos = arg_pos

    @property
    def __name__(self):
        if self.wrapped_func:
            return 'BoundGuard'
        else:
            return 'UnboundGuard'

    def __get__(self, instance, owner):
        return HeldGuard(instance, owner, self.wrapped_func, self.arg_name, self.arg_pos)

    def __str__(self):
        return self.__name__ + '(arg_name=' + str(self.arg_name) + ', arg_pos=' + str(self.arg_pos) + ')'

    def __repr__(self):
        return self.__name__ + '(arg_name=' + str(self.arg_name) + ', arg_pos=' + str(self.arg_pos) + \
            ', wrapped=' + repr(self.wrapped_func) + ')'

    def __call__(self, func):
        self.wrapped_func = func