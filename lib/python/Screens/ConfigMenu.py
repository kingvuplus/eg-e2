# Embedded file name: /usr/lib/enigma2/python/Screens/ConfigMenu.py
from Screen import Screen
from Components.ConfigList import ConfigList
from Components.ActionMap import ActionMap

class ConfigMenu(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self['actions'] = ActionMap(['OkCancelActions'], {'ok': self.okbuttonClick,
         'cancel': self.close})


class configTest(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self['config'] = ConfigList([configEntry('HKEY_LOCAL_ENIGMA/IMPORTANT/USER_ANNOYING_STUFF/SDTV/FLASHES/GREEN'), configEntry('HKEY_LOCAL_ENIGMA/IMPORTANT/USER_ANNOYING_STUFF/HDTV/FLASHES/GREEN')])
        self['actions'] = ActionMap(['OkCancelActions'], {'ok': self['config'].toggle,
         'cancel': self.close})