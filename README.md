Quilt
=====

The concept and implementation of multiple-dispatch as put forth in a blog post by the BDFL is a wonderful thing right up until you realize that the core mechanism involves matching on argument types in a dynamically typed language! Quilt aims to provide a more Pythonic and declarative approach to the problem of multiple dispatch by focusing instead on argument values and object attributes.

###Usage With Functions

Quilt lets you declaratively state properties about the arguments of a function and dispatch upon those arguments:

     @defpattern(z=pattern(bar=longer_than(0)))
     def foo(x, y, z):
       return 3 + len(z.bar)
     
     @foo.pattern(x=greater_than(4))
     def foo(x, y, z):
       return x + len(z.bar)

wherein we're matching either on "x" if it's greater than 4 or if the "bar" property of the "z" argument has length greater than 0.

###Usage In Classes

Quilt relies on the new metaclass property of `__prepare__` found in Python3 to produce the following syntax:

     class Foo(Quilt):
       def __init__(self, x):
         self.x = x
       
       @pattern(x=3, y=one_of(1, 2, 3))
       def bar(self, x, y):
         return x - y
      
       @bar.pattern(y=one_of(1, 2, 3))
       def bar(self, x, y):
         return y
       
       @bar.x
       def test_y(self, value):
         return self.x < value


wherein `bar` is only defined for "x" values of 3 or less than `self.x` and "y" values of 1, 2, or 3. It also works on `__init__` so that you can have multiple constructors for a class.
