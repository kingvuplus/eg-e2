# Embedded file name: /usr/lib/enigma2/python/Components/Converter/Combine.py
from Converter import Converter
from Components.Element import cached

class Combine(Converter, object):
    SINGLE_SOURCE = False

    def __init__(self, arg = None, func = None):
        Converter.__init__(self, arg)
        self.func = func

    @cached
    def getValue(self):
        return self.func(self.sources)

    value = property(getValue)