# Embedded file name: /usr/lib/enigma2/python/Screens/StreamingClientInfo.py
from Screen import Screen
from Components.About import about
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Button import Button
from Components.ScrollLabel import ScrollLabel
from Components.Converter.ClientsStreaming import ClientsStreaming
import skin

class StreamingClientsInfo(Screen):
    skin = '\n\t\t<screen name="StreamingClientsInfo" position="center,center" size="540,490" title="Streaming clients info">\n\t\t\t<widget name="ScrollLabel" font="Regular;20" position="0,00" size="540,490" zPosition="2" halign="left"/>\n\t\t</screen>\n\t'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skinName = ['AboutOE', 'StreamingClientsInfo']
        self.setTitle(_('Streaming clients info'))
        clients = ClientsStreaming('INFO_RESOLVE')
        text = clients.getText()
        self['lab1'] = Label(_('EGAMI %s') % about.getImageVersionString())
        self['key_red'] = Button(_('Close'))
        self['AboutScrollLabel'] = ScrollLabel(text or _('No stream clients'))
        self['actions'] = ActionMap(['ColorActions', 'SetupActions', 'DirectionActions'], {'cancel': self.close,
         'ok': self.close,
         'up': self['AboutScrollLabel'].pageUp,
         'down': self['AboutScrollLabel'].pageDown})