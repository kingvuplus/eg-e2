# Embedded file name: /usr/lib/enigma2/python/Screens/ServiceStopScreen.py
from Screens.MessageBox import MessageBox

class ServiceStopScreen:

    def __init__(self):
        try:
            self.session
        except:
            print '[ServiceStopScreen] ERROR: no self.session set'

        self.oldref = None
        self.onClose.append(self.__onClose)
        return

    def pipAvailable(self):
        try:
            self.session.pipshown
            pipavailable = True
        except:
            pipavailable = False

        return pipavailable

    def stopService(self):
        self.oldref = self.session.nav.getCurrentlyPlayingServiceOrGroup()
        self.session.nav.stopService()
        if self.pipAvailable():
            if self.session.pipshown:
                if hasattr(self.session, 'infobar'):
                    if self.session.infobar.servicelist and self.session.infobar.servicelist.dopipzap:
                        self.session.infobar.servicelist.togglePipzap()
                if hasattr(self.session, 'pip'):
                    del self.session.pip
                self.session.pipshown = False

    def __onClose(self):
        self.session.nav.playService(self.oldref)

    def restoreService(self, msg = _('Zap back to previously tuned service?')):
        if self.oldref:
            self.session.openWithCallback(self.restartPrevService, MessageBox, msg, MessageBox.TYPE_YESNO)
        else:
            self.restartPrevService(False)

    def restartPrevService(self, yesno):
        if not yesno:
            self.oldref = None
        self.close()
        return