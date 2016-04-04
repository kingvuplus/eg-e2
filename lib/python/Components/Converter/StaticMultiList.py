# Embedded file name: /usr/lib/enigma2/python/Components/Converter/StaticMultiList.py
from enigma import eListboxPythonMultiContent
from Components.Converter.StringList import StringList

class StaticMultiList(StringList):

    def changed(self, what):
        if not self.content:
            self.content = eListboxPythonMultiContent()
            if self.source:
                self.content.setItemHeight(self.source.item_height)
                index = 0
                for f in self.source.fonts:
                    self.content.setFont(index, f)
                    index += 1

        if self.source:
            self.content.setList(self.source.list)
        print 'downstream_elements:', self.downstream_elements
        self.downstream_elements.changed(what)