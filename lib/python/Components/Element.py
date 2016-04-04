# Embedded file name: /usr/lib/enigma2/python/Components/Element.py
from Tools.CList import CList

def cached(f):
    name = f.__name__

    def wrapper(self):
        cache = self.cache
        if cache is None:
            return f(self)
        else:
            if name not in cache:
                cache[name] = (True, f(self))
            return cache[name][1]

    return wrapper


class ElementError(Exception):

    def __init__(self, message):
        self.msg = message

    def __str__(self):
        return self.msg


class Element(object):
    CHANGED_DEFAULT = 0
    CHANGED_ALL = 1
    CHANGED_CLEAR = 2
    CHANGED_SPECIFIC = 3
    CHANGED_POLL = 4
    SINGLE_SOURCE = True

    def __init__(self):
        self.downstream_elements = CList()
        self.master = None
        self.sources = []
        self.source = None
        self.__suspended = True
        self.cache = None
        return

    def connectDownstream(self, downstream):
        self.downstream_elements.append(downstream)
        if self.master is None:
            self.master = downstream
        return

    def connectUpstream(self, upstream):
        self.sources.append(upstream)
        self.source = upstream
        self.changed((self.CHANGED_DEFAULT,))

    def connect(self, upstream):
        self.connectUpstream(upstream)
        upstream.connectDownstream(self)

    def disconnectAll(self):
        for s in self.sources:
            s.disconnectDownstream(self)

        if self.source:
            self.destroy()
        self.source = None
        self.sources = []
        return

    def disconnectDownstream(self, downstream):
        self.downstream_elements.remove(downstream)
        if self.master == downstream:
            self.master = None
        if len(self.downstream_elements) == 0:
            self.disconnectAll()
        return

    def changed(self, *args, **kwargs):
        self.cache = {}
        self.downstream_elements.changed(*args, **kwargs)
        self.cache = None
        return

    def setSuspend(self, suspended):
        changed = self.__suspended != suspended
        if not self.__suspended and suspended:
            self.doSuspend(1)
        elif self.__suspended and not suspended:
            self.doSuspend(0)
        self.__suspended = suspended
        if changed:
            for s in self.sources:
                s.checkSuspend()

    suspended = property(lambda self: self.__suspended, setSuspend)

    def checkSuspend(self):
        self.suspended = reduce(lambda x, y: x and y.__suspended, self.downstream_elements, True)

    def doSuspend(self, suspend):
        pass

    def destroy(self):
        pass