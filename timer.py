# Embedded file name: /usr/lib/enigma2/python/timer.py
from bisect import insort
from time import time, localtime, mktime
from enigma import eTimer, eActionMap
import datetime

class TimerEntry:
    StateWaiting = 0
    StatePrepared = 1
    StateRunning = 2
    StateEnded = 3
    StateFailed = 4

    def __init__(self, begin, end):
        self.begin = begin
        self.prepare_time = 20
        self.end = end
        self.state = 0
        self.findRunningEvent = True
        self.findNextEvent = False
        self.resetRepeated()
        self.repeatedbegindate = begin
        self.backoff = 0
        self.disabled = False
        self.failed = False

    def resetState(self):
        self.state = self.StateWaiting
        self.cancelled = False
        self.first_try_prepare = 0
        self.findRunningEvent = True
        self.findNextEvent = False
        self.timeChanged()

    def resetRepeated(self):
        self.repeated = int(0)

    def setRepeated(self, day):
        self.repeated |= 2 ** day

    def isRunning(self):
        return self.state == self.StateRunning

    def addOneDay(self, timedatestruct):
        oldHour = timedatestruct.tm_hour
        newdate = (datetime.datetime(timedatestruct.tm_year, timedatestruct.tm_mon, timedatestruct.tm_mday, timedatestruct.tm_hour, timedatestruct.tm_min, timedatestruct.tm_sec) + datetime.timedelta(days=1)).timetuple()
        if localtime(mktime(newdate)).tm_hour != oldHour:
            return (datetime.datetime(timedatestruct.tm_year, timedatestruct.tm_mon, timedatestruct.tm_mday, timedatestruct.tm_hour, timedatestruct.tm_min, timedatestruct.tm_sec) + datetime.timedelta(days=2)).timetuple()
        return newdate

    def isFindRunningEvent(self):
        return self.findRunningEvent

    def isFindNextEvent(self):
        return self.findNextEvent

    def processRepeated(self, findRunningEvent = True, findNextEvent = False):
        if self.repeated != 0:
            now = int(time()) + 1
            if findNextEvent:
                now = self.end + 120
            self.findRunningEvent = findRunningEvent
            self.findNextEvent = findNextEvent
            localrepeatedbegindate = localtime(self.repeatedbegindate)
            localbegin = localtime(self.begin)
            localend = localtime(self.end)
            localnow = localtime(now)
            day = []
            flags = self.repeated
            for x in (0, 1, 2, 3, 4, 5, 6):
                if flags & 1 == 1:
                    day.append(0)
                else:
                    day.append(1)
                flags >>= 1

            while day[localbegin.tm_wday] != 0 or mktime(localrepeatedbegindate) > mktime(localbegin) or day[localbegin.tm_wday] == 0 and findRunningEvent and localend < localnow or not findRunningEvent and localbegin < localnow:
                localbegin = self.addOneDay(localbegin)
                localend = self.addOneDay(localend)

            self.begin = int(mktime(localbegin))
            self.end = int(mktime(localend))
            if self.begin == self.end:
                self.end += 1
            self.timeChanged()

    def __lt__(self, o):
        return self.getNextActivation() < o.getNextActivation()

    def activate(self):
        pass

    def timeChanged(self):
        pass

    def shouldSkip(self):
        if self.disabled:
            if self.end <= time() and 'PowerTimerEntry' not in `self`:
                self.disabled = False
            return True
        if 'PowerTimerEntry' in `self`:
            if (self.timerType == 3 or self.timerType == 4) and self.autosleeprepeat != 'once':
                return False
            elif self.begin >= time() and (self.timerType == 3 or self.timerType == 4) and self.autosleeprepeat == 'once':
                return False
            elif (self.timerType == 3 or self.timerType == 4) and self.autosleeprepeat == 'once' and self.state != TimerEntry.StatePrepared:
                return True
            else:
                return self.end <= time() and self.state == TimerEntry.StateWaiting and self.timerType != 3 and self.timerType != 4
        else:
            return self.end <= time() and (self.state == TimerEntry.StateWaiting or self.state == TimerEntry.StateFailed)

    def abort(self):
        self.end = time()
        if self.begin > self.end:
            self.begin = self.end
        self.cancelled = True

    def getNextActivation(self):
        pass

    def fail(self):
        self.faileded = True

    def disable(self):
        self.disabled = True

    def enable(self):
        self.disabled = False


class Timer:
    MaxWaitTime = 100

    def __init__(self):
        self.timer_list = []
        self.processed_timers = []
        self.timer = eTimer()
        self.timer.callback.append(self.calcNextActivation)
        self.lastActivation = time()
        self.calcNextActivation()
        self.on_state_change = []

    def stateChanged(self, entry):
        for f in self.on_state_change:
            f(entry)

    def cleanup(self):
        self.processed_timers = [ entry for entry in self.processed_timers if entry.disabled ]

    def cleanupDisabled(self):
        disabled_timers = [ entry for entry in self.processed_timers if entry.disabled ]
        for timer in disabled_timers:
            timer.shouldSkip()

    def cleanupDaily(self, days):
        limit = time() - days * 3600 * 24
        self.processed_timers = [ entry for entry in self.processed_timers if entry.disabled and entry.repeated or entry.end and entry.end > limit ]

    def addTimerEntry(self, entry, noRecalc = 0):
        entry.processRepeated()
        if entry.shouldSkip() or entry.state == TimerEntry.StateEnded or entry.state == TimerEntry.StateWaiting and entry.disabled:
            insort(self.processed_timers, entry)
            entry.state = TimerEntry.StateEnded
        else:
            insort(self.timer_list, entry)
            if not noRecalc:
                self.calcNextActivation()

    def setNextActivation(self, now, when):
        delay = int((when - now) * 1000)
        self.timer.start(delay, 1)
        self.next = when

    def calcNextActivation(self):
        now = time()
        if self.lastActivation > now:
            print '[timer.py] timewarp - re-evaluating all processed timers.'
            tl = self.processed_timers
            self.processed_timers = []
            for x in tl:
                x.resetState()
                self.addTimerEntry(x, noRecalc=1)

        self.processActivation()
        self.lastActivation = now
        min = int(now) + self.MaxWaitTime
        if self.timer_list:
            self.timer_list.sort()
            w = self.timer_list[0].getNextActivation()
            if w < min:
                min = w
        if int(now) < 1072224000 and min > now + 5:
            min = now + 5
        self.setNextActivation(now, min)

    def timeChanged(self, timer):
        timer.timeChanged()
        if timer.state == TimerEntry.StateEnded:
            self.processed_timers.remove(timer)
        else:
            try:
                self.timer_list.remove(timer)
            except:
                print '[timer] Failed to remove, not in list'
                return

        if timer.state == TimerEntry.StateEnded:
            timer.state = TimerEntry.StateWaiting
        elif 'PowerTimerEntry' in `timer` and (timer.timerType == 3 or timer.timerType == 4):
            if timer.state > 0:
                eActionMap.getInstance().unbindAction('', timer.keyPressed)
            timer.state = TimerEntry.StateWaiting
        self.addTimerEntry(timer)

    def doActivate(self, w):
        self.timer_list.remove(w)
        if w.shouldSkip():
            w.state = TimerEntry.StateEnded
        elif w.activate():
            w.state += 1
        if w.state < TimerEntry.StateEnded:
            insort(self.timer_list, w)
        elif w.repeated:
            w.processRepeated()
            w.state = TimerEntry.StateWaiting
            self.addTimerEntry(w)
        else:
            insort(self.processed_timers, w)
        self.stateChanged(w)

    def processActivation(self):
        t = int(time()) + 1
        while self.timer_list and self.timer_list[0].getNextActivation() < t:
            self.doActivate(self.timer_list[0])