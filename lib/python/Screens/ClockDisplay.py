# Embedded file name: /usr/lib/enigma2/python/Screens/ClockDisplay.py
from Screen import Screen

class ClockDisplay(Screen):

    def okbutton(self):
        self.session.close()

    def __init__(self, session, clock):
        Screen.__init__(self, session)
        self['theClock'] = clock
        b = Button('bye')
        b.onClick = [self.okbutton]
        self['okbutton'] = b
        self['title'] = Header('clock dialog: here you see the current uhrzeit!')