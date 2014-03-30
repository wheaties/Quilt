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

    @property
    def __name__(self):
        return 'Guard'

    def __and__(self, other):
        return AndGuard(self, other)

    def __or__(self, other):
        return OrGuard(self, other)

    def validate_object(self, obj):
        try:
            attr = getattr(obj, self.arg_name)

            return self.validate(attr)
        except (AttributeError, TypeError):
            return False


class CompoundGuard(Guard):
    def __init__(self, primary, secondary):
        super(ConditionalGuard, self).__init__(primary.arg_name or secondary.arg_name, primary.arg_pos or secondary.arg_pos)
        self.primary = primary
        self.secondary = secondary

    @property
    def __name__(self):
        return 'And[' + self.primary.__name__ + ', ' + self.secondary.__name__ + ']'


class AndGuard(CompoundGuard):
    def __init__(self, primary, secondary):
        super(AndGuard, self).__init__(primary, secondary)

    def validate(self, value):
        return self.primary.validate(value) and self.secondary.validate(value)


class OrGuard(CompoundGuard):
    def __init__(self, primary, secondary):
        super(OrGuard, self).__init__(primary, secondary)

    def validate(self, value):
        return self.primary.validate(value) or self.secondary.validate(value)


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


class ConditionalGuard(Guard):
    '''
    Guard is used to constrain an argument such that we can declare it to satisfy a condition:
      @pattern(guard < 1)
    or in the case where we already have a pattern
    '''

    def __init__(self, arg_name=None, arg_pos=None):
        super(ConditionalGuard, self).__init__(arg_name, arg_pos)
        self.checks = []

    @property
    def __name__(self):
        return 'Guard[' + ','.join(x.__name__ for x in self.checks) + ']'

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

    def __ne__(self, other):
        return OperatorGuard(operator.ne, other)


guard = _Guard()


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
# 4. __and__ and __or__ to guard
# 5. close_to(x, error-bound)