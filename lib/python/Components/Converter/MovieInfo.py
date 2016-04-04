# Embedded file name: /usr/lib/enigma2/python/Components/Converter/MovieInfo.py
from Components.Converter.Converter import Converter
from Components.Element import cached, ElementError
from enigma import iServiceInformation, eServiceReference
from ServiceReference import ServiceReference

class MovieInfo(Converter, object):
    MOVIE_SHORT_DESCRIPTION = 0
    MOVIE_META_DESCRIPTION = 1
    MOVIE_REC_SERVICE_NAME = 2
    MOVIE_REC_SERVICE_REF = 3
    MOVIE_REC_FILESIZE = 4

    def __init__(self, type):
        if type == 'ShortDescription':
            self.type = self.MOVIE_SHORT_DESCRIPTION
        elif type == 'MetaDescription':
            self.type = self.MOVIE_META_DESCRIPTION
        elif type == 'RecordServiceName':
            self.type = self.MOVIE_REC_SERVICE_NAME
        elif type == 'FileSize':
            self.type = self.MOVIE_REC_FILESIZE
        elif type == 'RecordServiceRef':
            self.type = self.MOVIE_REC_SERVICE_REF
        else:
            raise ElementError("'%s' is not <ShortDescription|MetaDescription|RecordServiceName|FileSize> for MovieInfo converter" % type)
        Converter.__init__(self, type)

    @cached
    def getText(self):
        service = self.source.service
        info = self.source.info
        event = self.source.event
        if info and service:
            if self.type == self.MOVIE_SHORT_DESCRIPTION:
                if service.flags & eServiceReference.flagDirectory == eServiceReference.flagDirectory:
                    return service.getPath()
                return info.getInfoString(service, iServiceInformation.sDescription) or event and event.getShortDescription() or service.getPath()
            if self.type == self.MOVIE_META_DESCRIPTION:
                return event and (event.getExtendedDescription() or event.getShortDescription()) or info.getInfoString(service, iServiceInformation.sDescription) or service.getPath()
            if self.type == self.MOVIE_REC_SERVICE_NAME:
                rec_ref_str = info.getInfoString(service, iServiceInformation.sServiceref)
                return ServiceReference(rec_ref_str).getServiceName()
            if self.type == self.MOVIE_REC_SERVICE_REF:
                rec_ref_str = info.getInfoString(service, iServiceInformation.sServiceref)
                return str(ServiceReference(rec_ref_str))
            if self.type == self.MOVIE_REC_FILESIZE:
                if service.flags & eServiceReference.flagDirectory == eServiceReference.flagDirectory:
                    return _('Directory')
                filesize = info.getInfoObject(service, iServiceInformation.sFileSize)
                if filesize is not None:
                    if filesize >= 104857600000L:
                        return _('%.0f GB') % (filesize / 1073741824.0)
                    else:
                        return _('%.0f MB') % (filesize / 1048576.0)
        return ''

    text = property(getText)