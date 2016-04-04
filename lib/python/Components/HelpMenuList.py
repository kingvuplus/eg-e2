# Embedded file name: /usr/lib/enigma2/python/Components/HelpMenuList.py
from GUIComponent import GUIComponent
from enigma import eListboxPythonMultiContent, eListbox, gFont
from Tools.KeyBindings import queryKeyBinding, getKeyDescription
import skin

class HelpMenuList(GUIComponent):

    def __init__(self, helplist, callback):
        GUIComponent.__init__(self)
        self.onSelChanged = []
        self.l = eListboxPythonMultiContent()
        self.callback = callback
        self.extendedHelp = False
        l = []
        for actionmap, context, actions in helplist:
            for action, help in actions:
                if hasattr(help, '__call__'):
                    help = help()
                if not help:
                    continue
                buttons = queryKeyBinding(context, action)
                if not len(buttons):
                    continue
                name = None
                flags = 0
                for n in buttons:
                    name, flags = getKeyDescription(n[0]), n[1]
                    if name is not None:
                        break

                if name is None:
                    continue
                if flags & 8:
                    name = (name[0], 'long')
                entry = [(actionmap,
                  context,
                  action,
                  name)]
                if isinstance(help, list):
                    self.extendedHelp = True
                    print 'extendedHelpEntry found'
                    x, y, w, h = skin.parameters.get('HelpMenuListExtHlp0', (0, 0, 600, 26))
                    x1, y1, w1, h1 = skin.parameters.get('HelpMenuListExtHlp1', (0, 28, 600, 20))
                    entry.extend(((eListboxPythonMultiContent.TYPE_TEXT,
                      x,
                      y,
                      w,
                      h,
                      0,
                      0,
                      help[0]), (eListboxPythonMultiContent.TYPE_TEXT,
                      x1,
                      y1,
                      w1,
                      h1,
                      1,
                      0,
                      help[1])))
                else:
                    x, y, w, h = skin.parameters.get('HelpMenuListHlp', (0, 0, 600, 28))
                    entry.append((eListboxPythonMultiContent.TYPE_TEXT,
                     x,
                     y,
                     w,
                     h,
                     0,
                     0,
                     help))
                l.append(entry)

        self.l.setList(l)
        if self.extendedHelp is True:
            font = skin.fonts.get('HelpMenuListExt0', ('Regular', 24, 50))
            self.l.setFont(0, gFont(font[0], font[1]))
            self.l.setItemHeight(font[2])
            font = skin.fonts.get('HelpMenuListExt1', ('Regular', 18))
            self.l.setFont(1, gFont(font[0], font[1]))
        else:
            font = skin.fonts.get('HelpMenuList', ('Regular', 24, 38))
            self.l.setFont(0, gFont(font[0], font[1]))
            self.l.setItemHeight(font[2])
        return

    def ok(self):
        l = self.getCurrent()
        if l is None:
            return
        else:
            self.callback(l[0], l[1], l[2])
            return

    def getCurrent(self):
        sel = self.l.getCurrentSelection()
        return sel and sel[0]

    GUI_WIDGET = eListbox

    def postWidgetCreate(self, instance):
        instance.setContent(self.l)
        instance.selectionChanged.get().append(self.selectionChanged)
        self.instance.setWrapAround(True)

    def preWidgetRemove(self, instance):
        instance.setContent(None)
        instance.selectionChanged.get().remove(self.selectionChanged)
        return

    def selectionChanged(self):
        for x in self.onSelChanged:
            x()