# Embedded file name: /usr/lib/enigma2/python/Components/Converter/StringListSelection.py
from Components.Converter.Converter import Converter
from Components.Element import cached

class StringListSelection(Converter, object):

    def __init__(self, args):
        Converter.__init__(self, args)

    def selChanged(self):
        self.downstream_elements.changed((self.CHANGED_ALL, 0))

    @cached
    def getText(self):
        cur = self.source.current
        if cur and len(cur):
            return cur[0]
        else:
            return None

    text = property(getText)

    def changed(self, what):
        if what[0] == self.CHANGED_DEFAULT:
            self.source.onSelectionChanged.append(self.selChanged)
        Converter.changed(self, what)