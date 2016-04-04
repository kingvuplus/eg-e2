# Embedded file name: /usr/lib/enigma2/python/Components/config.py
from enigma import getPrevAsciiCode
from Tools.NumericalTextInput import NumericalTextInput
from Tools.Directories import resolveFilename, SCOPE_CONFIG, fileExists
from Components.Harddisk import harddiskmanager
from Tools.LoadPixmap import LoadPixmap
import copy
import os
from time import localtime, strftime

class ConfigElement(object):

    def __init__(self):
        self.extra_args = {}
        self.saved_value = None
        self.save_forced = False
        self.last_value = None
        self.save_disabled = False
        self.__notifiers = {}
        self.__notifiers_final = {}
        self.enabled = True
        self.callNotifiersOnSaveAndCancel = False
        return

    def getNotifiers(self):
        return [ func for func, val, call_on_save_and_cancel in self.__notifiers.itervalues() ]

    def setNotifiers(self, val):
        print 'just readonly access to notifiers is allowed! append/remove doesnt work anymore! please use addNotifier, removeNotifier, clearNotifiers'

    notifiers = property(getNotifiers, setNotifiers)

    def getNotifiersFinal(self):
        return [ func for func, val, call_on_save_and_cancel in self.__notifiers_final.itervalues() ]

    def setNotifiersFinal(self, val):
        print 'just readonly access to notifiers_final is allowed! append/remove doesnt work anymore! please use addNotifier, removeNotifier, clearNotifiers'

    notifiers_final = property(getNotifiersFinal, setNotifiersFinal)

    def setValue(self, value):
        self._value = value
        self.changed()

    def getValue(self):
        return self._value

    value = property(getValue, setValue)

    def fromstring(self, value):
        return value

    def load(self):
        sv = self.saved_value
        if sv is None:
            self.value = self.default
        else:
            self.value = self.fromstring(sv)
        return

    def tostring(self, value):
        return str(value)

    def save(self):
        if self.save_disabled or self.value == self.default and not self.save_forced:
            self.saved_value = None
        else:
            self.saved_value = self.tostring(self.value)
        if self.callNotifiersOnSaveAndCancel:
            self.changed()
        return

    def cancel(self):
        self.load()
        if self.callNotifiersOnSaveAndCancel:
            self.changed()

    def isChanged(self):
        sv = self.saved_value
        if sv is None and self.value == self.default:
            return False
        else:
            return self.tostring(self.value) != sv

    def changed(self):
        if self.__notifiers:
            for x in self.notifiers:
                try:
                    if self.extra_args and self.extra_args[x]:
                        x(self, self.extra_args[x])
                    else:
                        x(self)
                except:
                    x(self)

    def changedFinal(self):
        if self.__notifiers_final:
            for x in self.notifiers_final:
                try:
                    if self.extra_args and self.extra_args[x]:
                        x(self, self.extra_args[x])
                    else:
                        x(self)
                except:
                    x(self)

    def addNotifier(self, notifier, initial_call = True, immediate_feedback = True, call_on_save_or_cancel = False, extra_args = None):
        if not extra_args:
            extra_args = []
        try:
            self.extra_args[notifier] = extra_args
        except:
            pass

        if immediate_feedback:
            self.__notifiers[str(notifier)] = (notifier, self.value, call_on_save_or_cancel)
        else:
            self.__notifiers_final[str(notifier)] = (notifier, self.value, call_on_save_or_cancel)
        if initial_call:
            if extra_args:
                notifier(self, extra_args)
            else:
                notifier(self)

    def removeNotifier(self, notifier):
        try:
            del self.__notifiers[str(notifier)]
        except:
            try:
                del self.__notifiers_final[str(notifier)]
            except:
                pass

    def disableSave(self):
        self.save_disabled = True

    def __call__(self, selected):
        return self.getMulti(selected)

    def onSelect(self, session):
        pass

    def onDeselect(self, session):
        if not self.last_value == self.value:
            self.changedFinal()
            self.last_value = self.value


KEY_LEFT = 0
KEY_RIGHT = 1
KEY_OK = 2
KEY_DELETE = 3
KEY_BACKSPACE = 4
KEY_HOME = 5
KEY_END = 6
KEY_TOGGLEOW = 7
KEY_ASCII = 8
KEY_TIMEOUT = 9
KEY_NUMBERS = range(12, 22)
KEY_0 = 12
KEY_9 = 21

def getKeyNumber(key):
    return key - KEY_0


class choicesList(object):
    LIST_TYPE_LIST = 1
    LIST_TYPE_DICT = 2

    def __init__(self, choices, type = None):
        self.choices = choices
        if type is None:
            if isinstance(choices, list):
                self.type = choicesList.LIST_TYPE_LIST
            elif isinstance(choices, dict):
                self.type = choicesList.LIST_TYPE_DICT
        else:
            self.type = type
        return

    def __list__(self):
        if self.type == choicesList.LIST_TYPE_LIST:
            ret = [ not isinstance(x, tuple) and x or x[0] for x in self.choices ]
        else:
            ret = self.choices.keys()
        return ret or ['']

    def __iter__(self):
        if self.type == choicesList.LIST_TYPE_LIST:
            ret = [ not isinstance(x, tuple) and x or x[0] for x in self.choices ]
        else:
            ret = self.choices
        return iter(ret or [''])

    def __len__(self):
        return len(self.choices) or 1

    def updateItemDescription(self, index, descr):
        if self.type == choicesList.LIST_TYPE_LIST:
            orig = self.choices[index]
            self.choices[index] = (orig[0], descr)
        else:
            key = self.choices.keys()[index]
            self.choices[key] = descr

    def __getitem__(self, index):
        if self.type == choicesList.LIST_TYPE_LIST:
            ret = self.choices[index]
            if isinstance(ret, tuple):
                ret = ret[0]
            return ret
        return self.choices.keys()[index]

    def index(self, value):
        try:
            return self.__list__().index(value)
        except (ValueError, IndexError):
            return 0

    def __setitem__(self, index, value):
        if self.type == choicesList.LIST_TYPE_LIST:
            orig = self.choices[index]
            if isinstance(orig, tuple):
                self.choices[index] = (value, orig[1])
            else:
                self.choices[index] = value
        else:
            key = self.choices.keys()[index]
            orig = self.choices[key]
            del self.choices[key]
            self.choices[value] = orig

    def default(self):
        choices = self.choices
        if not choices:
            return ''
        if self.type is choicesList.LIST_TYPE_LIST:
            default = choices[0]
            if isinstance(default, tuple):
                default = default[0]
        else:
            default = choices.keys()[0]
        return default


class descriptionList(choicesList):

    def __list__(self):
        if self.type == choicesList.LIST_TYPE_LIST:
            ret = [ not isinstance(x, tuple) and x or x[1] for x in self.choices ]
        else:
            ret = self.choices.values()
        return ret or ['']

    def __iter__(self):
        return iter(self.__list__())

    def __getitem__(self, index):
        if self.type == choicesList.LIST_TYPE_LIST:
            for x in self.choices:
                if isinstance(x, tuple):
                    if x[0] == index:
                        return str(x[1])
                elif x == index:
                    return str(x)

            return str(index)
        else:
            return str(self.choices.get(index, ''))

    def __setitem__(self, index, value):
        if self.type == choicesList.LIST_TYPE_LIST:
            i = self.index(index)
            orig = self.choices[i]
            if isinstance(orig, tuple):
                self.choices[i] = (orig[0], value)
            else:
                self.choices[i] = value
        else:
            self.choices[index] = value


class ConfigSelection(ConfigElement):

    def __init__(self, choices, default = None):
        ConfigElement.__init__(self)
        self.choices = choicesList(choices)
        if default is None:
            default = self.choices.default()
        self._descr = None
        self.default = self._value = self.last_value = default
        return

    def setChoices(self, choices, default = None):
        self.choices = choicesList(choices)
        if default is None:
            default = self.choices.default()
        self.default = default
        if self.value not in self.choices:
            self.value = default
        return

    def setValue(self, value):
        if value in self.choices:
            self._value = value
        else:
            self._value = self.default
        self._descr = None
        self.changed()
        return

    def tostring(self, val):
        return val

    def getValue(self):
        return self._value

    def setCurrentText(self, text):
        i = self.choices.index(self.value)
        self.choices[i] = text
        self._descr = self.description[text] = text
        self._value = text

    value = property(getValue, setValue)

    def getIndex(self):
        return self.choices.index(self.value)

    index = property(getIndex)

    def handleKey(self, key):
        nchoices = len(self.choices)
        if nchoices > 1:
            i = self.choices.index(self.value)
            if key == KEY_LEFT:
                self.value = self.choices[(i + nchoices - 1) % nchoices]
            elif key == KEY_RIGHT:
                self.value = self.choices[(i + 1) % nchoices]
            elif key == KEY_HOME:
                self.value = self.choices[0]
            elif key == KEY_END:
                self.value = self.choices[nchoices - 1]

    def selectNext(self):
        nchoices = len(self.choices)
        i = self.choices.index(self.value)
        self.value = self.choices[(i + 1) % nchoices]

    def getText(self):
        if self._descr is not None:
            return self._descr
        else:
            descr = self._descr = self.description[self.value]
            if descr:
                return _(descr)
            return descr

    def getMulti(self, selected):
        if self._descr is not None:
            descr = self._descr
        else:
            descr = self._descr = self.description[self.value]
        if descr:
            return ('text', _(descr))
        else:
            return ('text', descr)

    def getHTML(self, id):
        res = ''
        for v in self.choices:
            descr = self.description[v]
            if self.value == v:
                checked = 'checked="checked" '
            else:
                checked = ''
            res += '<input type="radio" name="' + id + '" ' + checked + 'value="' + v + '">' + descr + '</input></br>\n'

        return res

    def unsafeAssign(self, value):
        self.value = value

    description = property(lambda self: descriptionList(self.choices.choices, self.choices.type))


boolean_descriptions = {False: _('false'),
 True: _('true')}

class ConfigBoolean(ConfigElement):

    def __init__(self, default = False, descriptions = boolean_descriptions, grafic = True):
        ConfigElement.__init__(self)
        self.descriptions = descriptions
        self.value = self.last_value = self.default = default
        self.grafic = False
        if grafic:
            from skin import switchPixmap
            offPath = switchPixmap.get('menu_off')
            onPath = switchPixmap.get('menu_on')
            if offPath and onPath:
                falseIcon = LoadPixmap(cached=True, path=offPath)
                trueIcon = LoadPixmap(cached=True, path=onPath)
                if falseIcon and trueIcon:
                    self.falseIcon = falseIcon
                    self.trueIcon = trueIcon
                    self.grafic = True

    def handleKey(self, key):
        if key in (KEY_LEFT, KEY_RIGHT):
            self.value = not self.value
        elif key == KEY_HOME:
            self.value = False
        elif key == KEY_END:
            self.value = True

    def getText(self):
        descr = self.descriptions[self.value]
        if descr:
            return _(descr)
        return descr

    def getMulti(self, selected):
        from config import config
        if self.grafic and config.usage.boolean_graphic.value:
            if self.value:
                return ('bolean', self.trueIcon)
            else:
                return ('bolean', self.falseIcon)
        else:
            return ('text', self.getText())

    def tostring(self, value):
        if not value:
            return 'false'
        else:
            return 'true'

    def fromstring(self, val):
        if val == 'true':
            return True
        else:
            return False

    def getHTML(self, id):
        if self.value:
            checked = ' checked="checked"'
        else:
            checked = ''
        return '<input type="checkbox" name="' + id + '" value="1" ' + checked + ' />'

    def unsafeAssign(self, value):
        if value == '1':
            self.value = True
        else:
            self.value = False

    def onDeselect(self, session):
        if not self.last_value == self.value:
            self.changedFinal()
            self.last_value = self.value


yes_no_descriptions = {False: _('no'),
 True: _('yes')}

class ConfigYesNo(ConfigBoolean):

    def __init__(self, default = False):
        ConfigBoolean.__init__(self, default=default, descriptions=yes_no_descriptions)


on_off_descriptions = {False: _('off'),
 True: _('on')}

class ConfigOnOff(ConfigBoolean):

    def __init__(self, default = False):
        ConfigBoolean.__init__(self, default=default, descriptions=on_off_descriptions)


enable_disable_descriptions = {False: _('disable'),
 True: _('enable')}

class ConfigEnableDisable(ConfigBoolean):

    def __init__(self, default = False):
        ConfigBoolean.__init__(self, default=default, descriptions=enable_disable_descriptions)


class ConfigDateTime(ConfigElement):

    def __init__(self, default, formatstring, increment = 86400):
        ConfigElement.__init__(self)
        self.increment = increment
        self.formatstring = formatstring
        self.value = self.last_value = self.default = int(default)

    def handleKey(self, key):
        if key == KEY_LEFT:
            self.value -= self.increment
        elif key == KEY_RIGHT:
            self.value += self.increment
        elif key == KEY_HOME or key == KEY_END:
            self.value = self.default

    def getText(self):
        return strftime(self.formatstring, localtime(self.value))

    def getMulti(self, selected):
        return ('text', strftime(self.formatstring, localtime(self.value)))

    def fromstring(self, val):
        return int(val)


class ConfigSequence(ConfigElement):

    def __init__(self, seperator, limits, default, censor_char = ''):
        ConfigElement.__init__(self)
        self.marked_pos = 0
        self.seperator = seperator
        self.limits = limits
        self.censor_char = censor_char
        self.last_value = self.default = default
        self.value = copy.copy(default)
        self.endNotifier = None
        return

    def validate(self):
        max_pos = 0
        num = 0
        for i in self._value:
            max_pos += len(str(self.limits[num][1]))
            if self._value[num] < self.limits[num][0]:
                self._value[num] = self.limits[num][0]
            if self._value[num] > self.limits[num][1]:
                self._value[num] = self.limits[num][1]
            num += 1

        if self.marked_pos >= max_pos:
            if self.endNotifier:
                for x in self.endNotifier:
                    x(self)

            self.marked_pos = max_pos - 1
        if self.marked_pos < 0:
            self.marked_pos = 0

    def validatePos(self):
        if self.marked_pos < 0:
            self.marked_pos = 0
        total_len = sum([ len(str(x[1])) for x in self.limits ])
        if self.marked_pos >= total_len:
            self.marked_pos = total_len - 1

    def addEndNotifier(self, notifier):
        if self.endNotifier is None:
            self.endNotifier = []
        self.endNotifier.append(notifier)
        return

    def handleKey(self, key):
        if key == KEY_LEFT:
            self.marked_pos -= 1
            self.validatePos()
        elif key == KEY_RIGHT:
            self.marked_pos += 1
            self.validatePos()
        elif key == KEY_HOME:
            self.marked_pos = 0
            self.validatePos()
        elif key == KEY_END:
            max_pos = 0
            num = 0
            for i in self._value:
                max_pos += len(str(self.limits[num][1]))
                num += 1

            self.marked_pos = max_pos - 1
            self.validatePos()
        elif key in KEY_NUMBERS or key == KEY_ASCII:
            if key == KEY_ASCII:
                code = getPrevAsciiCode()
                if code < 48 or code > 57:
                    return
                number = code - 48
            else:
                number = getKeyNumber(key)
            block_len = [ len(str(x[1])) for x in self.limits ]
            total_len = sum(block_len)
            pos = 0
            blocknumber = 0
            block_len_total = [0]
            for x in block_len:
                pos += block_len[blocknumber]
                block_len_total.append(pos)
                if pos - 1 >= self.marked_pos:
                    pass
                else:
                    blocknumber += 1

            number_len = len(str(self.limits[blocknumber][1]))
            posinblock = self.marked_pos - block_len_total[blocknumber]
            oldvalue = self._value[blocknumber]
            olddec = oldvalue % 10 ** (number_len - posinblock) - oldvalue % 10 ** (number_len - posinblock - 1)
            newvalue = oldvalue - olddec + 10 ** (number_len - posinblock - 1) * number
            self._value[blocknumber] = newvalue
            self.marked_pos += 1
            self.validate()
            self.changed()

    def genText(self):
        value = ''
        mPos = self.marked_pos
        num = 0
        for i in self._value:
            if value:
                value += self.seperator
                if mPos >= len(value) - 1:
                    mPos += 1
            if self.censor_char == '':
                value += ('%0' + str(len(str(self.limits[num][1]))) + 'd') % i
            else:
                value += self.censor_char * len(str(self.limits[num][1]))
            num += 1

        return (value, mPos)

    def getText(self):
        value, mPos = self.genText()
        return value

    def getMulti(self, selected):
        value, mPos = self.genText()
        if self.enabled:
            return ('mtext'[1 - selected:], value, [mPos])
        else:
            return ('text', value)

    def tostring(self, val):
        return self.seperator.join([ self.saveSingle(x) for x in val ])

    def saveSingle(self, v):
        return str(v)

    def fromstring(self, value):
        return [ int(x) for x in value.split(self.seperator) ]

    def onDeselect(self, session):
        if self.last_value != self._value:
            self.changedFinal()
            self.last_value = copy.copy(self._value)


ip_limits = [(0, 255),
 (0, 255),
 (0, 255),
 (0, 255)]

class ConfigIP(ConfigSequence):

    def __init__(self, default, auto_jump = False):
        ConfigSequence.__init__(self, seperator='.', limits=ip_limits, default=default)
        self.block_len = [ len(str(x[1])) for x in self.limits ]
        self.marked_block = 0
        self.overwrite = True
        self.auto_jump = auto_jump

    def handleKey(self, key):
        if key == KEY_LEFT:
            if self.marked_block > 0:
                self.marked_block -= 1
            self.overwrite = True
        elif key == KEY_RIGHT:
            if self.marked_block < len(self.limits) - 1:
                self.marked_block += 1
            self.overwrite = True
        elif key == KEY_HOME:
            self.marked_block = 0
            self.overwrite = True
        elif key == KEY_END:
            self.marked_block = len(self.limits) - 1
            self.overwrite = True
        elif key in KEY_NUMBERS or key == KEY_ASCII:
            if key == KEY_ASCII:
                code = getPrevAsciiCode()
                if code < 48 or code > 57:
                    return
                number = code - 48
            else:
                number = getKeyNumber(key)
            oldvalue = self._value[self.marked_block]
            if self.overwrite:
                self._value[self.marked_block] = number
                self.overwrite = False
            else:
                oldvalue *= 10
                newvalue = oldvalue + number
                if self.auto_jump and newvalue > self.limits[self.marked_block][1] and self.marked_block < len(self.limits) - 1:
                    self.handleKey(KEY_RIGHT)
                    self.handleKey(key)
                    return
                self._value[self.marked_block] = newvalue
            if len(str(self._value[self.marked_block])) >= self.block_len[self.marked_block]:
                self.handleKey(KEY_RIGHT)
            self.validate()
            self.changed()

    def genText(self):
        value = ''
        block_strlen = []
        for i in self._value:
            block_strlen.append(len(str(i)))
            if value:
                value += self.seperator
            value += str(i)

        leftPos = sum(block_strlen[:self.marked_block]) + self.marked_block
        rightPos = sum(block_strlen[:self.marked_block + 1]) + self.marked_block
        mBlock = range(leftPos, rightPos)
        return (value, mBlock)

    def getMulti(self, selected):
        value, mBlock = self.genText()
        if self.enabled:
            return ('mtext'[1 - selected:], value, mBlock)
        else:
            return ('text', value)

    def getHTML(self, id):
        return '.'.join([ '%d' % d for d in self.value ])


mac_limits = [(1, 255),
 (1, 255),
 (1, 255),
 (1, 255),
 (1, 255),
 (1, 255)]

class ConfigMAC(ConfigSequence):

    def __init__(self, default):
        ConfigSequence.__init__(self, seperator=':', limits=mac_limits, default=default)


class ConfigMacText(ConfigElement, NumericalTextInput):

    def __init__(self, default = '', visible_width = False):
        ConfigElement.__init__(self)
        NumericalTextInput.__init__(self, nextFunc=self.nextFunc, handleTimeout=False)
        self.marked_pos = 0
        self.allmarked = default != ''
        self.fixed_size = 17
        self.visible_width = visible_width
        self.offset = 0
        self.overwrite = 17
        self.help_window = None
        self.value = self.last_value = self.default = default
        self.useableChars = '0123456789ABCDEF'
        return

    def validateMarker(self):
        textlen = len(self.text)
        if self.marked_pos > textlen - 1:
            self.marked_pos = textlen - 1
        elif self.marked_pos < 0:
            self.marked_pos = 0

    def insertChar(self, ch, pos, owr):
        if self.text[pos] == ':':
            pos += 1
        if owr or self.overwrite:
            self.text = self.text[0:pos] + ch + self.text[pos + 1:]
        elif self.fixed_size:
            self.text = self.text[0:pos] + ch + self.text[pos:-1]
        else:
            self.text = self.text[0:pos] + ch + self.text[pos:]

    def handleKey(self, key):
        if key == KEY_LEFT:
            self.timeout()
            if self.allmarked:
                self.marked_pos = len(self.text)
                self.allmarked = False
            elif self.text[self.marked_pos - 1] == ':':
                self.marked_pos -= 2
            else:
                self.marked_pos -= 1
        elif key == KEY_RIGHT:
            self.timeout()
            if self.allmarked:
                self.marked_pos = 0
                self.allmarked = False
            elif self.marked_pos < len(self.text) - 1:
                if self.text[self.marked_pos + 1] == ':':
                    self.marked_pos += 2
                else:
                    self.marked_pos += 1
        elif key in KEY_NUMBERS:
            owr = self.lastKey == getKeyNumber(key)
            newChar = self.getKey(getKeyNumber(key))
            self.insertChar(newChar, self.marked_pos, owr)
        elif key == KEY_TIMEOUT:
            self.timeout()
            if self.help_window:
                self.help_window.update(self)
            if self.text[self.marked_pos] == ':':
                self.marked_pos += 1
            return
        if self.help_window:
            self.help_window.update(self)
        self.validateMarker()
        self.changed()

    def nextFunc(self):
        self.marked_pos += 1
        self.validateMarker()
        self.changed()

    def getValue(self):
        try:
            return self.text.encode('utf-8')
        except UnicodeDecodeError:
            print '[Config] Broken UTF8!'
            return self.text

    def setValue(self, val):
        try:
            self.text = val.decode('utf-8')
        except UnicodeDecodeError:
            self.text = val.decode('utf-8', 'ignore')
            print '[Config] Broken UTF8!'

    value = property(getValue, setValue)
    _value = property(getValue, setValue)

    def getText(self):
        return self.text.encode('utf-8')

    def getMulti(self, selected):
        if self.visible_width:
            if self.allmarked:
                mark = range(0, min(self.visible_width, len(self.text)))
            else:
                mark = [self.marked_pos - self.offset]
            return ('mtext'[1 - selected:], self.text[self.offset:self.offset + self.visible_width].encode('utf-8') + ' ', mark)
        else:
            if self.allmarked:
                mark = range(0, len(self.text))
            else:
                mark = [self.marked_pos]
            return ('mtext'[1 - selected:], self.text.encode('utf-8') + ' ', mark)

    def onSelect(self, session):
        self.allmarked = self.value != ''
        if session is not None:
            from Screens.NumericalTextInputHelpDialog import NumericalTextInputHelpDialog
            self.help_window = session.instantiateDialog(NumericalTextInputHelpDialog, self)
            self.help_window.setAnimationMode(0)
            self.help_window.show()
        return

    def onDeselect(self, session):
        self.marked_pos = 0
        self.offset = 0
        if self.help_window:
            session.deleteDialog(self.help_window)
            self.help_window = None
        if not self.last_value == self.value:
            self.changedFinal()
            self.last_value = self.value
        return

    def getHTML(self, id):
        return '<input type="text" name="' + id + '" value="' + self.value + '" /><br>\n'

    def unsafeAssign(self, value):
        self.value = str(value)


class ConfigPosition(ConfigSequence):

    def __init__(self, default, args):
        ConfigSequence.__init__(self, seperator=',', limits=[(0, args[0]),
         (0, args[1]),
         (0, args[2]),
         (0, args[3])], default=default)


clock_limits = [(0, 23), (0, 59)]

class ConfigClock(ConfigSequence):

    def __init__(self, default):
        t = localtime(default)
        ConfigSequence.__init__(self, seperator=':', limits=clock_limits, default=[t.tm_hour, t.tm_min])

    def increment(self):
        if self._value[1] == 59:
            if self._value[0] < 23:
                self._value[0] += 1
            else:
                self._value[0] = 0
            self._value[1] = 0
        else:
            self._value[1] += 1
        self.changed()

    def decrement(self):
        if self._value[1] == 0:
            if self._value[0] > 0:
                self._value[0] -= 1
            else:
                self._value[0] = 23
            self._value[1] = 59
        else:
            self._value[1] -= 1
        self.changed()


integer_limits = (0, 9999999999L)

class ConfigInteger(ConfigSequence):

    def __init__(self, default, limits = integer_limits):
        ConfigSequence.__init__(self, seperator=':', limits=[limits], default=default)

    def setValue(self, value):
        self._value = [value]
        self.changed()

    def getValue(self):
        return self._value[0]

    value = property(getValue, setValue)

    def fromstring(self, value):
        return int(value)

    def tostring(self, value):
        return str(value)


class ConfigPIN(ConfigInteger):

    def __init__(self, default, len = 4, censor = ''):
        if default == -1:
            default = '1111'
        ConfigSequence.__init__(self, seperator=':', limits=[(0, 10 ** len - 1)], censor_char=censor, default=default)
        self.len = len

    def getLength(self):
        return self.len


class ConfigFloat(ConfigSequence):

    def __init__(self, default, limits):
        ConfigSequence.__init__(self, seperator='.', limits=limits, default=default)

    def getFloat(self):
        return float(self.value[1] / float(self.limits[1][1] + 1) + self.value[0])

    float = property(getFloat)


egkeymap_us_de = {2: [u'1',
     u'!',
     None,
     None],
 3: [u'2',
     u'@',
     None,
     None],
 4: [u'3',
     u'#',
     None,
     '\xc2\xa3'],
 5: [u'4',
     u'$',
     '\xc3\xa7',
     None],
 6: [u'5',
     u'%',
     '\xc3\xbc',
     '\xe2\x82\xac'],
 7: [u'6',
     u'^',
     '\xc3\xb6',
     None],
 8: [u'7',
     u'&',
     '\xc3\xa4',
     None],
 9: [u'8',
     u'*',
     '\xc3\xa0',
     None],
 10: [u'9',
      u'(',
      '\xc3\xa8',
      None],
 11: [u'0',
      u')',
      '\xc3\xa9',
      None],
 12: [u'-',
      u'_',
      None,
      None],
 13: [u'=',
      u'+',
      '~',
      None],
 16: [u'q',
      u'Q',
      None,
      None],
 17: [u'w',
      u'W',
      None,
      None],
 18: [u'e',
      u'E',
      '\xe2\x82\xac',
      None],
 19: [u'r',
      u'R',
      None,
      None],
 20: [u't',
      u'T',
      None,
      None],
 21: [u'y',
      u'Y',
      None,
      None],
 22: [u'u',
      u'U',
      None,
      None],
 23: [u'i',
      u'I',
      None,
      None],
 24: [u'o',
      u'O',
      None,
      None],
 25: [u'p',
      u'P',
      None,
      None],
 26: [u'[',
      u'{',
      None,
      None],
 27: [u']',
      u'}',
      None,
      None],
 30: [u'a',
      u'A',
      None,
      None],
 31: [u's',
      u'S',
      '\xc3\x9f',
      None],
 32: [u'd',
      u'D',
      None,
      None],
 33: [u'f',
      u'F',
      None,
      None],
 34: [u'g',
      u'G',
      None,
      None],
 35: [u'h',
      u'H',
      None,
      None],
 36: [u'j',
      u'J',
      None,
      None],
 37: [u'k',
      u'K',
      None,
      None],
 38: [u'l',
      u'L',
      None,
      None],
 39: [u';',
      u':',
      None,
      None],
 40: [u"'",
      u'"',
      None,
      None],
 41: ['\xc2\xa7',
      '\xc2\xb0',
      '\xc2\xac',
      None],
 43: [u'\\',
      u'|',
      None,
      None],
 44: [u'z',
      u'Z',
      None,
      u'<'],
 45: [u'x',
      u'X',
      None,
      u'>'],
 46: [u'c',
      u'C',
      '\xc2\xa2',
      None],
 47: [u'v',
      u'V',
      None,
      None],
 48: [u'b',
      u'B',
      None,
      None],
 49: [u'n',
      u'N',
      None,
      None],
 50: [u'm',
      u'M',
      '\xc2\xb5',
      None],
 51: [u',',
      '<',
      None,
      None],
 52: [u'.',
      '>',
      None,
      None],
 53: [u'/',
      u'?',
      None,
      None],
 57: [u' ',
      None,
      None,
      None]}
egmapidx = 0
egkeymap = egkeymap_us_de
rckeyboard_enable = False

def getCharValue(code):
    global egmapidx
    global egkeymap
    global rckeyboard_enable
    print 'got ascii code : %d [%d]' % (code, egmapidx)
    if rckeyboard_enable:
        if code == 0:
            egmapidx = 0
            return None
        if code == 42:
            egmapidx += 1
            return None
        if code == 56:
            egmapidx += 3
            return None
        if code == 100:
            egmapidx += 2
            return None
        try:
            return egkeymap[code][egmapidx]
        except:
            return None

    else:
        return unichr(getPrevAsciiCode())
    return None


class ConfigText(ConfigElement, NumericalTextInput):

    def __init__(self, default = '', fixed_size = True, visible_width = False):
        ConfigElement.__init__(self)
        NumericalTextInput.__init__(self, nextFunc=self.nextFunc, handleTimeout=False)
        self.marked_pos = 0
        self.allmarked = default != ''
        self.fixed_size = fixed_size
        self.visible_width = visible_width
        self.offset = 0
        self.overwrite = fixed_size
        self.help_window = None
        self.value = self.last_value = self.default = default
        return

    def validateMarker(self):
        textlen = len(self.text)
        if self.fixed_size:
            if self.marked_pos > textlen - 1:
                self.marked_pos = textlen - 1
        elif self.marked_pos > textlen:
            self.marked_pos = textlen
        if self.marked_pos < 0:
            self.marked_pos = 0
        if self.visible_width:
            if self.marked_pos < self.offset:
                self.offset = self.marked_pos
            if self.marked_pos >= self.offset + self.visible_width:
                if self.marked_pos == textlen:
                    self.offset = self.marked_pos - self.visible_width
                else:
                    self.offset = self.marked_pos - self.visible_width + 1
            if self.offset > 0 and self.offset + self.visible_width > textlen:
                self.offset = max(0, len - self.visible_width)

    def insertChar(self, ch, pos, owr):
        if owr or self.overwrite:
            self.text = self.text[0:pos] + ch + self.text[pos + 1:]
        elif self.fixed_size:
            self.text = self.text[0:pos] + ch + self.text[pos:-1]
        else:
            self.text = self.text[0:pos] + ch + self.text[pos:]

    def deleteChar(self, pos):
        if not self.fixed_size:
            self.text = self.text[0:pos] + self.text[pos + 1:]
        elif self.overwrite:
            self.text = self.text[0:pos] + ' ' + self.text[pos + 1:]
        else:
            self.text = self.text[0:pos] + self.text[pos + 1:] + ' '

    def deleteAllChars(self):
        if self.fixed_size:
            self.text = ' ' * len(self.text)
        else:
            self.text = ''
        self.marked_pos = 0

    def handleKey(self, key):
        if key == KEY_DELETE:
            self.timeout()
            if self.allmarked:
                self.deleteAllChars()
                self.allmarked = False
            else:
                self.deleteChar(self.marked_pos)
                if self.fixed_size and self.overwrite:
                    self.marked_pos += 1
        elif key == KEY_BACKSPACE:
            self.timeout()
            if self.allmarked:
                self.deleteAllChars()
                self.allmarked = False
            elif self.marked_pos > 0:
                self.deleteChar(self.marked_pos - 1)
                if not self.fixed_size and self.offset > 0:
                    self.offset -= 1
                self.marked_pos -= 1
        elif key == KEY_LEFT:
            self.timeout()
            if self.allmarked:
                self.marked_pos = len(self.text)
                self.allmarked = False
            else:
                self.marked_pos -= 1
        elif key == KEY_RIGHT:
            self.timeout()
            if self.allmarked:
                self.marked_pos = 0
                self.allmarked = False
            else:
                self.marked_pos += 1
        elif key == KEY_HOME:
            self.timeout()
            self.allmarked = False
            self.marked_pos = 0
        elif key == KEY_END:
            self.timeout()
            self.allmarked = False
            self.marked_pos = len(self.text)
        elif key == KEY_TOGGLEOW:
            self.timeout()
            self.overwrite = not self.overwrite
        elif key == KEY_ASCII:
            self.timeout()
            newChar = unichr(getPrevAsciiCode())
            if not self.useableChars or newChar in self.useableChars:
                if self.allmarked:
                    self.deleteAllChars()
                    self.allmarked = False
                self.insertChar(newChar, self.marked_pos, False)
                self.marked_pos += 1
        elif key in KEY_NUMBERS:
            owr = self.lastKey == getKeyNumber(key)
            newChar = self.getKey(getKeyNumber(key))
            if self.allmarked:
                self.deleteAllChars()
                self.allmarked = False
            self.insertChar(newChar, self.marked_pos, owr)
        elif key == KEY_TIMEOUT:
            self.timeout()
            if self.help_window:
                self.help_window.update(self)
            return
        if self.help_window:
            self.help_window.update(self)
        self.validateMarker()
        self.changed()

    def nextFunc(self):
        self.marked_pos += 1
        self.validateMarker()
        self.changed()

    def getValue(self):
        try:
            return self.text.encode('utf-8')
        except UnicodeDecodeError:
            print '[Config] Broken UTF8!'
            return self.text

    def setValue(self, val):
        try:
            self.text = val.decode('utf-8')
        except UnicodeDecodeError:
            self.text = val.decode('utf-8', 'ignore')
            print '[Config] Broken UTF8!'

    value = property(getValue, setValue)
    _value = property(getValue, setValue)

    def getText(self):
        return self.text.encode('utf-8')

    def getMulti(self, selected):
        if self.visible_width:
            if self.allmarked:
                mark = range(0, min(self.visible_width, len(self.text)))
            else:
                mark = [self.marked_pos - self.offset]
            return ('mtext'[1 - selected:], self.text[self.offset:self.offset + self.visible_width].encode('utf-8') + ' ', mark)
        else:
            if self.allmarked:
                mark = range(0, len(self.text))
            else:
                mark = [self.marked_pos]
            return ('mtext'[1 - selected:], self.text.encode('utf-8') + ' ', mark)

    def onSelect(self, session):
        self.allmarked = self.value != ''
        if session is not None:
            from Screens.NumericalTextInputHelpDialog import NumericalTextInputHelpDialog
            self.help_window = session.instantiateDialog(NumericalTextInputHelpDialog, self)
            self.help_window.setAnimationMode(0)
            self.help_window.show()
        return

    def onDeselect(self, session):
        self.marked_pos = 0
        self.offset = 0
        if self.help_window:
            session.deleteDialog(self.help_window)
            self.help_window = None
        if not self.last_value == self.value:
            self.changedFinal()
            self.last_value = self.value
        return

    def getHTML(self, id):
        return '<input type="text" name="' + id + '" value="' + self.value + '" /><br>\n'

    def unsafeAssign(self, value):
        self.value = str(value)


class ConfigPassword(ConfigText):

    def __init__(self, default = '', fixed_size = False, visible_width = False, censor = '*'):
        ConfigText.__init__(self, default=default, fixed_size=fixed_size, visible_width=visible_width)
        self.censor_char = censor
        self.hidden = True

    def getMulti(self, selected):
        mtext, text, mark = ConfigText.getMulti(self, selected)
        if self.hidden:
            text = len(text) * self.censor_char
        return (mtext, text, mark)

    def onSelect(self, session):
        ConfigText.onSelect(self, session)
        self.hidden = False

    def onDeselect(self, session):
        ConfigText.onDeselect(self, session)
        self.hidden = True


class ConfigSelectionNumber(ConfigSelection):

    def __init__(self, min, max, stepwidth, default = None, wraparound = False):
        self.wraparound = wraparound
        if default is None:
            default = min
        default = str(default)
        choices = []
        step = min
        while step <= max:
            choices.append(str(step))
            step += stepwidth

        ConfigSelection.__init__(self, choices, default)
        return

    def getValue(self):
        return int(ConfigSelection.getValue(self))

    def setValue(self, val):
        ConfigSelection.setValue(self, str(val))

    value = property(getValue, setValue)

    def getIndex(self):
        return self.choices.index(self.value)

    index = property(getIndex)

    def isChanged(self):
        sv = self.saved_value
        strv = str(self.tostring(self.value))
        if sv is None and strv == str(self.default):
            return False
        else:
            return strv != str(sv)

    def handleKey(self, key):
        if not self.wraparound:
            if key == KEY_RIGHT:
                if len(self.choices) == self.choices.index(str(self.value)) + 1:
                    return
            if key == KEY_LEFT:
                if self.choices.index(str(self.value)) == 0:
                    return
        nchoices = len(self.choices)
        if nchoices > 1:
            i = self.choices.index(str(self.value))
            if key == KEY_LEFT:
                self.value = self.choices[(i + nchoices - 1) % nchoices]
            elif key == KEY_RIGHT:
                self.value = self.choices[(i + 1) % nchoices]
            elif key == KEY_HOME:
                self.value = self.choices[0]
            elif key == KEY_END:
                self.value = self.choices[nchoices - 1]


class ConfigNumber(ConfigText):

    def __init__(self, default = 0):
        ConfigText.__init__(self, str(default), fixed_size=False)

    def getValue(self):
        return int(self.text)

    def setValue(self, val):
        self.text = str(val)

    value = property(getValue, setValue)
    _value = property(getValue, setValue)

    def isChanged(self):
        sv = self.saved_value
        strv = self.tostring(self.value)
        if sv is None and strv == self.default:
            return False
        else:
            return strv != sv

    def conform(self):
        pos = len(self.text) - self.marked_pos
        self.text = self.text.lstrip('0')
        if self.text == '':
            self.text = '0'
        if pos > len(self.text):
            self.marked_pos = 0
        else:
            self.marked_pos = len(self.text) - pos

    def handleKey(self, key):
        if key in KEY_NUMBERS or key == KEY_ASCII:
            if key == KEY_ASCII:
                ascii = getPrevAsciiCode()
                if not 48 <= ascii <= 57:
                    return
            else:
                ascii = getKeyNumber(key) + 48
            newChar = unichr(ascii)
            if self.allmarked:
                self.deleteAllChars()
                self.allmarked = False
            self.insertChar(newChar, self.marked_pos, False)
            self.marked_pos += 1
        else:
            ConfigText.handleKey(self, key)
        self.conform()

    def onSelect(self, session):
        self.allmarked = self.value != ''

    def onDeselect(self, session):
        self.marked_pos = 0
        self.offset = 0
        if not self.last_value == self.value:
            self.changedFinal()
            self.last_value = self.value


class ConfigSearchText(ConfigText):

    def __init__(self, default = '', fixed_size = False, visible_width = False):
        ConfigText.__init__(self, default=default, fixed_size=fixed_size, visible_width=visible_width)
        NumericalTextInput.__init__(self, nextFunc=self.nextFunc, handleTimeout=False, search=True)


class ConfigDirectory(ConfigText):

    def __init__(self, default = '', visible_width = 60):
        ConfigText.__init__(self, default, fixed_size=True, visible_width=visible_width)

    def handleKey(self, key):
        pass

    def getValue(self):
        if self.text == '':
            return None
        else:
            return ConfigText.getValue(self)
            return None

    def setValue(self, val):
        if val is None:
            val = ''
        ConfigText.setValue(self, val)
        return

    def getMulti(self, selected):
        if self.text == '':
            return ('mtext'[1 - selected:], _('List of storage devices'), range(0))
        else:
            return ConfigText.getMulti(self, selected)

    def onSelect(self, session):
        self.allmarked = self.value != ''


class ConfigSlider(ConfigElement):

    def __init__(self, default = 0, increment = 1, limits = (0, 100)):
        ConfigElement.__init__(self)
        self.value = self.last_value = self.default = default
        self.min = limits[0]
        self.max = limits[1]
        self.increment = increment

    def checkValues(self):
        if self.value < self.min:
            self.value = self.min
        if self.value > self.max:
            self.value = self.max

    def handleKey(self, key):
        if key == KEY_LEFT:
            self.value -= self.increment
        elif key == KEY_RIGHT:
            self.value += self.increment
        elif key == KEY_HOME:
            self.value = self.min
        elif key == KEY_END:
            self.value = self.max
        else:
            return
        self.checkValues()

    def getText(self):
        return '%d / %d' % (self.value, self.max)

    def getMulti(self, selected):
        self.checkValues()
        return ('slider', self.value, self.max)

    def fromstring(self, value):
        return int(value)


class ConfigSatlist(ConfigSelection):

    def __init__(self, list, default = None):
        if default is not None:
            default = str(default)
        ConfigSelection.__init__(self, choices=[ (str(orbpos), desc) for orbpos, desc, flags in list ], default=default)
        return

    def getOrbitalPosition(self):
        if self.value == '':
            return None
        else:
            return int(self.value)

    orbital_position = property(getOrbitalPosition)


class ConfigSet(ConfigElement):

    def __init__(self, choices, default = None):
        if not default:
            default = []
        ConfigElement.__init__(self)
        if isinstance(choices, list):
            choices.sort()
            self.choices = choicesList(choices, choicesList.LIST_TYPE_LIST)
        if default is None:
            default = []
        self.pos = -1
        default.sort()
        self.last_value = self.default = default
        self.value = default[:]
        return

    def toggleChoice(self, choice):
        value = self.value
        if choice in value:
            value.remove(choice)
        else:
            value.append(choice)
            value.sort()
        self.changed()

    def handleKey(self, key):
        if key in KEY_NUMBERS + [KEY_DELETE, KEY_BACKSPACE]:
            if self.pos != -1:
                self.toggleChoice(self.choices[self.pos])
        elif key == KEY_LEFT:
            if self.pos < 0:
                self.pos = len(self.choices) - 1
            else:
                self.pos -= 1
        elif key == KEY_RIGHT:
            if self.pos >= len(self.choices) - 1:
                self.pos = -1
            else:
                self.pos += 1
        elif key in (KEY_HOME, KEY_END):
            self.pos = -1

    def genString(self, lst):
        res = ''
        for x in lst:
            res += self.description[x] + ' '

        return res

    def getText(self):
        return self.genString(self.value)

    def getMulti(self, selected):
        if not selected or self.pos == -1:
            return ('text', self.genString(self.value))
        else:
            tmp = self.value[:]
            ch = self.choices[self.pos]
            mem = ch in self.value
            if not mem:
                tmp.append(ch)
                tmp.sort()
            ind = tmp.index(ch)
            val1 = self.genString(tmp[:ind])
            val2 = ' ' + self.genString(tmp[ind + 1:])
            if mem:
                chstr = ' ' + self.description[ch] + ' '
            else:
                chstr = '(' + self.description[ch] + ')'
            len_val1 = len(val1)
            return ('mtext', val1 + chstr + val2, range(len_val1, len_val1 + len(chstr)))

    def onDeselect(self, session):
        self.pos = -1
        if not self.last_value == self.value:
            self.changedFinal()
            self.last_value = self.value[:]

    def tostring(self, value):
        return str(value)

    def fromstring(self, val):
        return eval(val)

    description = property(lambda self: descriptionList(self.choices.choices, choicesList.LIST_TYPE_LIST))


class ConfigLocations(ConfigElement):

    def __init__(self, default = None, visible_width = False):
        if not default:
            default = []
        ConfigElement.__init__(self)
        self.visible_width = visible_width
        self.pos = -1
        self.default = default
        self.locations = []
        self.mountpoints = []
        self.value = default[:]

    def setValue(self, value):
        locations = self.locations
        loc = [ x[0] for x in locations if x[3] ]
        add = [ x for x in value if x not in loc ]
        diff = add + [ x for x in loc if x not in value ]
        locations = [ x for x in locations if x[0] not in diff ] + [ [x,
         self.getMountpoint(x),
         True,
         True] for x in add ]
        self.locations = locations
        self.changed()

    def getValue(self):
        self.checkChangedMountpoints()
        locations = self.locations
        for x in locations:
            x[3] = x[2]

        return [ x[0] for x in locations if x[3] ]

    value = property(getValue, setValue)

    def tostring(self, value):
        return str(value)

    def fromstring(self, val):
        return eval(val)

    def load(self):
        sv = self.saved_value
        if sv is None:
            tmp = self.default
        else:
            tmp = self.fromstring(sv)
        locations = [ [x,
         None,
         False,
         False] for x in tmp ]
        self.refreshMountpoints()
        for x in locations:
            if fileExists(x[0]):
                x[1] = self.getMountpoint(x[0])
                x[2] = True

        self.locations = locations
        return

    def save(self):
        locations = self.locations
        if self.save_disabled or not locations:
            self.saved_value = None
        else:
            self.saved_value = self.tostring([ x[0] for x in locations ])
        return

    def isChanged(self):
        sv = self.saved_value
        locations = self.locations
        if val is None and not locations:
            return False
        else:
            return self.tostring([ x[0] for x in locations ]) != sv

    def addedMount(self, mp):
        for x in self.locations:
            if x[1] == mp:
                x[2] = True
            elif x[1] is None and fileExists(x[0]):
                x[1] = self.getMountpoint(x[0])
                x[2] = True

        return

    def removedMount(self, mp):
        for x in self.locations:
            if x[1] == mp:
                x[2] = False

    def refreshMountpoints(self):
        self.mountpoints = [ p.mountpoint for p in harddiskmanager.getMountedPartitions() if p.mountpoint != '/' ]
        self.mountpoints.sort(key=lambda x: -len(x))

    def checkChangedMountpoints(self):
        oldmounts = self.mountpoints
        self.refreshMountpoints()
        newmounts = self.mountpoints
        if oldmounts == newmounts:
            return
        for x in oldmounts:
            if x not in newmounts:
                self.removedMount(x)

        for x in newmounts:
            if x not in oldmounts:
                self.addedMount(x)

    def getMountpoint(self, file):
        file = os.path.realpath(file) + '/'
        for m in self.mountpoints:
            if file.startswith(m):
                return m

        return None

    def handleKey(self, key):
        if key == KEY_LEFT:
            self.pos -= 1
            if self.pos < -1:
                self.pos = len(self.value) - 1
        elif key == KEY_RIGHT:
            self.pos += 1
            if self.pos >= len(self.value):
                self.pos = -1
        elif key in (KEY_HOME, KEY_END):
            self.pos = -1

    def getText(self):
        return ' '.join(self.value)

    def getMulti(self, selected):
        if not selected:
            valstr = ' '.join(self.value)
            if self.visible_width and len(valstr) > self.visible_width:
                return ('text', valstr[0:self.visible_width])
            else:
                return ('text', valstr)
        else:
            i = 0
            valstr = ''
            ind1 = 0
            ind2 = 0
            for val in self.value:
                if i == self.pos:
                    ind1 = len(valstr)
                valstr += str(val) + ' '
                if i == self.pos:
                    ind2 = len(valstr)
                i += 1

            if self.visible_width and len(valstr) > self.visible_width:
                if ind1 + 1 < self.visible_width / 2:
                    off = 0
                else:
                    off = min(ind1 + 1 - self.visible_width / 2, len(valstr) - self.visible_width)
                return ('mtext', valstr[off:off + self.visible_width], range(ind1 - off, ind2 - off))
            return ('mtext', valstr, range(ind1, ind2))

    def onDeselect(self, session):
        self.pos = -1


class ConfigNothing(ConfigSelection):

    def __init__(self):
        ConfigSelection.__init__(self, choices=[('', '')])


class ConfigSubsectionContent(object):
    pass


class ConfigSubList(list, object):

    def __init__(self):
        list.__init__(self)
        self.stored_values = {}

    def save(self):
        for x in self:
            x.save()

    def load(self):
        for x in self:
            x.load()

    def getSavedValue(self):
        res = {}
        for i, val in enumerate(self):
            sv = val.saved_value
            if sv is not None:
                res[str(i)] = sv

        return res

    def setSavedValue(self, values):
        self.stored_values = dict(values)
        for key, val in self.stored_values.items():
            if int(key) < len(self):
                self[int(key)].saved_value = val

    saved_value = property(getSavedValue, setSavedValue)

    def append(self, item):
        i = str(len(self))
        list.append(self, item)
        if i in self.stored_values:
            item.saved_value = self.stored_values[i]
            item.load()

    def dict(self):
        return dict([ (str(index), value) for index, value in enumerate(self) ])


class ConfigSubDict(dict, object):

    def __init__(self):
        dict.__init__(self)
        self.stored_values = {}

    def save(self):
        for x in self.values():
            x.save()

    def load(self):
        for x in self.values():
            x.load()

    def getSavedValue(self):
        res = {}
        for key, val in self.items():
            sv = val.saved_value
            if sv is not None:
                res[str(key)] = sv

        return res

    def setSavedValue(self, values):
        self.stored_values = dict(values)
        for key, val in self.items():
            if str(key) in self.stored_values:
                val.saved_value = self.stored_values[str(key)]

    saved_value = property(getSavedValue, setSavedValue)

    def __setitem__(self, key, item):
        dict.__setitem__(self, key, item)
        if str(key) in self.stored_values:
            item.saved_value = self.stored_values[str(key)]
            item.load()

    def dict(self):
        return self


class ConfigSubsection(object):

    def __init__(self):
        self.__dict__['content'] = ConfigSubsectionContent()
        self.content.items = {}
        self.content.stored_values = {}

    def __setattr__(self, name, value):
        if name == 'saved_value':
            return self.setSavedValue(value)
        else:
            content = self.content
            content.items[name] = value
            x = content.stored_values.get(name, None)
            if x is not None:
                value.saved_value = x
                value.load()
            return

    def __getattr__(self, name):
        return self.content.items[name]

    def getSavedValue(self):
        res = self.content.stored_values
        for key, val in self.content.items.items():
            sv = val.saved_value
            if sv is not None:
                res[key] = sv
            elif key in res:
                del res[key]

        return res

    def setSavedValue(self, values):
        values = dict(values)
        self.content.stored_values = values
        for key, val in self.content.items.items():
            value = values.get(key, None)
            if value is not None:
                val.saved_value = value

        return

    saved_value = property(getSavedValue, setSavedValue)

    def save(self):
        for x in self.content.items.values():
            x.save()

    def load(self):
        for x in self.content.items.values():
            x.load()

    def dict(self):
        return self.content.items


class Config(ConfigSubsection):

    def __init__(self):
        ConfigSubsection.__init__(self)

    def pickle_this(self, prefix, topickle, result):
        for key, val in topickle.items():
            name = '.'.join((prefix, key))
            if isinstance(val, dict):
                self.pickle_this(name, val, result)
            elif isinstance(val, tuple):
                result += [name,
                 '=',
                 str(val[0]),
                 '\n']
            else:
                result += [name,
                 '=',
                 str(val),
                 '\n']

    def pickle(self):
        result = []
        self.pickle_this('config', self.saved_value, result)
        return ''.join(result)

    def unpickle(self, lines, base_file = True):
        tree = {}
        configbase = tree.setdefault('config', {})
        for l in lines:
            if not l or l[0] == '#':
                continue
            result = l.split('=', 1)
            if len(result) != 2:
                continue
            name, val = result
            val = val.strip()
            names = name.split('.')
            base = configbase
            for n in names[1:-1]:
                base = base.setdefault(n, {})

            base[names[-1]] = val
            if not base_file:
                try:
                    configEntry = eval(name)
                    if configEntry is not None:
                        configEntry.value = val
                except (SyntaxError, KeyError):
                    pass

        if 'config' in tree:
            self.setSavedValue(tree['config'])
        return

    def saveToFile(self, filename):
        text = self.pickle()
        try:
            import os
            f = open(filename + '.writing', 'w')
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
            f.close()
            os.rename(filename + '.writing', filename)
        except IOError:
            print "[Config] Couldn't write %s" % filename

    def loadFromFile(self, filename, base_file = True):
        self.unpickle(open(filename, 'r'), base_file)


config = Config()
config.misc = ConfigSubsection()

class ConfigFile:

    def __init__(self):
        pass

    CONFIG_FILE = resolveFilename(SCOPE_CONFIG, 'settings')

    def load(self):
        try:
            config.loadFromFile(self.CONFIG_FILE, True)
            print '[Config] Config file loaded ok...'
        except IOError as e:
            print '[Config] unable to load config (%s), assuming defaults...' % str(e)

    def save(self):
        config.saveToFile(self.CONFIG_FILE)

    def __resolveValue(self, pickles, cmap):
        key = pickles[0]
        if cmap.has_key(key):
            if len(pickles) > 1:
                return self.__resolveValue(pickles[1:], cmap[key].dict())
            else:
                return str(cmap[key].value)
        return None

    def getResolvedKey(self, key):
        names = key.split('.')
        if len(names) > 1:
            if names[0] == 'config':
                ret = self.__resolveValue(names[1:], config.content.items)
                if ret and len(ret):
                    return ret
        print '[Config] getResolvedKey', key, 'empty variable.'
        return ''


def NoSave(element):
    element.disableSave()
    return element


configfile = ConfigFile()
configfile.load()

def getConfigListEntry(*args):
    return args


def updateConfigElement(element, newelement):
    newelement.value = element.value
    return newelement


cec_limits = [(0, 15),
 (0, 15),
 (0, 15),
 (0, 15)]

class ConfigCECAddress(ConfigSequence):

    def __init__(self, default, auto_jump = False):
        ConfigSequence.__init__(self, seperator='.', limits=cec_limits, default=default)
        self.block_len = [ len(str(x[1])) for x in self.limits ]
        self.marked_block = 0
        self.overwrite = True
        self.auto_jump = auto_jump

    def handleKey(self, key):
        if key == KEY_LEFT:
            if self.marked_block > 0:
                self.marked_block -= 1
            self.overwrite = True
        elif key == KEY_RIGHT:
            if self.marked_block < len(self.limits) - 1:
                self.marked_block += 1
            self.overwrite = True
        elif key == KEY_HOME:
            self.marked_block = 0
            self.overwrite = True
        elif key == KEY_END:
            self.marked_block = len(self.limits) - 1
            self.overwrite = True
        elif key in KEY_NUMBERS or key == KEY_ASCII:
            if key == KEY_ASCII:
                code = getPrevAsciiCode()
                if code < 48 or code > 57:
                    return
                number = code - 48
            else:
                number = getKeyNumber(key)
            oldvalue = self._value[self.marked_block]
            if self.overwrite:
                self._value[self.marked_block] = number
                self.overwrite = False
            else:
                oldvalue *= 10
                newvalue = oldvalue + number
                if self.auto_jump and newvalue > self.limits[self.marked_block][1] and self.marked_block < len(self.limits) - 1:
                    self.handleKey(KEY_RIGHT)
                    self.handleKey(key)
                    return
                self._value[self.marked_block] = newvalue
            if len(str(self._value[self.marked_block])) >= self.block_len[self.marked_block]:
                self.handleKey(KEY_RIGHT)
            self.validate()
            self.changed()

    def genText(self):
        value = ''
        block_strlen = []
        for i in self._value:
            block_strlen.append(len(str(i)))
            if value:
                value += self.seperator
            value += str(i)

        leftPos = sum(block_strlen[:self.marked_block]) + self.marked_block
        rightPos = sum(block_strlen[:self.marked_block + 1]) + self.marked_block
        mBlock = range(leftPos, rightPos)
        return (value, mBlock)

    def getMulti(self, selected):
        value, mBlock = self.genText()
        if self.enabled:
            return ('mtext'[1 - selected:], value, mBlock)
        else:
            return ('text', value)

    def getHTML(self, id):
        return '.'.join([ '%d' % d for d in self.value ])