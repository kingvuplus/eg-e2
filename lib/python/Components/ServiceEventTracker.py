# Embedded file name: /usr/lib/enigma2/python/Components/ServiceEventTracker.py
InfoBarCount = 0

class InfoBarBase:
    onInfoBarOpened = []
    onInfoBarClosed = []

    @staticmethod
    def connectInfoBarOpened(fnc):
        if fnc not in InfoBarBase.onInfoBarOpened:
            InfoBarBase.onInfoBarOpened.append(fnc)

    @staticmethod
    def disconnectInfoBarOpened(fnc):
        if fnc in InfoBarBase.onInfoBarOpened:
            InfoBarBase.onInfoBarOpened.remove(fnc)

    @staticmethod
    def infoBarOpened(infobar):
        for x in InfoBarBase.onInfoBarOpened:
            x(infobar)

    @staticmethod
    def connectInfoBarClosed(fnc):
        if fnc not in InfoBarBase.onInfoBarClosed:
            InfoBarBase.onInfoBarClosed.append(fnc)

    @staticmethod
    def disconnectInfoBarClosed(fnc):
        if fnc in InfoBarBase.onInfoBarClosed:
            InfoBarBase.onInfoBarClosed.remove(fnc)

    @staticmethod
    def infoBarClosed(infobar):
        for x in InfoBarBase.onInfoBarClosed:
            x(infobar)

    def __init__(self, steal_current_service = False):
        global InfoBarCount
        if steal_current_service:
            ServiceEventTracker.setActiveInfoBar(self, None, None)
        else:
            nav = self.session.nav
            ServiceEventTracker.setActiveInfoBar(self, not steal_current_service and nav.getCurrentService(), nav.getCurrentlyPlayingServiceOrGroup())
        self.onClose.append(self.__close)
        InfoBarBase.infoBarOpened(self)
        InfoBarCount += 1
        return

    def __close(self):
        global InfoBarCount
        ServiceEventTracker.popActiveInfoBar()
        InfoBarBase.infoBarClosed(self)
        InfoBarCount -= 1


class ServiceEventTracker:
    InfoBarStack = []
    InfoBarStackSize = 0
    oldServiceStr = None
    EventMap = {}
    navcore = None

    @staticmethod
    def event(evt):
        set = ServiceEventTracker
        func_list = set.EventMap.setdefault(evt, [])
        if func_list:
            nav = set.navcore
            cur_ref = nav.getCurrentlyPlayingServiceOrGroup()
            try:
                old_service_running = set.oldRef and cur_ref and cur_ref == set.oldRef and set.oldServiceStr == nav.getCurrentService().getPtrString()
            except:
                old_service_running = None

            if not old_service_running and set.oldServiceStr:
                set.oldServiceStr = None
                set.oldRef = None
            ssize = set.InfoBarStackSize
            stack = set.InfoBarStack
            for func in func_list:
                if func[0] or not old_service_running and stack[ssize - 1] == func[1] or old_service_running and ssize > 1 and stack[ssize - 2] == func[1]:
                    func[2]()

        return

    @staticmethod
    def setActiveInfoBar(infobar, old_service, old_ref):
        set = ServiceEventTracker
        set.oldRef = old_ref
        set.oldServiceStr = old_service and old_service.getPtrString()
        set.InfoBarStack.append(infobar)
        set.InfoBarStackSize += 1

    @staticmethod
    def popActiveInfoBar():
        set = ServiceEventTracker
        stack = set.InfoBarStack
        if set.InfoBarStackSize:
            nav = set.navcore
            set.InfoBarStackSize -= 1
            del stack[set.InfoBarStackSize]
            old_service = nav.getCurrentService()
            set.oldServiceStr = old_service and old_service.getPtrString()
            set.oldRef = nav.getCurrentlyPlayingServiceOrGroup()

    def __init__(self, screen, eventmap):
        self.__screen = screen
        self.__eventmap = eventmap
        self.__passall = not isinstance(screen, InfoBarBase)
        EventMap = ServiceEventTracker.EventMap
        if not len(EventMap):
            screen.session.nav.event.append(ServiceEventTracker.event)
            ServiceEventTracker.navcore = screen.session.nav
        EventMap = EventMap.setdefault
        for x in eventmap.iteritems():
            EventMap(x[0], []).append((self.__passall, screen, x[1]))

        screen.onClose.append(self.__del_event)

    def __del_event(self):
        EventMap = ServiceEventTracker.EventMap.setdefault
        for x in self.__eventmap.iteritems():
            EventMap(x[0], []).remove((self.__passall, self.__screen, x[1]))