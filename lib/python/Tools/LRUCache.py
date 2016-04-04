# Embedded file name: /usr/lib/enigma2/python/Tools/LRUCache.py
from functools import update_wrapper
from collections import namedtuple
try:
    from thread import RLock
except:

    class RLock:

        def __enter__(self):
            pass

        def __exit__(self, exctype, excinst, exctb):
            pass


_CacheInfo = namedtuple('CacheInfo', ['hits',
 'misses',
 'maxsize',
 'currsize'])

class _HashedSeq(list):
    __slots__ = 'hashvalue'

    def __init__(self, tup, hash = hash):
        self[:] = tup
        self.hashvalue = hash(tup)

    def __hash__(self):
        return self.hashvalue


def _make_key(args, kwds, typed, kwd_mark = (object(),), fasttypes = {int,
 str,
 frozenset,
 type(None)}, sorted = sorted, tuple = tuple, type = type, len = len):
    key = args
    if kwds:
        sorted_items = sorted(kwds.items())
        key += kwd_mark
        for item in sorted_items:
            key += item

    if typed:
        key += tuple((type(v) for v in args))
        if kwds:
            key += tuple((type(v) for k, v in sorted_items))
    elif len(key) == 1 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedSeq(key)


def lru_cache(maxsize = 128, typed = False):
    if maxsize is not None and not isinstance(maxsize, int):
        raise TypeError('Expected maxsize to be an integer or None')
    sentinel = object()
    make_key = _make_key
    PREV, NEXT, KEY, RESULT = (0, 1, 2, 3)

    def decorating_function(user_function):
        cache = {}
        d = {'hits': 0,
         'misses': 0,
         'full': False,
         'root': []}
        cache_get = cache.get
        lock = RLock()
        d['root'][:] = [d['root'],
         d['root'],
         None,
         None]
        if maxsize == 0:

            def wrapper(*args, **kwds):
                result = user_function(*args, **kwds)
                d['misses'] += 1
                return result

        elif maxsize is None:

            def wrapper(*args, **kwds):
                key = make_key(args, kwds, typed)
                result = cache_get(key, sentinel)
                if result is not sentinel:
                    d['hits'] += 1
                    return result
                result = user_function(*args, **kwds)
                cache[key] = result
                d['misses'] += 1
                return result

        else:

            def wrapper(*args, **kwds):
                key = make_key(args, kwds, typed)
                with lock:
                    link = cache_get(key)
                    if link is not None:
                        link_prev, link_next, _key, result = link
                        link_prev[NEXT] = link_next
                        link_next[PREV] = link_prev
                        last = d['root'][PREV]
                        last[NEXT] = d['root'][PREV] = link
                        link[PREV] = last
                        link[NEXT] = d['root']
                        d['hits'] += 1
                        return result
                result = user_function(*args, **kwds)
                with lock:
                    if key in cache:
                        pass
                    elif d['full']:
                        oldroot = d['root']
                        oldroot[KEY] = key
                        oldroot[RESULT] = result
                        d['root'] = oldroot[NEXT]
                        oldkey = d['root'][KEY]
                        oldresult = d['root'][RESULT]
                        d['root'][KEY] = d['root'][RESULT] = None
                        del cache[oldkey]
                        cache[key] = oldroot
                    else:
                        last = d['root'][PREV]
                        link = [last,
                         d['root'],
                         key,
                         result]
                        last[NEXT] = d['root'][PREV] = cache[key] = link
                        d['full'] = len(cache) >= maxsize
                    d['misses'] += 1
                return result

        def cache_info():
            with lock:
                return _CacheInfo(d['hits'], d['misses'], maxsize, len(cache))

        def cache_clear():
            with lock:
                cache.clear()
                d['root'][:] = [d['root'],
                 d['root'],
                 None,
                 None]
                d['hits'] = d['misses'] = 0
                d['full'] = False
            return

        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        return update_wrapper(wrapper, user_function)

    return decorating_function