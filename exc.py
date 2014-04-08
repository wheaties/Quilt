__author__ = 'Owein Reese'


from itertools import chain


class MatchError(Exception):
    '''Thrown in situations where none of the guarded functions' patterns matched the input parameters.'''

    def __init__(self, *args, **kwargs):
        super(MatchError, self).__init__()
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return self.__print__(repr)

    def __str__(self):
        return self.__print__(str)

    def __print__(self, f):
        values = chain(map(f, self.args), (f(k) + '=' + f(v) for k, v in self.kwargs.items()))

        return 'Function not defined for ' + ', '.join(values)