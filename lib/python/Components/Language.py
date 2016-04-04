# Embedded file name: /usr/lib/enigma2/python/Components/Language.py
import gettext
import locale
import os
from Tools.Directories import SCOPE_LANGUAGE, resolveFilename
from time import time, localtime, strftime
LPATH = resolveFilename(SCOPE_LANGUAGE, '')
Lpackagename = 'enigma2-locale-'

class Language:

    def __init__(self):
        gettext.install('enigma2', resolveFilename(SCOPE_LANGUAGE, ''), unicode=0, codeset='utf-8')
        self.activeLanguage = 0
        self.catalog = None
        self.lang = {}
        self.InitLang()
        self.callbacks = []
        return

    def InitLang(self):
        self.langlist = []
        self.langlistselection = []
        self.ll = os.listdir(LPATH)
        self.addLanguage('Polski', 'pl', 'PL', 'ISO-8859-15')
        self.addLanguage('Svenska', 'sv', 'SE', 'ISO-8859-15')
        self.addLanguage('\xd0\xa0\xd1\x83\xd1\x81\xd1\x81\xd0\xba\xd0\xb8\xd0\xb9', 'ru', 'RU', 'ISO-8859-15')
        self.addLanguage('English (US)', 'en', 'US', 'ISO-8859-15')
        self.addLanguage('English (UK)', 'en', 'GB', 'ISO-8859-15')
        self.addLanguage('Deutsch', 'de', 'DE', 'ISO-8859-15')
        self.addLanguage('Arabic', 'ar', 'AE', 'ISO-8859-15')
        self.addLanguage('\xd0\x91\xd1\x8a\xd0\xbb\xd0\xb3\xd0\xb0\xd1\x80\xd1\x81\xd0\xba\xd0\xb8', 'bg', 'BG', 'ISO-8859-15')
        self.addLanguage('Bokm\xc3\xa5l', 'nb', 'NO', 'ISO-8859-15')
        self.addLanguage('Catal\xc3\xa0', 'ca', 'AD', 'ISO-8859-15')
        self.addLanguage('\xc4\x8cesky', 'cs', 'CZ', 'ISO-8859-15')
        self.addLanguage('Dansk', 'da', 'DK', 'ISO-8859-15')
        self.addLanguage('\xce\x95\xce\xbb\xce\xbb\xce\xb7\xce\xbd\xce\xb9\xce\xba\xce\xac', 'el', 'GR', 'ISO-8859-7')
        self.addLanguage('Espa\xc3\xb1ol', 'es', 'ES', 'ISO-8859-15')
        self.addLanguage('Eesti', 'et', 'EE', 'ISO-8859-15')
        self.addLanguage('Persian', 'fa', 'IR', 'ISO-8859-15')
        self.addLanguage('Suomi', 'fi', 'FI', 'ISO-8859-15')
        self.addLanguage('Fran\xc3\xa7ais', 'fr', 'FR', 'ISO-8859-15')
        self.addLanguage('Frysk', 'fy', 'NL', 'ISO-8859-15')
        self.addLanguage('Hebrew', 'he', 'IL', 'ISO-8859-15')
        self.addLanguage('Hrvatski', 'hr', 'HR', 'ISO-8859-15')
        self.addLanguage('Magyar', 'hu', 'HU', 'ISO-8859-15')
        self.addLanguage('\xc3\x8dslenska', 'is', 'IS', 'ISO-8859-15')
        self.addLanguage('Italiano', 'it', 'IT', 'ISO-8859-15')
        self.addLanguage('Kurdish', 'ku', 'KU', 'ISO-8859-15')
        self.addLanguage('Lietuvi\xc5\xb3', 'lt', 'LT', 'ISO-8859-15')
        self.addLanguage('Latvie\xc5\xa1u', 'lv', 'LV', 'ISO-8859-15')
        self.addLanguage('Nederlands', 'nl', 'NL', 'ISO-8859-15')
        self.addLanguage('Norsk Bokm\xc3\xa5l', 'nb', 'NO', 'ISO-8859-15')
        self.addLanguage('Norsk', 'no', 'NO', 'ISO-8859-15')
        self.addLanguage('Portugu\xc3\xaas', 'pt', 'PT', 'ISO-8859-15')
        self.addLanguage('Portugu\xc3\xaas do Brasil', 'pt', 'BR', 'ISO-8859-15')
        self.addLanguage('Romanian', 'ro', 'RO', 'ISO-8859-15')
        self.addLanguage('Slovensky', 'sk', 'SK', 'ISO-8859-15')
        self.addLanguage('Sloven\xc5\xa1\xc4\x8dina', 'sl', 'SI', 'ISO-8859-15')
        self.addLanguage('Srpski', 'sr', 'YU', 'ISO-8859-15')
        self.addLanguage('\xe0\xb8\xa0\xe0\xb8\xb2\xe0\xb8\xa9\xe0\xb8\xb2\xe0\xb9\x84\xe0\xb8\x97\xe0\xb8\xa2', 'th', 'TH', 'ISO-8859-15')
        self.addLanguage('T\xc3\xbcrk\xc3\xa7e', 'tr', 'TR', 'ISO-8859-15')
        self.addLanguage('Ukrainian', 'uk', 'UA', 'ISO-8859-15')

    def addLanguage(self, name, lang, country, encoding):
        try:
            if lang in self.ll:
                if country == 'GB' or country == 'BR':
                    if lang + '_' + country in self.ll:
                        self.lang[str(lang + '_' + country)] = (name,
                         lang,
                         country,
                         encoding)
                        self.langlist.append(str(lang + '_' + country))
                else:
                    self.lang[str(lang + '_' + country)] = (name,
                     lang,
                     country,
                     encoding)
                    self.langlist.append(str(lang + '_' + country))
        except:
            print '[Language] Language ' + str(name) + ' not found'

        self.langlistselection.append((str(lang + '_' + country), name))

    def activateLanguage(self, index):
        try:
            lang = self.lang[index]
            print '[Language] Activating language ' + lang[0]
            self.catalog = gettext.translation('enigma2', resolveFilename(SCOPE_LANGUAGE, ''), languages=[index], fallback=True)
            self.catalog.install(names=('ngettext', 'pgettext'))
            self.activeLanguage = index
            for x in self.callbacks:
                if x:
                    x()

        except:
            print '[Language] Selected language does not exist!'

        for category in [locale.LC_CTYPE,
         locale.LC_COLLATE,
         locale.LC_TIME,
         locale.LC_MONETARY,
         locale.LC_MESSAGES,
         locale.LC_NUMERIC]:
            try:
                locale.setlocale(category, (self.getLanguage(), 'UTF-8'))
            except:
                pass

        os.environ['LC_TIME'] = self.getLanguage() + '.UTF-8'
        os.environ['LANGUAGE'] = self.getLanguage() + '.UTF-8'
        os.environ['GST_SUBTITLE_ENCODING'] = self.getGStreamerSubtitleEncoding()

    def activateLanguageIndex(self, index):
        if index < len(self.langlist):
            self.activateLanguage(self.langlist[index])

    def getLanguageList(self):
        return [ (x, self.lang[x]) for x in self.langlist ]

    def getLanguageListSelection(self):
        return self.langlistselection

    def getActiveLanguage(self):
        return self.activeLanguage

    def getActiveCatalog(self):
        return self.catalog

    def getActiveLanguageIndex(self):
        idx = 0
        for x in self.langlist:
            if x == self.activeLanguage:
                return idx
            idx += 1

        return None

    def getLanguage(self):
        try:
            return str(self.lang[self.activeLanguage][1]) + '_' + str(self.lang[self.activeLanguage][2])
        except:
            return ''

    def getGStreamerSubtitleEncoding(self):
        try:
            return str(self.lang[self.activeLanguage][3])
        except:
            return 'ISO-8859-15'

    def addCallback(self, callback):
        self.callbacks.append(callback)

    def delLanguage(self, delLang = None):
        from Components.config import config, configfile
        from shutil import rmtree
        lang = config.osd.language.value
        if delLang:
            print 'DELETE LANG', delLang
            if delLang == 'en_US' or delLang == 'en_GB':
                print 'Default Language can not be deleted !!'
                return
            if delLang == 'pt_BR':
                delLang = delLang.lower()
                delLang = delLang.replace('_', '-')
                os.system('opkg remove --autoremove --force-depends ' + Lpackagename + delLang)
            else:
                os.system('opkg remove --autoremove --force-depends ' + Lpackagename + delLang[:2])
        else:
            print 'Delete all lang except ', lang
            ll = os.listdir(LPATH)
            for x in ll:
                if len(x) > 2:
                    if x != lang:
                        x = x.lower()
                        x = x.replace('_', '-')
                        os.system('opkg remove --autoremove --force-depends ' + Lpackagename + x)
                elif x != lang[:2] and x != 'en':
                    os.system('opkg remove --autoremove --force-depends ' + Lpackagename + x)
                elif x == 'pt':
                    if x != lang:
                        os.system('opkg remove --autoremove --force-depends ' + Lpackagename + x)

            os.system('touch /etc/enigma2/.removelang')
        self.InitLang()

    def updateLanguageCache(self):
        t = localtime(time())
        createdate = strftime('%d.%m.%Y  %H:%M:%S', t)
        f = open('/usr/lib/enigma2/python/Components/Language_cache.py', 'w')
        f.write('# -*- coding: UTF-8 -*-\n')
        f.write('# date: ' + createdate + '\n#\n\n')
        f.write('LANG_TEXT = {\n')
        for lang in self.langlist:
            catalog = gettext.translation('enigma2', resolveFilename(SCOPE_LANGUAGE, ''), languages=[str(lang)], fallback=True)
            T1 = catalog.gettext('Please use the UP and DOWN keys to select your language. Afterwards press the OK button.')
            T2 = catalog.gettext('Language selection')
            T3 = catalog.gettext('Cancel')
            T4 = catalog.gettext('Save')
            f.write('"' + lang + '"' + ': {\n')
            f.write('\t "T1": "' + T1 + '",\n')
            f.write('\t "T2": "' + T2 + '",\n')
            f.write('\t "T3": "' + T3 + '",\n')
            f.write('\t "T4": "' + T4 + '",\n')
            f.write('},\n')

        f.write('}\n')
        f.close
        catalog = None
        lang = None
        return


language = Language()