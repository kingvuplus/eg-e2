# Embedded file name: /usr/lib/enigma2/python/Screens/Screen.py
from Tools.Profile import profile
profile('LOAD:GUISkin')
from Components.GUISkin import GUISkin
profile('LOAD:Source')
from Components.Sources.Source import Source
profile('LOAD:GUIComponent')
from Components.GUIComponent import GUIComponent
profile('LOAD:eRCInput')
from enigma import eRCInput

class Screen(dict, GUISkin):
    False, SUSPEND_STOPS, SUSPEND_PAUSES = range(3)
    ALLOW_SUSPEND = False
    global_screen = None

    def __init__(self, session, parent = None):
        dict.__init__(self)
        self.skinName = self.__class__.__name__
        self.session = session
        self.parent = parent
        GUISkin.__init__(self)
        self.onClose = []
        self.onFirstExecBegin = []
        self.onExecBegin = []
        self.onExecEnd = []
        self.onShown = []
        self.onShow = []
        self.onHide = []
        self.execing = False
        self.shown = True
        self.already_shown = False
        self.renderer = []
        self.helpList = []
        self.close_on_next_exec = None
        self.stand_alone = False
        self.keyboardMode = None
        return

    def saveKeyboardMode(self):
        rcinput = eRCInput.getInstance()
        self.keyboardMode = rcinput.getKeyboardMode()

    def setKeyboardModeAscii(self):
        rcinput = eRCInput.getInstance()
        rcinput.setKeyboardMode(rcinput.kmAscii)

    def setKeyboardModeNone(self):
        rcinput = eRCInput.getInstance()
        rcinput.setKeyboardMode(rcinput.kmNone)

    def restoreKeyboardMode(self):
        rcinput = eRCInput.getInstance()
        if self.keyboardMode is not None:
            rcinput.setKeyboardMode(self.keyboardMode)
        return

    def execBegin(self):
        self.active_components = []
        if self.close_on_next_exec is not None:
            tmp = self.close_on_next_exec
            self.close_on_next_exec = None
            self.execing = True
            self.close(*tmp)
        else:
            single = self.onFirstExecBegin
            self.onFirstExecBegin = []
            for x in self.onExecBegin + single:
                x()
                if not self.stand_alone and self.session.current_dialog != self:
                    return

            for val in self.values() + self.renderer:
                val.execBegin()
                if not self.stand_alone and self.session.current_dialog != self:
                    return
                self.active_components.append(val)

            self.execing = True
            for x in self.onShown:
                x()

        return

    def execEnd(self):
        active_components = self.active_components
        self.active_components = None
        for val in active_components:
            val.execEnd()

        self.execing = False
        for x in self.onExecEnd:
            x()

        return

    def doClose(self):
        self.hide()
        for x in self.onClose:
            x()

        del self.helpList
        GUISkin.close(self)
        for val in self.renderer:
            val.disconnectAll()

        del self.session
        for name, val in self.items():
            val.destroy()
            del self[name]

        self.renderer = []
        self.__dict__.clear()

    def close(self, *retval):
        if not self.execing:
            self.close_on_next_exec = retval
        else:
            self.session.close(self, *retval)

    def setFocus(self, o):
        self.instance.setFocus(o.instance)

    def show(self):
        print '[SCREENNAME] ', self.skinName
        if self.shown and self.already_shown or not self.instance:
            return
        self.shown = True
        self.already_shown = True
        self.instance.show()
        for x in self.onShow:
            x()

        for val in self.values() + self.renderer:
            if isinstance(val, GUIComponent) or isinstance(val, Source):
                val.onShow()

    def hide(self):
        if not self.shown or not self.instance:
            return
        self.shown = False
        self.instance.hide()
        for x in self.onHide:
            x()

        for val in self.values() + self.renderer:
            if isinstance(val, GUIComponent) or isinstance(val, Source):
                val.onHide()

    def setAnimationMode(self, mode):
        if self.instance:
            self.instance.setAnimationMode(mode)

    def __repr__(self):
        return str(type(self))

    def getRelatedScreen(self, name):
        if name == 'session':
            return self.session.screen
        elif name == 'parent':
            return self.parent
        elif name == 'global':
            return self.global_screen
        else:
            return None
            return None