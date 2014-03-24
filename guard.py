__author__ = 'Owein Reese'

import operator


class Guard(object):
    def __init__(self, arg_name=None, arg_pos=None):
        self.arg_name = arg_name
        self.arg_pos = arg_pos

    def validate(self, value):
        return True

    def validate_object(self, obj):
        try:
            attr = getattr(obj, self.arg_name)

            return self.validate(attr)
        except (AttributeError, TypeError):
            return False


class OperatorGuard(Guard):
    def __init__(self, op, value, arg_name=None, arg_pos=None):
        super(OperatorGuard, self).__init__(arg_name, arg_pos)
        self.op = op
        self.value = value

    def validate(self, value):
        return self.op(value, self.value)


class ValueGuard(Guard):
    def __init__(self, value, arg_name=None, arg_pos=None):
        super(ValueGuard, self).__init__(arg_name, arg_pos)
        self.value = value

    def validate(self, value):
        return self.value == value


class ConditionalGuard(Guard):
    '''
    Guard is used to constrain an argument such that we can declare it to satisfy a condition:
      @pattern(guard < 1)
    or in the case where we already have a pattern
    '''

    def __init__(self, arg_name=None, arg_pos=None):
        super(ConditionalGuard, self).__init__(arg_name, arg_pos)
        self.checks = []

    def __le__(self, other):
        self.checks.append(OperatorGuard(operator.le, other))
        return self

    def __lt__(self, other):
        self.checks.append(OperatorGuard(operator.lt, other))
        return self

    def __ge__(self, other):
        self.checks.append(OperatorGuard(operator.ge, other))
        return self

    def __gt__(self, other):
        self.checks.append(OperatorGuard(operator.gt, other))
        return self

    def validate(self, value):
        return all(check.validate(value) for check in self.checks)


class _Guard(object):
    def __le__(self, other):
        return ConditionalGuard() <= other

    def __lt__(self, other):
        return ConditionalGuard() < other

    def __ge__(self, other):
        return ConditionalGuard() >= other

    def __gt__(self, other):
        return ConditionalGuard() > other

    def __eq__(self, other):
        return ValueGuard(other)


guard = _Guard()


class PlaceholderGuard(Guard):
    def __init__(self, wrapped_func=None, arg_name=None, arg_pos=None):
        super(PlaceholderGuard, self).__init__(arg_name, arg_pos)
        self.wrapped_func = wrapped_func

    def validate(self, value):
        if self.wrapped_func:
            return self.wrapped_func(value)
        else:
            return True

    def __call__(self, func):
        self.wrapped_func = func