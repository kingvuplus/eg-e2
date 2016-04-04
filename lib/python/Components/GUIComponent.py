# Embedded file name: /usr/lib/enigma2/python/Components/GUIComponent.py
import skin
from enigma import ePoint, eSize

class GUIComponent(object):

    def __init__(self):
        self.instance = None
        self.onVisibilityChange = []
        self.__visible = 0
        self.visible = 1
        self.skinAttributes = None
        self.deprecationInfo = None
        return

    def execBegin(self):
        pass

    def execEnd(self):
        pass

    def onShow(self):
        pass

    def onHide(self):
        pass

    def destroy(self):
        self.__dict__.clear()

    def applySkin(self, desktop, parent):
        if not self.visible:
            self.instance.hide()
        if self.skinAttributes is None:
            return False
        else:
            skin.applyAllAttributes(self.instance, desktop, self.skinAttributes, parent.scale)
            return True

    def move(self, x, y = None):
        if y is None:
            self.instance.move(x)
        else:
            self.instance.move(ePoint(int(x), int(y)))
        return

    def resize(self, x, y = None):
        self.width = x
        self.height = y
        if y is None:
            self.instance.resize(x)
        else:
            self.instance.resize(eSize(int(x), int(y)))
        return

    def setZPosition(self, z):
        self.instance.setZPosition(z)

    def show(self):
        old = self.__visible
        self.__visible = 1
        if self.instance is not None:
            self.instance.show()
        if old != self.__visible:
            for fnc in self.onVisibilityChange:
                fnc(True)

        return

    def hide(self):
        old = self.__visible
        self.__visible = 0
        if self.instance is not None:
            self.instance.hide()
        if old != self.__visible:
            for fnc in self.onVisibilityChange:
                fnc(False)

        return

    def getVisible(self):
        return self.__visible

    def setVisible(self, visible):
        if visible:
            self.show()
        else:
            self.hide()

    visible = property(getVisible, setVisible)

    def setPosition(self, x, y):
        self.instance.move(ePoint(int(x), int(y)))

    def getPosition(self):
        p = self.instance.position()
        return (p.x(), p.y())

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

    position = property(getPosition, setPosition)

    def GUIcreate(self, parent):
        self.instance = self.createWidget(parent)
        self.postWidgetCreate(self.instance)

    def GUIdelete(self):
        self.preWidgetRemove(self.instance)
        self.instance = None
        return

    def createWidget(self, parent):
        return self.GUI_WIDGET(parent)

    def postWidgetCreate(self, instance):
        pass

    def preWidgetRemove(self, instance):
        pass