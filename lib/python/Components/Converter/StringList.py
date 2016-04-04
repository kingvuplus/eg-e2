# Embedded file name: /usr/lib/enigma2/python/Components/Converter/StringList.py
from Converter import Converter
from enigma import eListboxPythonStringContent
from Components.Element import cached

class StringList(Converter):

    def __init__(self, type):
        Converter.__init__(self, type)
        self.content = None
        return

    def changed(self, what):
        if not self.content:
            self.content = eListboxPythonStringContent()
        if self.source:
            self.content.setList(self.source.list)
        self.downstream_elements.changed(what)

    def selectionChanged(self, index):
        self.source.selectionChanged(index)

    def setIndex(self, index):
        print 'changed selection in listbox!'
        for x in self.downstream_elements:
            print 'downstream element', x
            if x is not self.master:
                print 'is not master, so update to index', index
                x.index = index

    def getIndex(self, index):
        return None

    index = property(getIndex, setIndex)

    @cached
    def getCurrent(self):
        if self.source is None or self.index is None or self.index >= len(self.source.list):
            return
        else:
            return self.source.list[self.index]

    current = property(getCurrent)

    @cached
    def getIndex(self):
        if self.master is None:
            return
        else:
            return self.master.index

    def setIndex(self, index):
        if self.master is not None:
            self.master.index = index
        return

    index = property(getIndex, setIndex)

    def entry_changed(self, index):
        if self.content:
            self.content.invalidateEntry(index)