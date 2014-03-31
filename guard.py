__author__ = 'Owein Reese'

import operator


class Guard(object):
    def __init__(self, arg_name=None, arg_pos=None):
        self.arg_name = arg_name
        self.arg_pos = arg_pos

    def validate(self, value):
        raise NotImplementedError

    def __str__(self):
        return self.__name__ + '(arg_name=' + str(self.arg_name)  + ', arg_pos=' + str(self.arg_pos) + ')'

    def __neg__(self):
        return ReverseGuard(self)

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
        except (KeyError, TypeError):
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


def equal_to(value):
    return ValueGuard(value)

eq = equal_to


def not_equal_to(value):
    return not ValueGuard(value)

ne = not_equal_to


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


#TODO: Add the following:
# 1. _Length with a length var
# 2. one_of
# 3. contains
# 5. close_to(x, error-bound)