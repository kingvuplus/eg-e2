# Embedded file name: /usr/lib/enigma2/python/Tools/LXMLTools.py


def elementsWithTag(el, tag):
    if isinstance(tag, str):
        s = tag
        tag = lambda x: x == s
    for x in el:
        if not x.tag:
            continue
        if tag(x.tag):
            yield x


def mergeText(nodelist):
    rc = ''
    for node in nodelist:
        if node.text:
            rc = rc + node.text

    return rc


def stringToXML(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace("'", '&apos;').replace('"', '&quot;')