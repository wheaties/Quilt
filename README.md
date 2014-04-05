Quilt
=====

The concept and implementation of multiple-dispatch as put forth in a blog post by the BDFL is a wonderful thing right up until you realize that the core mechanism involves matching on argument types in a dynamically typed language! Quilt aims to provide a more Pythonic and declarative approach to the problem of multiple dispatch by focusing instead on argument values and object attributes.

Current Quilt is a WIP and suitable only for Python 3 due to its reliance on `__prepare__`.
