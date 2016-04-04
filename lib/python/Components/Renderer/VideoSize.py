# Embedded file name: /usr/lib/enigma2/python/Components/Renderer/VideoSize.py
from Components.VariableText import VariableText
from enigma import eLabel, iServiceInformation
from Renderer import Renderer

class VideoSize(Renderer, VariableText):

    def __init__(self):
        Renderer.__init__(self)
        VariableText.__init__(self)

    GUI_WIDGET = eLabel

    def changed(self, what):
        service = self.source.service
        info = service and service.info()
        if info is None:
            self.text = ''
            return
        else:
            xresol = info.getInfo(iServiceInformation.sVideoWidth)
            yresol = info.getInfo(iServiceInformation.sVideoHeight)
            if xresol > 0:
                self.text = str(xresol) + 'x' + str(yresol)
            else:
                self.text = ''
            return