# Embedded file name: /usr/lib/enigma2/python/keymapparser.py
import enigma
import xml.etree.cElementTree
from keyids import KEYIDS
from Tools.KeyBindings import addKeyBinding

class KeymapError(Exception):

    def __init__(self, message):
        self.msg = message

    def __str__(self):
        return self.msg


def parseKeys(context, filename, actionmap, device, keys):
    for x in keys.findall('key'):
        get_attr = x.attrib.get
        mapto = get_attr('mapto')
        id = get_attr('id')
        flags = get_attr('flags')
        flag_ascii_to_id = lambda x: {'m': 1,
         'b': 2,
         'r': 4,
         'l': 8}[x]
        flags = sum(map(flag_ascii_to_id, flags))
        if len(id) == 1:
            keyid = ord(id) | 32768
        elif id[0] == '\\':
            if id[1] == 'x':
                keyid = int(id[2:], 16) | 32768
            elif id[1] == 'd':
                keyid = int(id[2:]) | 32768
            else:
                raise KeymapError("[Keymapparser] key id '" + str(id) + "' is neither hex nor dec")
        else:
            try:
                keyid = KEYIDS[id]
            except:
                raise KeymapError("[Keymapparser] key id '" + str(id) + "' is illegal")

        actionmap.bindKey(filename, device, keyid, flags, context, mapto)
        addKeyBinding(filename, keyid, context, mapto, flags)


def readKeymap(filename):
    p = enigma.eActionMap.getInstance()
    source = open(filename)
    try:
        dom = xml.etree.cElementTree.parse(source)
    except:
        raise KeymapError('[Keymapparser] keymap %s not well-formed.' % filename)

    source.close()
    keymap = dom.getroot()
    for cmap in keymap.findall('map'):
        context = cmap.attrib.get('context')
        parseKeys(context, filename, p, 'generic', cmap)
        for device in cmap.findall('device'):
            parseKeys(context, filename, p, device.attrib.get('name'), device)


def removeKeymap(filename):
    p = enigma.eActionMap.getInstance()
    p.unbindKeyDomain(filename)