# Embedded file name: /usr/lib/enigma2/python/Components/Converter/Streaming.py
from Converter import Converter
from Components.Element import cached

class Streaming(Converter):

    @cached
    def getText(self):
        service = self.source.service
        if service is None:
            return '-NO SERVICE\n'
        else:
            streaming = service.stream()
            s = streaming and streaming.getStreamingData()
            if s is None or not any(s):
                err = service.getError()
                if err:
                    return '-SERVICE ERROR:%d\n' % err
                else:
                    return '=NO STREAM\n'
            demux = s['demux']
            pids = ','.join([ '%x:%s' % (x[0], x[1]) for x in s['pids'] ])
            return '+%d:%s\n' % (demux, pids)

    text = property(getText)