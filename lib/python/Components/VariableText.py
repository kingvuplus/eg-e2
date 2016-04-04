# Embedded file name: /usr/lib/enigma2/python/Components/VariableText.py


class VariableText(object):

    def __init__(self):
        object.__init__(self)
        self.message = ''
        self.instance = None
        return

    def setText(self, text):
        try:
            self.message = text
            if self.instance:
                self.instance.setText(self.message or '')
        except:
            self.message = ''
            self.instance.setText(self.message or '')

    def setMarkedPos(self, pos):
        if self.instance:
            self.instance.setMarkedPos(int(pos))

    def getText(self):
        return self.message

    text = property(getText, setText)

    def postWidgetCreate(self, instance):
        try:
            instance.setText(self.message or '')
        except:
            pass