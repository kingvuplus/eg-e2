# Embedded file name: /usr/lib/enigma2/python/Screens/About.py
from Screen import Screen
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Sources.StaticText import StaticText
from Components.Harddisk import Harddisk
from Components.NimManager import nimmanager
from Components.Label import Label
from Components.About import about
from Components.ScrollLabel import ScrollLabel
from Components.Console import Console
from Components.config import config
from enigma import eTimer, getEnigmaVersionString, eLabel, eConsoleAppContainer
from boxbranding import getBoxType, getMachineBrand, getMachineName, getImageVersion, getImageType, getImageBuild, getDriverDate
from Components.Pixmap import MultiPixmap
from Components.Network import iNetwork
from Components.HTMLComponent import HTMLComponent
from Components.GUIComponent import GUIComponent
import skin
from Tools.StbHardware import getFPVersion
from os import path
from re import search

class About(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('Image Information'))
        self.skinName = 'AboutOE'
        self.populate()
        self['key_red'] = Button(_('Close'))
        self['key_green'] = Button(_('Translations'))
        self['actions'] = ActionMap(['SetupActions',
         'ColorActions',
         'TimerEditActions',
         'DirectionActions'], {'cancel': self.close,
         'ok': self.close,
         'log': self.showAboutReleaseNotes,
         'up': self['AboutScrollLabel'].pageUp,
         'down': self['AboutScrollLabel'].pageDown,
         'green': self.showTranslationInfo})

    def populate(self):
        EGAMIVersion = _('EGAMI %s') % about.getImageVersionString()
        self['lab1'] = Label(EGAMIVersion)
        model = None
        AboutText = ''
        AboutText += _('Model:\t%s %s\n') % (getMachineBrand(), getMachineName())
        if path.exists('/proc/stb/info/chipset'):
            AboutText += _('Chipset:\tBCM%s\n') % about.getChipSetString()
        AboutText += _('CPU:\t%s\n') % about.getCPUString()
        AboutText += _('CPU speed:\t%s\n') % about.getCPUSpeedString()
        AboutText += _('Cores:\t%s\n') % about.getCpuCoresString()
        AboutText += _('Version:\t%s') % EGAMIVersion + '\n'
        AboutText += _('Kernel:\t%s') % about.getKernelVersionString() + '\n'
        AboutText += _('Oe-Core:\t%s') % about.getEnigmaVersionString() + '\n'
        AboutText += _('Image Type:\t%s\n') % getImageType().title()
        AboutText += _('Skin name:\t%s\n') % config.skin.primary_skin.value[0:-9]
        string = getDriverDate()
        year = string[0:4]
        month = string[4:6]
        day = string[6:8]
        driversdate = '-'.join((year, month, day))
        AboutText += _('Drivers:\t%s') % driversdate + '\n'
        fp_version = getFPVersion()
        if fp_version is None:
            fp_version = ''
        elif fp_version != 0:
            fp_version = _('Front panel:\t%s') % str(fp_version)
            AboutText += fp_version + '\n'
        AboutText += _('Python:\t%s\n') % about.getPythonVersionString()
        AboutText += _('GStreamer:\t%s') % about.getGStreamerVersionString().replace('GStreamer', '') + '\n\n'
        tempinfo = ''
        if path.exists('/proc/stb/sensors/temp0/value') and getBoxType() not in 'gbquad':
            f = open('/proc/stb/sensors/temp0/value', 'r')
            tempinfo = f.read()
            f.close()
        elif path.exists('/proc/stb/fp/temp_sensor') and getBoxType() not in 'gbquad':
            f = open('/proc/stb/fp/temp_sensor', 'r')
            tempinfo = f.read()
            f.close()
        if tempinfo and int(tempinfo.replace('\n', '')) > 0:
            mark = str('\xc2\xb0')
            AboutText += _('System temperature: %s') % tempinfo.replace('\n', '') + mark + 'C\n\n'
        AboutText += _('Installed:\t%s\n') % about.getFlashDateString()
        AboutText += _('Last update:\t%s') % getEnigmaVersionString() + '\n\n'
        AboutText += _('WWW:\t%s') % about.getImageUrlString()
        self['AboutScrollLabel'] = ScrollLabel(AboutText)
        return

    def showTranslationInfo(self):
        self.session.open(TranslationInfo)

    def showAboutReleaseNotes(self):
        self.session.open(ViewGitLog)

    def createSummary(self):
        return AboutSummary


class Devices(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('Device Information'))
        self.skinName = ['SystemDevicesInfo', 'Devices']
        EGAMIVersion = _('EGAMI %s') % about.getImageVersionString()
        self['lab1'] = Label(EGAMIVersion)
        self['TunerHeader'] = StaticText(_('Detected Tuners:'))
        self['HDDHeader'] = StaticText(_('Detected Devices:'))
        self['MountsHeader'] = StaticText(_('Network Servers:'))
        self['nims'] = StaticText()
        self['hdd'] = StaticText()
        self['mounts'] = StaticText()
        self.list = []
        self.activityTimer = eTimer()
        self.activityTimer.timeout.get().append(self.populate2)
        self['actions'] = ActionMap(['SetupActions', 'ColorActions', 'TimerEditActions'], {'cancel': self.close,
         'ok': self.close})
        self.onLayoutFinish.append(self.populate)

    def populate(self):
        self.mountinfo = ''
        self['actions'].setEnabled(False)
        scanning = _('Please wait while scanning for devices...')
        self['nims'].setText(scanning)
        self['hdd'].setText(scanning)
        self['mounts'].setText(scanning)
        self.activityTimer.start(1)

    def populate2(self):
        self.activityTimer.stop()
        self.Console = Console()
        niminfo = ''
        nims = nimmanager.nimList()
        for count in range(len(nims)):
            if niminfo:
                niminfo += '\n'
            niminfo += nims[count]

        self['nims'].setText(niminfo)
        self.list = []
        list2 = []
        f = open('/proc/partitions', 'r')
        for line in f.readlines():
            parts = line.strip().split()
            if not parts:
                continue
            device = parts[3]
            if not search('sd[a-z][1-9]', device):
                continue
            if device in list2:
                continue
            mount = '/dev/' + device
            f = open('/proc/mounts', 'r')
            for line in f.readlines():
                if device in line:
                    parts = line.strip().split()
                    mount = str(parts[1])
                    break

            f.close()
            if not mount.startswith('/dev/'):
                size = Harddisk(device).diskSize()
                free = Harddisk(device).free()
                if float(size) / 1024 / 1024 >= 1:
                    sizeline = _('Size: ') + str(round(float(size) / 1024 / 1024, 2)) + _('TB')
                elif size / 1024 >= 1:
                    sizeline = _('Size: ') + str(round(float(size) / 1024, 2)) + _('GB')
                elif size >= 1:
                    sizeline = _('Size: ') + str(size) + _('MB')
                else:
                    sizeline = _('Size: ') + _('unavailable')
                if float(free) / 1024 / 1024 >= 1:
                    freeline = _('Free: ') + str(round(float(free) / 1024 / 1024, 2)) + _('TB')
                elif free / 1024 >= 1:
                    freeline = _('Free: ') + str(round(float(free) / 1024, 2)) + _('GB')
                elif free >= 1:
                    freeline = _('Free: ') + str(free) + _('MB')
                else:
                    freeline = _('Free: ') + _('full')
                self.list.append(mount + '\t' + sizeline + ' \t' + freeline)
            else:
                self.list.append(mount + '\t' + _('Not mounted'))
            list2.append(device)

        self.list = '\n'.join(self.list)
        self['hdd'].setText(self.list)
        self.Console.ePopen("df -mh | grep -v '^Filesystem'", self.Stage1Complete)

    def Stage1Complete(self, result, retval, extra_args = None):
        result = result.replace('\n                        ', ' ').split('\n')
        self.mountinfo = ''
        for line in result:
            self.parts = line.split()
            if line and self.parts[0] and (self.parts[0].startswith('192') or self.parts[0].startswith('//192')):
                line = line.split()
                ipaddress = line[0]
                mounttotal = line[1]
                mountfree = line[3]
                if self.mountinfo:
                    self.mountinfo += '\n'
                self.mountinfo += '%s (%sB, %sB %s)' % (ipaddress,
                 mounttotal,
                 mountfree,
                 _('free'))

        if self.mountinfo:
            self['mounts'].setText(self.mountinfo)
        else:
            self['mounts'].setText(_('none'))
        self['actions'].setEnabled(True)

    def createSummary(self):
        return AboutSummary


class SystemMemoryInfo(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('Memory Information'))
        self.skinName = ['SystemMemoryInfo', 'About']
        EGAMIVersion = _('EGAMI %s') % about.getImageVersionString()
        self['lab1'] = Label(EGAMIVersion)
        self['AboutScrollLabel'] = ScrollLabel()
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'cancel': self.close,
         'ok': self.close})
        out_lines = file('/proc/meminfo').readlines()
        self.AboutText = _('RAM') + '\n\n'
        RamTotal = '-'
        RamFree = '-'
        for lidx in range(len(out_lines) - 1):
            tstLine = out_lines[lidx].split()
            if 'MemTotal:' in tstLine:
                MemTotal = out_lines[lidx].split()
                self.AboutText += _('Total memory:') + '\t' + MemTotal[1] + '\n'
            if 'MemFree:' in tstLine:
                MemFree = out_lines[lidx].split()
                self.AboutText += _('Free memory:') + '\t' + MemFree[1] + '\n'
            if 'Buffers:' in tstLine:
                Buffers = out_lines[lidx].split()
                self.AboutText += _('Buffers:') + '\t' + Buffers[1] + '\n'
            if 'Cached:' in tstLine:
                Cached = out_lines[lidx].split()
                self.AboutText += _('Cached:') + '\t' + Cached[1] + '\n'
            if 'SwapTotal:' in tstLine:
                SwapTotal = out_lines[lidx].split()
                self.AboutText += _('Total swap:') + '\t' + SwapTotal[1] + '\n'
            if 'SwapFree:' in tstLine:
                SwapFree = out_lines[lidx].split()
                self.AboutText += _('Free swap:') + '\t' + SwapFree[1] + '\n\n'

        self['actions'].setEnabled(False)
        self.Console = Console()
        self.Console.ePopen("df -mh / | grep -v '^Filesystem'", self.Stage1Complete)

    def Stage1Complete(self, result, retval, extra_args = None):
        flash = str(result).replace('\n', '')
        flash = flash.split()
        RamTotal = flash[1]
        RamFree = flash[3]
        self.AboutText += _('FLASH') + '\n\n'
        self.AboutText += _('Total:') + '\t' + RamTotal + '\n'
        self.AboutText += _('Free:') + '\t' + RamFree + '\n\n'
        self['AboutScrollLabel'].setText(self.AboutText)
        self['actions'].setEnabled(True)

    def createSummary(self):
        return AboutSummary


class SystemNetworkInfo(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('Network Information'))
        self.skinName = ['SystemNetworkInfo', 'WlanStatus']
        EGAMIVersion = _('EGAMI %s') % about.getImageVersionString()
        self['lab1'] = Label(EGAMIVersion)
        self['LabelBSSID'] = StaticText()
        self['LabelESSID'] = StaticText()
        self['LabelQuality'] = StaticText()
        self['LabelSignal'] = StaticText()
        self['LabelBitrate'] = StaticText()
        self['LabelEnc'] = StaticText()
        self['BSSID'] = StaticText()
        self['ESSID'] = StaticText()
        self['quality'] = StaticText()
        self['signal'] = StaticText()
        self['bitrate'] = StaticText()
        self['enc'] = StaticText()
        self['IFtext'] = StaticText()
        self['IF'] = StaticText()
        self['Statustext'] = StaticText()
        self['statuspic'] = MultiPixmap()
        self['statuspic'].setPixmapNum(1)
        self['statuspic'].show()
        self.iface = None
        self.createscreen()
        self.iStatus = None
        if iNetwork.isWirelessInterface(self.iface):
            try:
                from Plugins.SystemPlugins.WirelessLan.Wlan import iStatus
                self.iStatus = iStatus
            except:
                pass

            self.resetList()
            self.onClose.append(self.cleanup)
        self.updateStatusbar()
        self['key_red'] = StaticText(_('Close'))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions', 'DirectionActions'], {'cancel': self.close,
         'ok': self.close,
         'up': self['AboutScrollLabel'].pageUp,
         'down': self['AboutScrollLabel'].pageDown})
        return

    def createscreen(self):
        self.AboutText = ''
        self.iface = 'eth0'
        eth0 = about.getIfConfig('eth0')
        if eth0.has_key('addr'):
            self.AboutText += _('IP:') + '\t' + eth0['addr'] + '\n'
            if eth0.has_key('netmask'):
                self.AboutText += _('Netmask:') + '\t' + eth0['netmask'] + '\n'
            if eth0.has_key('hwaddr'):
                self.AboutText += _('MAC:') + '\t' + eth0['hwaddr'] + '\n'
            self.iface = 'eth0'
        eth1 = about.getIfConfig('eth1')
        if eth1.has_key('addr'):
            self.AboutText += _('IP:') + '\t' + eth1['addr'] + '\n'
            if eth1.has_key('netmask'):
                self.AboutText += _('Netmask:') + '\t' + eth1['netmask'] + '\n'
            if eth1.has_key('hwaddr'):
                self.AboutText += _('MAC:') + '\t' + eth1['hwaddr'] + '\n'
            self.iface = 'eth1'
        ra0 = about.getIfConfig('ra0')
        if ra0.has_key('addr'):
            self.AboutText += _('IP:') + '\t' + ra0['addr'] + '\n'
            if ra0.has_key('netmask'):
                self.AboutText += _('Netmask:') + '\t' + ra0['netmask'] + '\n'
            if ra0.has_key('hwaddr'):
                self.AboutText += _('MAC:') + '\t' + ra0['hwaddr'] + '\n'
            self.iface = 'ra0'
        wlan0 = about.getIfConfig('wlan0')
        if wlan0.has_key('addr'):
            self.AboutText += _('IP:') + '\t' + wlan0['addr'] + '\n'
            if wlan0.has_key('netmask'):
                self.AboutText += _('Netmask:') + '\t' + wlan0['netmask'] + '\n'
            if wlan0.has_key('hwaddr'):
                self.AboutText += _('MAC:') + '\t' + wlan0['hwaddr'] + '\n'
            self.iface = 'wlan0'
        rx_bytes, tx_bytes = about.getIfTransferredData(self.iface)
        self.AboutText += '\n' + _('Bytes received:') + '\t' + rx_bytes + '\n'
        self.AboutText += _('Bytes sent:') + '\t' + tx_bytes + '\n'
        hostname = file('/proc/sys/kernel/hostname').read()
        self.AboutText += '\n' + _('Hostname:') + '\t' + hostname + '\n'
        self['AboutScrollLabel'] = ScrollLabel(self.AboutText)

    def cleanup(self):
        if self.iStatus:
            self.iStatus.stopWlanConsole()

    def resetList(self):
        if self.iStatus:
            self.iStatus.getDataForInterface(self.iface, self.getInfoCB)

    def getInfoCB(self, data, status):
        self.LinkState = None
        if data is not None:
            if data is True:
                if status is not None:
                    if self.iface == 'wlan0' or self.iface == 'ra0':
                        if status[self.iface]['essid'] == 'off':
                            essid = _('No Connection')
                        else:
                            essid = status[self.iface]['essid']
                        if status[self.iface]['accesspoint'] == 'Not-Associated':
                            accesspoint = _('Not-Associated')
                            essid = _('No Connection')
                        else:
                            accesspoint = status[self.iface]['accesspoint']
                        if self.has_key('BSSID'):
                            self.AboutText += _('Accesspoint:') + '\t' + accesspoint + '\n'
                        if self.has_key('ESSID'):
                            self.AboutText += _('SSID:') + '\t' + essid + '\n'
                        quality = status[self.iface]['quality']
                        if self.has_key('quality'):
                            self.AboutText += _('Link Quality:') + '\t' + quality + '\n'
                        if status[self.iface]['bitrate'] == '0':
                            bitrate = _('Unsupported')
                        else:
                            bitrate = str(status[self.iface]['bitrate']) + ' Mb/s'
                        if self.has_key('bitrate'):
                            self.AboutText += _('Bitrate:') + '\t' + bitrate + '\n'
                        signal = status[self.iface]['signal']
                        if self.has_key('signal'):
                            self.AboutText += _('Signal Strength:') + '\t' + signal + '\n'
                        if status[self.iface]['encryption'] == 'off':
                            if accesspoint == 'Not-Associated':
                                encryption = _('Disabled')
                            else:
                                encryption = _('Unsupported')
                        else:
                            encryption = _('Enabled')
                        if self.has_key('enc'):
                            self.AboutText += _('Encryption:') + '\t' + encryption + '\n'
                        if status[self.iface]['essid'] == 'off' or status[self.iface]['accesspoint'] == 'Not-Associated' or status[self.iface]['accesspoint'] is False:
                            self.LinkState = False
                            self['statuspic'].setPixmapNum(1)
                            self['statuspic'].show()
                        else:
                            self.LinkState = True
                            iNetwork.checkNetworkState(self.checkNetworkCB)
                        self['AboutScrollLabel'].setText(self.AboutText)
        return

    def exit(self):
        self.close(True)

    def updateStatusbar(self):
        self['IFtext'].setText(_('Network:'))
        self['IF'].setText(iNetwork.getFriendlyAdapterName(self.iface))
        self['Statustext'].setText(_('Link:'))
        if iNetwork.isWirelessInterface(self.iface):
            try:
                self.iStatus.getDataForInterface(self.iface, self.getInfoCB)
            except:
                self['statuspic'].setPixmapNum(1)
                self['statuspic'].show()

        else:
            iNetwork.getLinkState(self.iface, self.dataAvail)

    def dataAvail(self, data):
        self.LinkState = None
        for line in data.splitlines():
            line = line.strip()
            if 'Link detected:' in line:
                if 'yes' in line:
                    self.LinkState = True
                else:
                    self.LinkState = False

        if self.LinkState:
            iNetwork.checkNetworkState(self.checkNetworkCB)
        else:
            self['statuspic'].setPixmapNum(1)
            self['statuspic'].show()
        return

    def checkNetworkCB(self, data):
        try:
            if iNetwork.getAdapterAttribute(self.iface, 'up') is True:
                if self.LinkState is True:
                    if data <= 2:
                        self['statuspic'].setPixmapNum(0)
                    else:
                        self['statuspic'].setPixmapNum(1)
                    self['statuspic'].show()
                else:
                    self['statuspic'].setPixmapNum(1)
                    self['statuspic'].show()
            else:
                self['statuspic'].setPixmapNum(1)
                self['statuspic'].show()
        except:
            pass

    def createSummary(self):
        return AboutSummary


class AboutSummary(Screen):

    def __init__(self, session, parent):
        Screen.__init__(self, session, parent=parent)
        EGAMIVersion = _('EGAMI %s') % about.getImageVersionString()
        self['selected'] = Label(EGAMIVersion)
        AboutText = _('Model: %s %s\n') % (getMachineBrand(), getMachineName())
        if path.exists('/proc/stb/info/chipset'):
            chipset = open('/proc/stb/info/chipset', 'r').read()
            AboutText += _('Chipset: BCM%s') % chipset.replace('\n', '') + '\n'
        AboutText += _('Version: %s') % getImageVersion() + '\n'
        AboutText += _('Build: %s') % getImageVersion() + '\n'
        AboutText += _('Kernel: %s') % about.getKernelVersionString() + '\n'
        string = getDriverDate()
        year = string[0:4]
        month = string[4:6]
        day = string[6:8]
        driversdate = '-'.join((year, month, day))
        AboutText += _('Drivers: %s') % driversdate + '\n'
        AboutText += _('Last update: %s') % getEnigmaVersionString() + '\n\n'
        tempinfo = ''
        if path.exists('/proc/stb/sensors/temp0/value'):
            tempinfo = open('/proc/stb/sensors/temp0/value', 'r').read()
        elif path.exists('/proc/stb/fp/temp_sensor'):
            tempinfo = open('/proc/stb/fp/temp_sensor', 'r').read()
        if tempinfo and int(tempinfo.replace('\n', '')) > 0:
            mark = str('\xc2\xb0')
            AboutText += _('System temperature: %s') % tempinfo.replace('\n', '') + mark + 'C\n\n'
        self['AboutText'] = StaticText(AboutText)


class ViewGitLog(Screen):

    def __init__(self, session, args = None):
        Screen.__init__(self, session)
        self.skinName = 'SoftwareUpdateChanges'
        self.setTitle(_('OE Changes'))
        self.logtype = 'oe'
        self['text'] = ScrollLabel()
        self['title_summary'] = StaticText()
        self['text_summary'] = StaticText()
        self['key_red'] = Button(_('Close'))
        self['key_green'] = Button(_('OK'))
        self['key_yellow'] = Button(_('Show E2 Log'))
        self['myactions'] = ActionMap(['ColorActions', 'OkCancelActions', 'DirectionActions'], {'cancel': self.closeRecursive,
         'green': self.closeRecursive,
         'red': self.closeRecursive,
         'yellow': self.changelogtype,
         'left': self.pageUp,
         'right': self.pageDown,
         'down': self.pageDown,
         'up': self.pageUp}, -1)
        self.onLayoutFinish.append(self.getlog)

    def changelogtype(self):
        if self.logtype == 'oe':
            self['key_yellow'].setText(_('Show OE Log'))
            self.setTitle(_('Enigma2 Changes'))
            self.logtype = 'e2'
        else:
            self['key_yellow'].setText(_('Show E2 Log'))
            self.setTitle(_('OE Changes'))
            self.logtype = 'oe'
        self.getlog()

    def pageUp(self):
        self['text'].pageUp()

    def pageDown(self):
        self['text'].pageDown()

    def getlog(self):
        fd = open('/etc/' + self.logtype + '-git.log', 'r')
        releasenotes = fd.read()
        fd.close()
        releasenotes = releasenotes.replace('\negami: build', '\n\nopenatv: build')
        self['text'].setText(releasenotes)
        summarytext = releasenotes
        try:
            self['title_summary'].setText(summarytext[0] + ':')
            self['text_summary'].setText(summarytext[1])
        except:
            self['title_summary'].setText('')
            self['text_summary'].setText('')

    def unattendedupdate(self):
        self.close((_('Unattended upgrade without GUI and reboot system'), 'cold'))

    def closeRecursive(self):
        self.close((_('Cancel'), ''))


class TranslationInfo(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('Translation Information'))
        info = _('TRANSLATOR_INFO')
        if info == 'TRANSLATOR_INFO':
            info = ''
        infolines = _('').split('\n')
        infomap = {}
        for x in infolines:
            l = x.split(': ')
            if len(l) != 2:
                continue
            type, value = l
            infomap[type] = value

        print infomap
        self['key_red'] = Button(_('Cancel'))
        self['TranslationInfo'] = StaticText(info)
        translator_name = infomap.get('Language-Team', 'none')
        if translator_name == 'none':
            translator_name = infomap.get('Last-Translator', '')
        self['TranslatorName'] = StaticText(translator_name)
        self['actions'] = ActionMap(['SetupActions'], {'cancel': self.close,
         'ok': self.close})


class CommitInfo(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skinName = ['CommitInfo', 'About']
        self['AboutScrollLabel'] = ScrollLabel(_('Please wait'))
        self['actions'] = ActionMap(['SetupActions', 'DirectionActions'], {'cancel': self.close,
         'ok': self.close,
         'up': self['AboutScrollLabel'].pageUp,
         'down': self['AboutScrollLabel'].pageDown,
         'left': self.left,
         'right': self.right})
        self['key_red'] = Button(_('Cancel'))
        self.project = 0
        self.projects = [('enigma2', 'Enigma2'),
         ('openpli-oe-core', 'Openpli Oe Core'),
         ('enigma2-plugins', 'Enigma2 Plugins'),
         ('aio-grab', 'Aio Grab'),
         ('gst-plugin-dvbmediasink', 'Gst Plugin Dvbmediasink'),
         ('HenksatSettings', 'Henksat Settings'),
         ('enigma2-plugin-extensions-xmltvimport', 'Plugin Xmltvimport'),
         ('enigma2-plugin-skins-magic', 'Skin Magic SD'),
         ('tuxtxt', 'Tuxtxt')]
        self.cachedProjects = {}
        self.Timer = eTimer()
        self.Timer.callback.append(self.readGithubCommitLogs)
        self.Timer.start(50, True)

    def readGithubCommitLogs(self):
        url = 'https://api.github.com/repos/openpli/%s/commits' % self.projects[self.project][0]
        commitlog = ''
        from datetime import datetime
        from json import loads
        from urllib2 import urlopen
        try:
            commitlog += 80 * '-' + '\n'
            commitlog += url.split('/')[-2] + '\n'
            commitlog += 80 * '-' + '\n'
            for c in loads(urlopen(url, timeout=5).read()):
                creator = c['commit']['author']['name']
                title = c['commit']['message']
                date = datetime.strptime(c['commit']['committer']['date'], '%Y-%m-%dT%H:%M:%SZ').strftime('%x %X')
                commitlog += date + ' ' + creator + '\n' + title + '\n\n'

            commitlog = commitlog.encode('utf-8')
            self.cachedProjects[self.projects[self.project][1]] = commitlog
        except:
            commitlog += _('Currently the commit log cannot be retrieved - please try later again')

        self['AboutScrollLabel'].setText(commitlog)

    def updateCommitLogs(self):
        if self.cachedProjects.has_key(self.projects[self.project][1]):
            self['AboutScrollLabel'].setText(self.cachedProjects[self.projects[self.project][1]])
        else:
            self['AboutScrollLabel'].setText(_('Please wait'))
            self.Timer.start(50, True)

    def left(self):
        self.project = self.project == 0 and len(self.projects) - 1 or self.project - 1
        self.updateCommitLogs()

    def right(self):
        self.project = self.project != len(self.projects) - 1 and self.project + 1 or 0
        self.updateCommitLogs()


class MemoryInfo(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'cancel': self.close,
         'ok': self.getMemoryInfo,
         'green': self.getMemoryInfo,
         'blue': self.clearMemory})
        self['key_red'] = Label(_('Cancel'))
        self['key_green'] = Label(_('Refresh'))
        self['key_blue'] = Label(_('Clear'))
        self['lmemtext'] = Label()
        self['lmemvalue'] = Label()
        self['rmemtext'] = Label()
        self['rmemvalue'] = Label()
        self['pfree'] = Label()
        self['pused'] = Label()
        self['slide'] = ProgressBar()
        self['slide'].setValue(100)
        self['params'] = MemoryInfoSkinParams()
        self['info'] = Label(_("This info is for developers only.\nFor a normal users it is not important.\nDon't panic, please, when here will be displayed any suspicious informations!"))
        self.setTitle(_('Memory Info'))
        self.onLayoutFinish.append(self.getMemoryInfo)

    def getMemoryInfo(self):
        try:
            ltext = rtext = ''
            lvalue = rvalue = ''
            mem = 1
            free = 0
            rows_in_column = self['params'].rows_in_column
            for i, line in enumerate(open('/proc/meminfo', 'r')):
                s = line.strip().split(None, 2)
                if len(s) == 3:
                    name, size, units = s
                elif len(s) == 2:
                    name, size = s
                    units = ''
                else:
                    continue
                if name.startswith('MemTotal'):
                    mem = int(size)
                if name.startswith('MemFree') or name.startswith('Buffers') or name.startswith('Cached'):
                    free += int(size)
                if i < rows_in_column:
                    ltext += ''.join((name, '\n'))
                    lvalue += ''.join((size,
                     ' ',
                     units,
                     '\n'))
                else:
                    rtext += ''.join((name, '\n'))
                    rvalue += ''.join((size,
                     ' ',
                     units,
                     '\n'))

            self['lmemtext'].setText(ltext)
            self['lmemvalue'].setText(lvalue)
            self['rmemtext'].setText(rtext)
            self['rmemvalue'].setText(rvalue)
            self['slide'].setValue(int(100.0 * (mem - free) / mem + 0.25))
            self['pfree'].setText('%.1f %s' % (100.0 * free / mem, '%'))
            self['pused'].setText('%.1f %s' % (100.0 * (mem - free) / mem, '%'))
        except Exception as e:
            print '[About] getMemoryInfo FAIL:', e

        return

    def clearMemory(self):
        eConsoleAppContainer().execute('sync')
        open('/proc/sys/vm/drop_caches', 'w').write('3')
        self.getMemoryInfo()


class MemoryInfoSkinParams(HTMLComponent, GUIComponent):

    def __init__(self):
        GUIComponent.__init__(self)
        self.rows_in_column = 25

    def applySkin(self, desktop, screen):
        if self.skinAttributes is not None:
            attribs = []
            for attrib, value in self.skinAttributes:
                if attrib == 'rowsincolumn':
                    self.rows_in_column = int(value)

            self.skinAttributes = attribs
        return GUIComponent.applySkin(self, desktop, screen)

    GUI_WIDGET = eLabel