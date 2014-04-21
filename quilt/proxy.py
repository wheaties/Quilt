from quilt.exc import MatchError


class FunctionProxy(object):
    """Callable object that proxies an iterable collection of related GuardedFunctions associated with an instance
    and/or class of a member function of a class. If no GuardedFunction matches the arguments, raises a MatchError.

    FunctionProxy should not be constructed or used on it's own. It is an internal class used by the library to bind
    actual object instances to the underlying functions. It is responsible for determining the first matching function
    to the provided arguments and returning the evaluation of that function. From the perspective of the caller, it
    should be transparent and unseen.

    :param proxy_cache: an iterable collection of GuardedFunction.
    :param instance: An instance of an object. Defaults to None.
    :param owner: An instance of an owning class. Defaults to None.
    """

    def __init__(self, proxy_cache, instance=None, owner=None):
        self.proxy_cache = proxy_cache
        self.instance = instance
        self.owner = owner

    def __getattr__(self, item):
        return getattr(self.proxy_cache, item)

    def __str__(self):
        return self.__print__(str)

    def __repr__(self):
        return self.__print__(repr)

    def __print__(self, f):
        return 'FunctionProxy(underlying=[' + ', '.join(map(f, self.proxy_cache)) + '], instance=' + f(self.instance) \
            + ', owner=' + f(self.owner) + ')'

    def __call__(self, *args, **kwargs):
        """Calls each GuardedFunction until the first function validates against the provided arguments. If nothing
        validates, an exception is raised."""
        for guarded_func in self.proxy_cache:
            if guarded_func.validate_instance(self.instance, self.owner, *args, **kwargs):
                return guarded_func.underlying_func.__get__(self.instance, self.owner)(*args, **kwargs)
        raise MatchError(*args, **kwargs)


class ProxyCache(object):
    """Descriptor object for holding a reference to all GuardedFunction that have been assigned to the named class
    attribute. Proxies the attributes of the most recently added GuardedFunction for use with PlaceholderGuard.

    ProxyCache should not be constructed or used on its own. It is an internal class used by the library. The purpose
    is two fold, the first to be the descriptor responsible for returning a FunctionProxy via the __get__ method.
    The second is as a collection of GuardedFunction which can be iterated over by the FunctionProxy object and kept in
    sync with stateful changes made to the class instance.

    ProxyCache guarantees but does not explicitly enforce a non-emptiness cache criteria. If emptied, all FunctionProxy
    that are returned will throw MatchError.

    :param initial_func: The first GuardedFunction
    """
    def __init__(self, initial_func):
        self.cache = [initial_func]
        self.most_recent = initial_func

    def __getattr__(self, item):
        return getattr(self.most_recent, item)

    def __get__(self, instance=None, owner=None):
        return FunctionProxy(self, instance, owner)

    def __iter__(self):
        return iter(self.cache)

    def __str__(self):
        return self.__print__(str)

    def __repr__(self):
        return self.__print__(repr)

    def __print__(self, f):
        return 'ProxyCache(proxies=[' + ', '.join(map(f, self.cache)) + '], most_recent=' + f(self.most_recent) + ')'

    def append(self, value):
        self.cache.append(value)
        self.most_recent = value


class DefProxy(object):
    """Callable object that proxies an iterable collection of related GuardedFunctions associated with a named family of
    pattern matched function declarations within a module. If no GuardedFunction matches the arguments, raises a
    MatchError.

    DefProxy should not be constructed or used on it's own. It is an internal class used by the library. Like
    FunctionProxy its primary responsibility is to determine the first matching function to a set of provided arguments
    and evaluating the matched function against those arguments. And like FunctionProxy it should be transparent and
    unseen by the caller.

    Secondary to behaving like a function is also acting like a module level cache. Like ProxyCache, all attribute
    properties delegate to the last assigned GuardedFunction. This includes the __name__, __module__ and __globals__
    attributes. Accessing the __closure__ property always will return None. No attribute accessed this way is
    assignable.

    :param proxy_cache: an iterable collection of GuardeFunction.
    :param most_recent: the most recently added GuardedFunction.
    """

    def __init__(self, proxy_cache, most_recent):
        self.proxy_cache = proxy_cache
        self.most_recent = most_recent

    @property
    def __name__(self):
        return self.most_recent.__name__

    @property
    def __module__(self):
        return self.most_recent.__module__

    @property
    def __closure__(self):
        return None

    @property
    def __globals__(self):
        return self.most_recent.__globals__

    def __getattr__(self, item):
        return getattr(self.most_recent, item)

    def __str__(self):
        return self.__print__(str)

    def __repr__(self):
        return self.__print__(repr)

    def __print__(self, f):
        return 'DefProxy(name=' + self.__name__ + ', cached=[' + ', '.join(map(f, self.proxy_cache)) + '])'

    def __call__(self, *args, **kwargs):
        for guarded_func in self.proxy_cache:
            if guarded_func.validate(*args, **kwargs):
                return guarded_func.underlying_func(*args, **kwargs)
        raise MatchError(*args, **kwargs)