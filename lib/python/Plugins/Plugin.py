# Embedded file name: /usr/lib/enigma2/python/Plugins/Plugin.py
from Components.config import ConfigSubsection, config
import os
config.plugins = ConfigSubsection()

class PluginDescriptor:
    WHERE_EXTENSIONSMENU = 1
    WHERE_MAINMENU = 2
    WHERE_PLUGINMENU = 3
    WHERE_MOVIELIST = 4
    WHERE_MENU = 5
    WHERE_AUTOSTART = 6
    WHERE_WIZARD = 7
    WHERE_SESSIONSTART = 8
    WHERE_TELETEXT = 9
    WHERE_FILESCAN = 10
    WHERE_NETWORKSETUP = 11
    WHERE_EVENTINFO = 12
    WHERE_NETWORKCONFIG_READ = 13
    WHERE_AUDIOMENU = 14
    WHERE_SOFTWAREMANAGER = 15
    WHERE_CHANNEL_CONTEXT_MENU = 16
    WHERE_NETWORKMOUNTS = 17
    WHERE_VIXMENU = 18
    WHERE_RECORDTIMER = 19
    WHERE_SATCONFIGCHANGED = 20
    WHERE_SERVICESCAN = 21
    WHERE_EXTENSIONSINGLE = 22

    def __init__(self, name = 'Plugin', where = None, description = '', icon = None, fnc = None, wakeupfnc = None, needsRestart = None, internal = False, weight = 0):
        if not where:
            where = []
        self.name = name
        self.internal = internal
        self.needsRestart = needsRestart
        self.path = None
        if isinstance(where, list):
            self.where = where
        else:
            self.where = [where]
        self.description = description
        if icon is None or isinstance(icon, str):
            self.iconstr = icon
            self._icon = None
        else:
            self.iconstr = None
            self._icon = icon
        self.weight = weight
        self.wakeupfnc = wakeupfnc
        self.__call__ = fnc
        return

    def updateIcon(self, path):
        self.path = path

    def getWakeupTime(self):
        return self.wakeupfnc and self.wakeupfnc() or -1

    @property
    def icon(self):
        if self.iconstr:
            from Tools.LoadPixmap import LoadPixmap
            return LoadPixmap(os.path.join(self.path, self.iconstr))
        else:
            return self._icon

    def __eq__(self, other):
        return self.__call__ == other.__call__

    def __ne__(self, other):
        return self.__call__ != other.__call__

    def __lt__(self, other):
        if self.weight < other.weight:
            return True
        elif self.weight == other.weight:
            return self.name < other.name
        else:
            return False

    def __gt__(self, other):
        return other < self

    def __ge__(self, other):
        return not self < other

    def __le__(self, other):
        return not other < self