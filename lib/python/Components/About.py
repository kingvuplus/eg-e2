# Embedded file name: /usr/lib/enigma2/python/Components/About.py
from Tools.Directories import resolveFilename, SCOPE_SYSETC
from os import path
import sys
import os
import time
from boxbranding import getBoxType, getImageVersion
from sys import modules
import socket, fcntl, struct, time, os

def getVersionString():
    return getImageVersion()


def getImageVersionString():
    try:
        file = open(resolveFilename(SCOPE_SYSETC, 'image-version'), 'r')
        lines = file.readlines()
        for x in lines:
            splitted = x.split('=')
            if splitted[0] == 'version':
                version = splitted[1].replace('\n', '')

        file.close()
        return version
    except IOError:
        return 'unavailable'


def getImageUrlString():
    try:
        file = open(resolveFilename(SCOPE_SYSETC, 'image-version'), 'r')
        lines = file.readlines()
        for x in lines:
            splitted = x.split('=')
            if splitted[0] == 'url':
                version = splitted[1].replace('\n', '')

        file.close()
        return version
    except IOError:
        return 'unavailable'


def getFlashDateString():
    try:
        return time.strftime(_('%Y-%m-%d'), time.localtime(os.stat('/boot').st_ctime))
    except:
        return _('unknown')


def getEnigmaVersionString():
    return getImageVersion()


def getGStreamerVersionString():
    import enigma
    return enigma.getGStreamerVersionString()


def getKernelVersionString():
    try:
        f = open('/proc/version', 'r')
        kernelversion = f.read().split(' ', 4)[2].split('-', 2)[0]
        f.close()
        return kernelversion
    except:
        return _('unknown')


def getLastUpdateString():
    try:
        file = open(resolveFilename(SCOPE_SYSETC, 'image-version'), 'r')
        lines = file.readlines()
        for x in lines:
            splitted = x.split('=')
            if splitted[0] == 'date':
                string = splitted[1].replace('\n', '')
                year = string[0:4]
                month = string[4:6]
                day = string[6:8]
                date = '-'.join((year, month, day))
                hour = string[8:10]
                minute = string[10:12]
                time = ':'.join((hour, minute))
                lastupdated = ' '.join((date, time))

        file.close()
        return lastupdated
    except IOError:
        return _('unavailable')


def getModelString():
    try:
        file = open('/proc/stb/info/boxtype', 'r')
        model = file.readline().strip()
        file.close()
        return model
    except IOError:
        return 'unknown'


def getChipSetString():
    if getBoxType() in ('dm7080', 'dm820'):
        return '7435'
    try:
        f = open('/proc/stb/info/chipset', 'r')
        chipset = f.read()
        f.close()
        return str(chipset.lower().replace('\n', '').replace('bcm', '').replace('brcm', '').replace('sti', ''))
    except IOError:
        return 'unavailable'


def getCPUSpeedString():
    mhz = _('unavailable')
    if getBoxType() in 'vusolo4k':
        return '1.5 GHz'
    try:
        file = open('/proc/cpuinfo', 'r')
        lines = file.readlines()
        for x in lines:
            splitted = x.split(': ')
            if len(splitted) > 1:
                splitted[1] = splitted[1].replace('\n', '')
                if splitted[0].startswith('cpu MHz'):
                    mhz = float(splitted[1].split(' ')[0])
                    if mhz and mhz >= 1000:
                        mhz = '%s GHz' % str(round(mhz / 1000, 1))
                    else:
                        mhz = '%s MHz' % str(round(mhz, 1))

        file.close()
        return mhz
    except IOError:
        return _('unavailable')


def getCPUString():
    if getBoxType() in ('xc7362', 'vusolo4k'):
        return 'Broadcom'
    try:
        system = 'unknown'
        file = open('/proc/cpuinfo', 'r')
        lines = file.readlines()
        for x in lines:
            splitted = x.split(': ')
            if len(splitted) > 1:
                splitted[1] = splitted[1].replace('\n', '')
                if splitted[0].startswith('system type'):
                    system = splitted[1].split(' ')[0]
                elif splitted[0].startswith('Processor'):
                    system = splitted[1].split(' ')[0]

        file.close()
        return system
    except IOError:
        return 'unavailable'


def getCpuCoresString():
    try:
        file = open('/proc/cpuinfo', 'r')
        lines = file.readlines()
        for x in lines:
            splitted = x.split(': ')
            if len(splitted) > 1:
                splitted[1] = splitted[1].replace('\n', '')
                if splitted[0].startswith('processor'):
                    if int(splitted[1]) > 0:
                        cores = 2
                    else:
                        cores = 1

        file.close()
        return cores
    except IOError:
        return _('unavailable')


def _ifinfo(sock, addr, ifname):
    iface = struct.pack('256s', ifname[:15])
    info = fcntl.ioctl(sock.fileno(), addr, iface)
    if addr == 35111:
        return ''.join([ '%02x:' % ord(char) for char in info[18:24] ])[:-1].upper()
    else:
        return socket.inet_ntoa(info[20:24])


def getIfConfig(ifname):
    ifreq = {'ifname': ifname}
    infos = {}
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    infos['addr'] = 35093
    infos['brdaddr'] = 35097
    infos['hwaddr'] = 35111
    infos['netmask'] = 35099
    try:
        for k, v in infos.items():
            ifreq[k] = _ifinfo(sock, v, ifname)

    except:
        pass

    sock.close()
    return ifreq


def getIfTransferredData(ifname):
    f = open('/proc/net/dev', 'r')
    for line in f:
        if ifname in line:
            data = line.split('%s:' % ifname)[1].split()
            rx_bytes, tx_bytes = data[0], data[8]
            f.close()
            return (rx_bytes, tx_bytes)


def getPythonVersionString():
    try:
        import commands
        status, output = commands.getstatusoutput('python -V')
        return output.split(' ')[1]
    except:
        return _('unknown')


about = sys.modules[__name__]