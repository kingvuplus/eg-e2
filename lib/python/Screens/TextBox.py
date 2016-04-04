# Embedded file name: /usr/lib/enigma2/python/Screens/TextBox.py
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel

class TextBox(Screen):

    def __init__(self, session, text = '', title = None):
        Screen.__init__(self, session)
        self.text = text
        self['text'] = ScrollLabel(self.text)
        self['actions'] = ActionMap(['OkCancelActions', 'DirectionActions'], {'cancel': self.cancel,
         'ok': self.ok,
         'up': self['text'].pageUp,
         'down': self['text'].pageDown}, -1)
        if title:
            self.setTitle(title)

    def ok(self):
        self.close()

    def cancel(self):
        self.close()