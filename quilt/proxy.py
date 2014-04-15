from quilt.exc import MatchError


class FunctionProxy(object):
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
        return 'FunctionProxy(underlying=[' + ', '.join(map(f, self.proxy_cache)) + '])'

    def __call__(self, *args, **kwargs):
        for guarded_func in self.proxy_cache:
            if guarded_func.validate_instance(self.instance, self.owner, *args, **kwargs):
                return guarded_func.underlying_func.__get__(self.instance, self.owner)(*args, **kwargs)
        raise MatchError(*args, **kwargs)


class ProxyCache(object):
    def __init__(self, initial_func):
        self.cache = [initial_func]
        self.most_recent = initial_func

    def __getattr__(self, item):
        return getattr(self.most_recent, item)

    def __get__(self, instance=None, owner=None):
        return FunctionProxy(self, instance, owner)

    def __iter__(self):
        return iter(self.cache)

    def append(self, value):
        self.cache.append(value)
        self.most_recent = value