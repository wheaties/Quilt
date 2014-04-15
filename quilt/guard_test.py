__author__ = 'Owein'

from unittest import TestCase
from quilt.guard import *


class _Yo(Guard):
    def __init__(self, name):
        super(_Yo, self).__init__(arg_name=name)

    def validate(self, value):
        return True


class GuardTest(TestCase):
    def test_validate_obj_no_attr(self):
        g = _Yo('y')
        self.assertFalse(g.validate_object(object()))

    def test_validate_obj(self):
        g = _Yo('x')
        class Foo(object):
            x = 1

        self.assertTrue(g.validate_object(Foo()))

    def test_iterable_on(self):
        g = _Yo('x')
        g.arg_pos = 1

        self.assertTrue(g.validate_iterable([1, 2]))

    def test_iterable_off(self):
        g = _Yo('x')
        g.arg_pos = 1

        self.assertFalse(g.validate_iterable([1]))

    def test_non_iterable(self):
        g = _Yo('x')
        g.arg_pos = 1

        self.assertFalse(g.validate_iterable(object()))


class ReverseGuardTest(TestCase):
    def test_validate_obj_no_attr(self):
        g = ReverseGuard(_Yo('x'))
        self.assertFalse(g.validate_object(object()))

    def test_validate_obj(self):
        g = ReverseGuard(_Yo('x'))
        class Foo(object):
            x = 1

        self.assertFalse(g.validate_object(Foo()))

    def test_validate(self):
        g = ReverseGuard(_Yo('x'))
        self.assertFalse(g.validate(1))


class OperatorGuardTest(TestCase):
    def test_less(self):
        g = lt(1)

        self.assertTrue(g.validate(0))
        self.assertFalse(g. validate(1))

    def test_less_or_equal(self):
        g = lte(1)

        self.assertTrue(g.validate(0))
        self.assertTrue(g.validate(1))
        self.assertFalse(g. validate(2))

    def test_greater(self):
        g = gt(0)

        self.assertTrue(g.validate(1))
        self.assertFalse(g. validate(0))

    def test_greater_or_equal(self):
        g = gte(0)

        self.assertTrue(g.validate(1))
        self.assertTrue(g.validate(0))
        self.assertFalse(g. validate(-1))


class TestAndOrGuard(TestCase):
    def test_and(self):
        class Bar(Guard):
            def validate(self, value):
                return False

        g = _Yo('a')
        h = Bar()
        self.assertFalse(g.and_(h).validate(object()))

    def test_and_pass(self):
        self.assertTrue(_Yo('x').and_(_Yo('y')).validate(object()))

    def test_or(self):
        class Bar(Guard):
            def validate(self, value):
                return False

        g = _Yo('x')
        h = Bar()
        self.assertTrue(g.or_(h).validate(object()))

    def test_or_pass(self):
        self.assertTrue(_Yo('x').or_(_Yo('')).validate(object()))


class TestValueGuard(TestCase):
    def test_value(self):
        g = ValueGuard(1)
        self.assertTrue(g.validate(1))
        self.assertFalse(g.validate(2))

    def test_wrong_type(self):
        g = ValueGuard(1)
        self.assertFalse(g.validate('1'))

    def test_position(self):
        g = ValueGuard(1, arg_pos=1)
        self.assertTrue(g.validate(1))
        self.assertFalse(g.validate(2))

    def test_kw(self):
        g = ValueGuard(1, arg_name='x')
        self.assertTrue(g.validate(1))
        self.assertFalse(g.validate(3))


class TestOneOfGuard(TestCase):
    def test_empty(self):
        g = one_of([])
        self.assertFalse(g.validate([]))
        self.assertFalse(g.validate(1))

    def test_one_iter(self):
        g = one_of([1])
        self.assertTrue(g.validate(1))
        self.assertFalse(g.validate(2))

    def test_one_args(self):
        g = one_of(1)
        self.assertTrue(g.validate(1))
        self.assertFalse(g.validate(2))

    def test_several_args(self):
        g = one_of([1], 2, 3)
        self.assertTrue(g.validate(2))
        self.assertTrue(g.validate([1]))
        self.assertFalse(g.validate(0))


class TestContainsGuard(TestCase):
    def test_empty(self):
        g = contains([])
        self.assertTrue(g.validate([1,2,3]))

    def test_one_args(self):
        g = contains(1)
        self.assertTrue(g.validate([1,2,3]))
        self.assertFalse(g.validate([2,3]))

    def test_one(self):
        g = contains([1])
        self.assertTrue(g.validate([1,2,3]))
        self.assertFalse(g.validate([2,3]))

    def test_several(self):
        g = contains([1,2])
        self.assertTrue(g.validate([1,2,3]))
        self.assertFalse(g.validate([2,3]))

    def test_several_args(self):
        g = contains(1, 2)
        self.assertTrue(g.validate([1,2,3]))
        self.assertFalse(g.validate([2,3]))


class TestCloseToGuard(TestCase):
    def test_equals(self):
        g = close_to(1.0, 0.0)
        self.assertFalse(g.validate(1.0))
        self.assertFalse(g.validate(0.9999999999999999))

    def test_within(self):
        g = close_to(1.0, 0.001)
        self.assertTrue(g.validate(0.9991))
        self.assertTrue(g.validate(1.0001))
        self.assertFalse(g.validate(0.999))

    def test_operator(self):
        def oper(x, y):
            return x - 2*y

        g = close_to(1.0, 0.1, oper)
        self.assertTrue(g.validate(1.0))
        self.assertFalse(g.validate(5))


class TestLengthGuard(TestCase):
    def test_length(self):
        g = has_length(4)
        self.assertTrue(g.validate([1,2,3,4]))
        self.assertFalse(g.validate([1,2,3]))

    def test_shorter(self):
        g = shorter_than(4)
        self.assertFalse(g.validate([1,2,3,4]))
        self.assertTrue(g.validate([1,2,3]))

    def test_longer(self):
        g = longer_than(3)
        self.assertTrue(g.validate([1,2,3,4]))
        self.assertFalse(g.validate([1,2,3]))

    def test_not_longer(self):
        g = not_longer_than(3)
        self.assertFalse(g.validate([1,2,3,4]))
        self.assertTrue(g.validate([1,2,3]))

    def test_not_shorter(self):
        g = not_shorter_than(4)
        self.assertTrue(g.validate([1,2,3,4]))
        self.assertFalse(g.validate([1,2,3]))


class TestRegexGuard(TestCase):
    def test_match(self):
        g = regex('[abc]de')

        self.assertTrue(g.validate('ade'))
        self.assertTrue(g.validate('bde'))
        self.assertTrue(g.validate('cde'))
        self.assertFalse(g.validate('dde'))
        self.assertFalse(g.validate('dade'))

    def test_empty(self):
        g = regex('')

        self.assertTrue(g.validate(''))
        self.assertTrue(g.validate('a'))

    def test_middle(self):
        g = regex('[ab]d', beginning=False)

        self.assertTrue(g.validate('ad'))
        self.assertTrue(g.validate('bd'))
        self.assertTrue(g.validate('bad'))
        self.assertFalse(g.validate('dab'))


class TestBeginsWithGuard(TestCase):
    def test_match(self):
        g = begins_with('ade')

        self.assertTrue(g.validate('ade'))
        self.assertTrue(g.validate('adefgh'))
        self.assertFalse(g.validate('aade'))

    def test_empty(self):
        g = begins_with('')

        self.assertTrue('a')
        self.assertFalse('')


class TestEndsWithGuard(TestCase):
    def test_match(self):
        g = ends_with('ade')

        self.assertTrue(g.validate('ade'))
        self.assertTrue(g.validate('aade'))
        self.assertFalse(g.validate('adea'))

    def test_empty(self):
        g = ends_with('')

        self.assertTrue('a')
        self.assertFalse('')


class TestPlaceholderGuard(TestCase):
    def test_empty(self):
        g = PlaceholderGuard()
        self.assertTrue(g.validate(object()))

    def test_call(self):
        g = PlaceholderGuard()
        @g
        def tester(x):
            return x < 2

        self.assertFalse(g.validate(4))
        self.assertTrue(g.validate(0))

