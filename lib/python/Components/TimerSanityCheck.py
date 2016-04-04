# Embedded file name: /usr/lib/enigma2/python/Components/TimerSanityCheck.py
import NavigationInstance
from time import localtime, mktime, gmtime
from ServiceReference import ServiceReference
from enigma import iServiceInformation, eServiceCenter, eServiceReference, getBestPlayableServiceReference
from timer import TimerEntry
from Tools.CIHelper import cihelper
from Components.config import config

class TimerSanityCheck:

    def __init__(self, timerlist, newtimer = None):
        self.localtimediff = 90000 - mktime(gmtime(90000))
        self.timerlist = timerlist
        self.newtimer = newtimer
        self.simultimer = []
        self.rep_eventlist = []
        self.nrep_eventlist = []
        self.bflag = -1
        self.eflag = 1

    def check(self, ext_timer = 1):
        if ext_timer != 1:
            self.newtimer = ext_timer
        if self.newtimer is None:
            self.simultimer = []
        else:
            self.simultimer = [self.newtimer]
        return self.checkTimerlist()

    def getSimulTimerList(self):
        return self.simultimer

    def doubleCheck(self):
        if self.newtimer is not None and self.newtimer.service_ref.ref.valid():
            self.simultimer = [self.newtimer]
            for timer in self.timerlist:
                if timer == self.newtimer:
                    return True
                if self.newtimer.begin >= timer.begin and self.newtimer.end <= timer.end:
                    fl1 = timer.service_ref.ref.flags & eServiceReference.isGroup
                    fl2 = self.newtimer.service_ref.ref.flags & eServiceReference.isGroup
                    if fl1 != fl2:
                        return False
                    if fl1:
                        return timer.service_ref.ref.getPath() == self.newtimer.service_ref.ref.getPath()
                    getUnsignedDataRef1 = timer.service_ref.ref.getUnsignedData
                    getUnsignedDataRef2 = self.newtimer.service_ref.ref.getUnsignedData
                    for x in (1, 2, 3, 4):
                        if getUnsignedDataRef1(x) != getUnsignedDataRef2(x):
                            break
                    else:
                        return True

        return False

    def checkTimerlist(self, ext_timer = 1):
        serviceHandler = eServiceCenter.getInstance()
        self.rep_eventlist = []
        self.nrep_eventlist = []
        if ext_timer != 1:
            self.newtimer = ext_timer
        if self.newtimer is not None and not self.newtimer.disabled:
            if not self.newtimer.service_ref.ref.valid():
                return False
            rflags = self.newtimer.repeated
            rflags = (rflags & 127) >> 3 | (rflags & 7) << 4
            if rflags:
                begin = self.newtimer.begin % 86400
                if self.localtimediff > 0 and begin + self.localtimediff > 86400:
                    rflags = rflags >> 1 & 63 | rflags << 6 & 64
                elif self.localtimediff < 0 and begin < self.localtimediff:
                    rflags = rflags << 1 & 126 | rflags >> 6 & 1
                while rflags:
                    if rflags & 1:
                        self.rep_eventlist.append((begin, -1))
                    begin += 86400
                    rflags >>= 1

            else:
                self.nrep_eventlist.extend([(self.newtimer.begin, self.bflag, -1), (self.newtimer.end, self.eflag, -1)])
        idx = 0
        for timer in self.timerlist:
            if timer != self.newtimer and not timer.disabled:
                if timer.repeated:
                    rflags = timer.repeated
                    rflags = (rflags & 127) >> 3 | (rflags & 7) << 4
                    begin = timer.begin % 86400
                    if self.localtimediff > 0 and begin + self.localtimediff > 86400:
                        rflags = rflags >> 1 & 63 | rflags << 6 & 64
                    elif self.localtimediff < 0 and begin < self.localtimediff:
                        rflags = rflags << 1 & 126 | rflags >> 6 & 1
                    while rflags:
                        if rflags & 1:
                            self.rep_eventlist.append((begin, idx))
                        begin += 86400
                        rflags >>= 1

                elif timer.state < TimerEntry.StateEnded:
                    self.nrep_eventlist.extend([(timer.begin, self.bflag, idx), (timer.end, self.eflag, idx)])
            idx += 1

        if self.nrep_eventlist:
            interval_begin = min(self.nrep_eventlist)[0]
            interval_end = max(self.nrep_eventlist)[0]
            offset_0 = interval_begin - interval_begin % 604800
            weeks = (interval_end - offset_0) / 604800
            if (interval_end - offset_0) % 604800:
                weeks += 1
            for cnt in range(int(weeks)):
                for event in self.rep_eventlist:
                    if event[1] == -1:
                        event_begin = self.newtimer.begin
                        event_end = self.newtimer.end
                    else:
                        event_begin = self.timerlist[event[1]].begin
                        event_end = self.timerlist[event[1]].end
                    new_event_begin = event[0] + offset_0 + cnt * 604800
                    new_lth = localtime(new_event_begin).tm_hour
                    new_event_begin += 3600 * (localtime(event_begin).tm_hour - new_lth)
                    new_event_end = new_event_begin + (event_end - event_begin)
                    if event[1] == -1:
                        if new_event_begin >= self.newtimer.begin:
                            self.nrep_eventlist.extend([(new_event_begin, self.bflag, event[1]), (new_event_end, self.eflag, event[1])])
                    elif new_event_begin >= self.timerlist[event[1]].begin:
                        self.nrep_eventlist.extend([(new_event_begin, self.bflag, event[1]), (new_event_end, self.eflag, event[1])])

        else:
            offset_0 = 345600
            for cnt in (0, 1):
                for event in self.rep_eventlist:
                    if event[1] == -1:
                        event_begin = self.newtimer.begin
                        event_end = self.newtimer.end
                    else:
                        event_begin = self.timerlist[event[1]].begin
                        event_end = self.timerlist[event[1]].end
                    new_event_begin = event[0] + offset_0 + cnt * 604800
                    new_event_end = new_event_begin + (event_end - event_begin)
                    self.nrep_eventlist.extend([(new_event_begin, self.bflag, event[1]), (new_event_end, self.eflag, event[1])])

        self.nrep_eventlist.sort()
        fakeRecList = []
        ConflictTimer = None
        ConflictTunerType = None
        newTimerTunerType = None
        cnt = 0
        idx = 0
        is_ci_use = 0
        is_ci_timer_conflict = 0
        overlaplist = []
        ci_timer = False
        if config.misc.use_ci_assignment.value and cihelper.ServiceIsAssigned(self.newtimer.service_ref.ref):
            ci_timer = self.newtimer
            ci_timer_begin = ci_timer.begin
            ci_timer_end = ci_timer.end
            ci_timer_dur = ci_timer_end - ci_timer_begin
            ci_timer_events = []
            for ev in self.nrep_eventlist:
                if ev[2] == -1:
                    ci_timer_events.append((ev[0], ev[0] + ci_timer_dur))

        for event in self.nrep_eventlist:
            cnt += event[1]
            if event[2] == -1:
                timer = self.newtimer
            else:
                timer = self.timerlist[event[2]]
            if event[1] == self.bflag:
                tunerType = []
                if timer.service_ref.ref and timer.service_ref.ref.flags & eServiceReference.isGroup:
                    fakeRecService = NavigationInstance.instance.recordService(getBestPlayableServiceReference(timer.service_ref.ref, eServiceReference(), True), True)
                else:
                    fakeRecService = NavigationInstance.instance.recordService(timer.service_ref, True)
                if fakeRecService:
                    fakeRecResult = fakeRecService.start(True)
                else:
                    fakeRecResult = -1
                if fakeRecResult == -6 and len(NavigationInstance.instance.getRecordings(True)) < 2:
                    print '[TimerSanityCheck] less than two timers in the simulated recording list - timer conflict is not plausible - ignored !'
                    fakeRecResult = 0
                if not fakeRecResult:
                    if hasattr(fakeRecService, 'frontendInfo') and hasattr(fakeRecService.frontendInfo(), 'getFrontendData'):
                        feinfo = fakeRecService.frontendInfo().getFrontendData()
                        tunerType.append(feinfo.get('tuner_type'))
                else:

                    def getServiceType(ref):
                        serviceInfo = serviceHandler.info(ref)
                        serviceInfo = serviceInfo and serviceInfo.getInfoObject(ref, iServiceInformation.sTransponderData)
                        return serviceInfo and serviceInfo['tuner_type'] or ''

                    ref = timer.service_ref.ref
                    if ref.flags & eServiceReference.isGroup:
                        serviceList = serviceHandler.list(ref)
                        if serviceList:
                            for ref in serviceList.getContent('R'):
                                type = getServiceType(ref)
                                if type not in tunerType:
                                    tunerType.append(type)

                    else:
                        tunerType.append(getServiceType(ref))
                if event[2] == -1:
                    newTimerTunerType = tunerType
                overlaplist.append((fakeRecResult, timer, tunerType))
                fakeRecList.append((timer, fakeRecService))
                if fakeRecResult:
                    if ConflictTimer is None:
                        ConflictTimer = timer
                        ConflictTunerType = tunerType
            elif event[1] == self.eflag:
                for fakeRec in fakeRecList:
                    if timer == fakeRec[0] and fakeRec[1]:
                        NavigationInstance.instance.stopRecordService(fakeRec[1])
                        fakeRecList.remove(fakeRec)

                fakeRec = None
                for entry in overlaplist:
                    if entry[1] == timer:
                        overlaplist.remove(entry)

            else:
                print 'Bug: unknown flag!'
            if ci_timer and cihelper.ServiceIsAssigned(timer.service_ref.ref):
                if event[1] == self.bflag:
                    timer_begin = event[0]
                    timer_end = event[0] + (timer.end - timer.begin)
                else:
                    timer_end = event[0]
                    timer_begin = event[0] - (timer.end - timer.begin)
                if timer != ci_timer:
                    for ci_ev in ci_timer_events:
                        if ci_ev[0] >= timer_begin and ci_ev[0] <= timer_end or ci_ev[1] >= timer_begin and ci_ev[1] <= timer_end:
                            if ci_timer.service_ref.ref != timer.service_ref.ref:
                                is_ci_timer_conflict = 1
                                break

                if is_ci_timer_conflict == 1:
                    if ConflictTimer is None:
                        ConflictTimer = timer
                        ConflictTunerType = tunerType
            self.nrep_eventlist[idx] = (event[0],
             event[1],
             event[2],
             cnt,
             overlaplist[:])
            idx += 1

        if ConflictTimer is None:
            return True
        if self.newtimer is not None:
            if self.newtimer is not ConflictTimer:
                for event in self.nrep_eventlist:
                    if len(event[4]) > 1:
                        kt = False
                        nt = False
                        for entry in event[4]:
                            if entry[1] is ConflictTimer:
                                kt = True
                            if entry[1] is self.newtimer:
                                nt = True

                        if nt and kt:
                            ConflictTimer = self.newtimer
                            ConflictTunerType = newTimerTunerType
                            break

        self.simultimer = [ConflictTimer]
        for event in self.nrep_eventlist:
            if len(event[4]) > 1:
                for entry in event[4]:
                    if entry[1] is ConflictTimer:
                        break
                else:
                    continue

                for entry in event[4]:
                    if entry[1] not in self.simultimer:
                        for x in entry[2]:
                            if x in ConflictTunerType:
                                self.simultimer.append(entry[1])
                                break

        if len(self.simultimer) < 2:
            print 'Possible Bug: unknown Conflict!'
            return True
        else:
            return False