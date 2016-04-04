# Embedded file name: /usr/lib/enigma2/python/Tools/NumericalTextInput.py
from enigma import eTimer
from Components.Language import language
MAP_SEARCH = (u'%_0', u' 1', u'abc2', u'def3', u'ghi4', u'jkl5', u'mno6', u'pqrs7', u'tuv8', u'wxyz9')
MAP_SEARCH_UPCASE = (u'0%_', u'1 ', u'ABC2', u'DEF3', u'GHI4', u'JKL5', u'MNO6', u'PQRS7', u'TUV8', u'WXYZ9')
MAP_DEFAULT = (u'0,?!&@=*\'+"()$~%#', u' 1.:;/-_', u'abc2ABC', u'def3DEF', u'ghi4GHI', u'jkl5JKL', u'mno6MNO', u'pqrs7PQRS', u'tuv8TUV', u'wxyz9WXYZ')
MAP_DE = (u'0,?!&@=*\'+"()$~%#', u' 1.:;/-_', u'abc\xe42ABC\xc4', u'def3DEF', u'ghi4GHI', u'jkl5JKL', u'mno\xf66MNO\xd6', u'pqrs\xdf7PQRS\xdf', u'tuv\xfc8TUV\xdc', u'wxyz9WXYZ')
MAP_ES = (u'0,?!&@=*\'+"()$~%#', u' 1.:;/-_', u'abc\xe1\xe02ABC\xc1\xc0', u'de\xe9\xe8f3DEF\xc9\xc8', u'ghi\xed\xec4GHI\xcd\xcc', u'jkl5JKL', u'mn\xf1o\xf3\xf26MN\xd1O\xd3\xd2', u'pqrs7PQRS', u'tuv\xfa\xf98TUV\xda\xd9', u'wxyz9WXYZ')
MAP_SE = (u'0,?!&@=*\'+"()$~%#', u' 1.:;/-_', u'abc\xe5\xe42ABC\xc5\xc4', u'def\xe93DEF\xc9', u'ghi4GHI', u'jkl5JKL', u'mno\xf66MNO\xd6', u'pqrs7PQRS', u'tuv8TUV', u'wxyz9WXYZ')
MAP_CZ = (u'0,?\'+"()@$!=&*%#', u' 1.:;/-_', u'abc2\xe1\u010dABC\xc1\u010c', u'def3\u010f\xe9\u011bDEF\u010e\xc9\u011a', u'ghi4\xedGHI\xcd', u'jkl5JKL', u'mno6\u0148\xf3MNO\u0147\xd3', u'pqrs7\u0159\u0161PQRS\u0158\u0160', u'tuv8\u0165\xfa\u016fTUV\u0164\xda\u016e', u'wxyz9\xfd\u017eWXYZ\xdd\u017d')
MAP_SK = (u'0,?\'+"()@$!=&*%', u' 1.:;/-_', u'abc2\xe1\xe4\u010dABC\xc1\xc4\u010c', u'def3\u010f\xe9\u011bDEF\u010e\xc9\u011a', u'ghi4\xedGHI\xcd', u'jkl5\u013e\u013aJKL\u013d\u0139', u'mno6\u0148\xf3\xf6\xf4MNO\u0147\xd3\xd6\xd4', u'pqrs7\u0159\u0155\u0161PQRS\u0158\u0154\u0160', u'tuv8\u0165\xfa\u016f\xfcTUV\u0164\xda\u016e\xdc', u'wxyz9\xfd\u017eWXYZ\xdd\u017d')
MAP_PL = (u'0,?\'+"()@$!=&*%#', u' 1.:;/-_', u'abc\u0105\u01072ABC\u0104\u0106', u'def\u01193DEF\u0118', u'ghi4GHI', u'jkl\u01425JKL\u0141', u'mno\u0144\xf36MNO\u0143\xd3', u'pqrs\u015b7PQRS\u015a', u'tuv8TUV', u'wxyz\u017a\u017c9WXYZ\u0179\u017b')
MAP_RU = (u'0,?\'+"()@$!=&*%#', u' 1.:;/-_', u'abc\u0430\u0431\u0432\u04332ABC\u0410\u0411\u0412\u0413', u'def\u0434\u0435\u0436\u04373DEF\u0414\u0415\u0416\u0417', u'ghi\u0438\u0439\u043a\u043b4GHI\u0418\u0419\u041a\u041b', u'jkl\u043c\u043d\u043e\u043f5JKL\u041c\u041d\u041e\u041f', u'mno\u0440\u0441\u0442\u04436MNO\u0420\u0421\u0422\u0423', u'pqrs\u0444\u0445\u0446\u04477PQRS\u0424\u0425\u0426\u0427', u'tuv\u0448\u0449\u044c\u044b8TUV\u0428\u0429\u042c\u042b', u'wxyz\u044a\u044d\u044e\u044f9WXYZ\u042a\u042d\u042e\u042f')
MAP_LV = (u'0,?!&@=*\'+"()$~%', u' 1.:;/-_', u'a\u0101bc\u010d2A\u0100BC\u010c', u'de\u0113f3DE\u0112F', u'g\u0123hi\u012b4G\u0122HI\u012a', u'jk\u0137l\u013c5JK\u0136L\u013b', u'mn\u0146o6MN\u0145O', u'pqrs\u01617PQRS\u0160', u'tu\u016bv8TU\u016aV', u'wxyz\u017e9WXYZ\u017d')
MAP_NL = (u'0,?!&@=*\'+"()$~%#', u' 1.:;/-_', u'abc2ABC', u'de\xebf3DE\xcbF', u'ghi\xef4GHI\xcf', u'jkl5JKL', u'mno6MNO', u'pqrs7PQRS', u'tuv8TUV', u'wxyz9WXYZ')
MAPPINGS = {'de_DE': MAP_DE,
 'es_ES': MAP_ES,
 'sv_SE': MAP_SE,
 'fi_FI': MAP_SE,
 'cs_CZ': MAP_CZ,
 'sk_SK': MAP_SK,
 'pl_PL': MAP_PL,
 'ru_RU': MAP_RU,
 'lv_LV': MAP_LV,
 'nl_NL': MAP_NL}

class NumericalTextInput:

    def __init__(self, nextFunc = None, handleTimeout = True, search = False, mapping = None):
        self.useableChars = None
        self.nextFunction = nextFunc
        if handleTimeout:
            self.timer = eTimer()
            self.timer.callback.append(self.timeout)
        else:
            self.timer = None
        self.lastKey = -1
        self.pos = -1
        if mapping is not None:
            self.mapping = mapping
        elif search:
            self.mapping = MAP_SEARCH
        else:
            self.mapping = MAPPINGS.get(language.getLanguage(), MAP_DEFAULT)
        return

    def setUseableChars(self, useable):
        self.useableChars = unicode(useable)

    def getKey(self, num):
        cnt = 0
        if self.lastKey != num:
            if self.lastKey != -1:
                self.nextChar()
            self.lastKey = num
            self.pos = -1
        if self.timer is not None:
            self.timer.start(1000, True)
        while True:
            self.pos += 1
            if len(self.mapping[num]) <= self.pos:
                self.pos = 0
            if self.useableChars:
                pos = self.useableChars.find(self.mapping[num][self.pos])
                if pos == -1:
                    cnt += 1
                    if cnt < len(self.mapping[num]):
                        continue
                    else:
                        return
            break

        return self.mapping[num][self.pos]

    def nextKey(self):
        if self.timer is not None:
            self.timer.stop()
        self.lastKey = -1
        return

    def nextChar(self):
        self.nextKey()
        if self.nextFunction:
            self.nextFunction()

    def timeout(self):
        if self.lastKey != -1:
            self.nextChar()