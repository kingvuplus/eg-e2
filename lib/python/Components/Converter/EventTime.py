# Embedded file name: /usr/lib/enigma2/python/Components/Converter/EventTime.py
from Converter import Converter
from Poll import Poll
from time import time
from Components.Element import cached, ElementError
from Components.config import config
from enigma import eEPGCache

class EventTime(Poll, Converter, object):
    STARTTIME = 0
    ENDTIME = 1
    REMAINING = 2
    REMAINING_VFD = 3
    PROGRESS = 4
    DURATION = 5
    ELAPSED = 6
    ELAPSED_VFD = 7
    NEXT_START_TIME = 8
    NEXT_END_TIME = 9
    NEXT_DURATION = 10
    THIRD_START_TIME = 11
    THIRD_END_TIME = 12
    THIRD_DURATION = 13

    def __init__(self, type):
        Converter.__init__(self, type)
        Poll.__init__(self)
        self.epgcache = eEPGCache.getInstance()
        if type == 'EndTime':
            self.type = self.ENDTIME
        elif type == 'Remaining':
            self.type = self.REMAINING
            self.poll_interval = 60000
            self.poll_enabled = True
        elif type == 'VFDRemaining':
            self.type = self.REMAINING_VFD
            self.poll_interval = 60000
            self.poll_enabled = True
        elif type == 'StartTime':
            self.type = self.STARTTIME
        elif type == 'Duration':
            self.type = self.DURATION
        elif type == 'Progress':
            self.type = self.PROGRESS
            self.poll_interval = 30000
            self.poll_enabled = True
        elif type == 'Elapsed':
            self.type = self.ELAPSED
            self.poll_interval = 60000
            self.poll_enabled = True
        elif type == 'VFDElapsed':
            self.type = self.ELAPSED_VFD
            self.poll_interval = 60000
            self.poll_enabled = True
        elif type == 'NextStartTime':
            self.type = self.NEXT_START_TIME
        elif type == 'NextEndTime':
            self.type = self.NEXT_END_TIME
        elif type == 'NextDurartion':
            self.type = self.NEXT_DURATION
        elif type == 'ThirdStartTime':
            self.type = self.THIRD_START_TIME
        elif type == 'ThirdEndTime':
            self.type = self.THIRD_END_TIME
        elif type == 'ThirdDurartion':
            self.type = self.THIRD_DURATION
        else:
            raise ElementError("'%s' is not <StartTime|EndTime|Remaining|Elapsed|Duration|Progress> for EventTime converter" % type)

    @cached
    def getTime(self):
        event = self.source.event
        if event is None:
            return
        else:
            st = event.getBeginTime()
            if self.type == self.STARTTIME:
                return st
            duration = event.getDuration()
            if self.type == self.DURATION:
                return duration
            st += duration
            if self.type == self.ENDTIME:
                return st
            if self.type == self.REMAINING or self.type == self.REMAINING_VFD or self.type == self.ELAPSED or self.type == self.ELAPSED_VFD:
                now = int(time())
                remaining = st - now
                if remaining < 0:
                    remaining = 0
                start_time = event.getBeginTime()
                end_time = start_time + duration
                elapsed = now - start_time
                if start_time <= now <= end_time:
                    if self.type == self.REMAINING and config.usage.swap_time_remaining_on_osd.value == '0':
                        return (duration, remaining)
                    if self.type == self.REMAINING and config.usage.swap_time_remaining_on_osd.value == '1':
                        return (duration, elapsed)
                    if self.type == self.REMAINING and config.usage.swap_time_remaining_on_osd.value == '2':
                        return (duration, elapsed, remaining)
                    if self.type == self.REMAINING and config.usage.swap_time_remaining_on_osd.value == '3':
                        return (duration, remaining, elapsed)
                    if self.type == self.ELAPSED and config.usage.swap_time_remaining_on_osd.value == '0':
                        return (duration, elapsed)
                    if self.type == self.ELAPSED and config.usage.swap_time_remaining_on_osd.value == '1':
                        return (duration, remaining)
                    if self.type == self.ELAPSED and config.usage.swap_time_remaining_on_osd.value == '2':
                        return (duration, elapsed, remaining)
                    if self.type == self.ELAPSED and config.usage.swap_time_remaining_on_osd.value == '3':
                        return (duration, remaining, elapsed)
                    if self.type == self.REMAINING_VFD and config.usage.swap_time_remaining_on_vfd.value == '0':
                        return (duration, remaining)
                    if self.type == self.REMAINING_VFD and config.usage.swap_time_remaining_on_vfd.value == '1':
                        return (duration, elapsed)
                    if self.type == self.REMAINING_VFD and config.usage.swap_time_remaining_on_vfd.value == '2':
                        return (duration, elapsed, remaining)
                    if self.type == self.REMAINING_VFD and config.usage.swap_time_remaining_on_vfd.value == '3':
                        return (duration, remaining, elapsed)
                    if self.type == self.ELAPSED_VFD and config.usage.swap_time_remaining_on_vfd.value == '0':
                        return (duration, elapsed)
                    if self.type == self.ELAPSED_VFD and config.usage.swap_time_remaining_on_vfd.value == '1':
                        return (duration, remaining)
                    if self.type == self.ELAPSED_VFD and config.usage.swap_time_remaining_on_vfd.value == '2':
                        return (duration, elapsed, remaining)
                    if self.type == self.ELAPSED_VFD and config.usage.swap_time_remaining_on_vfd.value == '3':
                        return (duration, remaining, elapsed)
                else:
                    return (duration, None)
            elif self.type == self.NEXT_START_TIME or self.type == self.NEXT_END_TIME or self.type == self.NEXT_DURATION or self.type == self.THIRD_START_TIME or self.type == self.THIRD_END_TIME or self.type == self.THIRD_DURATION:
                reference = self.source.service
                info = reference and self.source.info
                if info is None:
                    return
                test = ['IBDCX', (reference.toString(),
                  1,
                  -1,
                  1440)]
                self.list = [] if self.epgcache is None else self.epgcache.lookupEvent(test)
                if self.list:
                    try:
                        if self.type == self.NEXT_START_TIME and self.list[1][1]:
                            return self.list[1][1]
                        if self.type == self.NEXT_END_TIME and self.list[1][1] and self.list[1][2]:
                            return int(self.list[1][1]) + int(self.list[1][2])
                        if self.type == self.THIRD_START_TIME and self.list[2][1]:
                            return self.list[2][1]
                        if self.type == self.THIRD_END_TIME and self.list[2][1] and self.list[2][2]:
                            return int(self.list[2][1]) + int(self.list[2][2])
                        return
                    except:
                        return

            return

    @cached
    def getValue(self):
        event = self.source.event
        if event is None:
            return
        else:
            progress = int(time()) - event.getBeginTime()
            duration = event.getDuration()
            if duration > 0 and progress >= 0:
                if progress > duration:
                    progress = duration
                return progress * 1000 / duration
            return
            return

    time = property(getTime)
    value = property(getValue)
    range = 1000

    def changed(self, what):
        Converter.changed(self, what)
        if self.type == self.PROGRESS and len(self.downstream_elements):
            if not self.source.event and self.downstream_elements[0].visible:
                self.downstream_elements[0].visible = False
            elif self.source.event and not self.downstream_elements[0].visible:
                self.downstream_elements[0].visible = True