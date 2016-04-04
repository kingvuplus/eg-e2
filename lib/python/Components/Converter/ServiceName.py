# Embedded file name: /usr/lib/enigma2/python/Components/Converter/ServiceName.py
from Components.Converter.Converter import Converter
from Components.config import config
from enigma import iServiceInformation, iPlayableService, iPlayableServicePtr, eServiceReference, eEPGCache, eServiceCenter
from ServiceReference import resolveAlternate
from Components.Element import cached
from Tools.Directories import fileExists

class ServiceName(Converter, object):
    NAME = 0
    NAME_ONLY = 1
    NAME_EVENT = 2
    PROVIDER = 3
    REFERENCE = 4
    EDITREFERENCE = 5
    SID = 6
    TRANSPONDER = 7

    def __init__(self, type):
        Converter.__init__(self, type)
        self.epgQuery = eEPGCache.getInstance().lookupEventTime
        self.mode = ''
        if ';' in type:
            type, self.mode = type.split(';')
        if type == 'Provider':
            self.type = self.PROVIDER
        elif type == 'Reference':
            self.type = self.REFERENCE
        elif type == 'EditReference':
            self.type = self.EDITREFERENCE
        elif type == 'NameOnly':
            self.type = self.NAME_ONLY
        elif type == 'NameAndEvent':
            self.type = self.NAME_EVENT
        elif type == 'Sid':
            self.type = self.SID
        elif type == 'TransponderInfo':
            self.type = self.TRANSPONDER
        else:
            self.type = self.NAME

    @cached
    def getText(self):
        service = self.source.service
        info = None
        if isinstance(service, eServiceReference):
            info = self.source.info
        elif isinstance(service, iPlayableServicePtr):
            info = service and service.info()
            service = None
        if not info:
            return ''
        else:
            if self.type == self.NAME or self.type == self.NAME_ONLY or self.type == self.NAME_EVENT:
                name = service and info.getName(service)
                if name is None:
                    name = info.getName()
                name = name.replace('\xc2\x86', '').replace('\xc2\x87', '')
                if self.type == self.NAME_EVENT:
                    act_event = info and info.getEvent(0)
                    if not act_event and info:
                        refstr = info.getInfoString(iServiceInformation.sServiceref)
                        act_event = self.epgQuery(eServiceReference(refstr), -1, 0)
                    if act_event is None:
                        return '%s - ' % name
                    else:
                        return '%s - %s' % (name, act_event.getEventName())
                elif self.type != self.NAME_ONLY and config.usage.show_infobar_channel_number.value and hasattr(self.source, 'serviceref') and self.source.serviceref and '0:0:0:0:0:0:0:0:0' not in self.source.serviceref.toString():
                    numservice = self.source.serviceref
                    num = numservice and numservice.getChannelNum() or None
                    if num is not None:
                        return str(num) + '   ' + name
                    else:
                        return name
                else:
                    return name
            else:
                if self.type == self.PROVIDER:
                    return info.getInfoString(iServiceInformation.sProvider)
                if self.type == self.REFERENCE or self.type == self.EDITREFERENCE and hasattr(self.source, 'editmode') and self.source.editmode:
                    if not service:
                        refstr = info.getInfoString(iServiceInformation.sServiceref)
                        path = refstr and eServiceReference(refstr).getPath()
                        if path and fileExists('%s.meta' % path):
                            fd = open('%s.meta' % path, 'r')
                            refstr = fd.readline().strip()
                            fd.close()
                        return refstr
                    nref = resolveAlternate(service)
                    if nref:
                        service = nref
                    return service.toString()
                if self.type == self.SID:
                    if service is None:
                        tmpref = info.getInfoString(iServiceInformation.sServiceref)
                    else:
                        tmpref = service.toString()
                    if tmpref:
                        refsplit = tmpref.split(':')
                        if len(refsplit) >= 3:
                            return refsplit[3]
                        else:
                            return tmpref
                    else:
                        return 'N/A'
                elif self.type == self.TRANSPONDER:
                    if service:
                        nref = resolveAlternate(service)
                        if nref:
                            service = nref
                            info = eServiceCenter.getInstance().info(service)
                        transponder_info = info.getInfoObject(service, iServiceInformation.sTransponderData)
                    else:
                        transponder_info = info.getInfoObject(iServiceInformation.sTransponderData)
                    if 'InRootOnly' in self.mode and not self.rootBouquet():
                        return ''
                    if 'NoRoot' in self.mode and self.rootBouquet():
                        return ''
                    if transponder_info:
                        self.t_info = ConvertToHumanReadable(transponder_info)
                        if self.system() == None:
                            return ''
                        if 'DVB-T' in self.system():
                            return self.dvb_t()
                        if 'DVB-C' in self.system():
                            return self.dvb_c()
                        return self.dvb_s()
                    if service:
                        result = service.toString()
                    else:
                        result = info.getInfoString(iServiceInformation.sServiceref)
                    if '%3a//' in result:
                        return result.rsplit('%3a//', 1)[1].split('/')[0]
                    return ''
            return

    text = property(getText)

    def changed(self, what):
        if what[0] != self.CHANGED_SPECIFIC or what[1] in (iPlayableService.evStart,):
            Converter.changed(self, what)