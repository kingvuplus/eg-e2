# Embedded file name: /usr/lib/enigma2/python/Components/InputDevice.py
from os import listdir, open as os_open, close as os_close, write as os_write, O_RDWR, O_NONBLOCK
from fcntl import ioctl
from boxbranding import getBoxType, getBrandOEM
import struct
from config import config, ConfigSubsection, ConfigInteger, ConfigYesNo, ConfigText, ConfigSlider
from Tools.Directories import pathExists
boxtype = getBoxType()
IOC_NRBITS = 8L
IOC_TYPEBITS = 8L
IOC_SIZEBITS = 13L
IOC_DIRBITS = 3L
IOC_NRSHIFT = 0L
IOC_TYPESHIFT = IOC_NRSHIFT + IOC_NRBITS
IOC_SIZESHIFT = IOC_TYPESHIFT + IOC_TYPEBITS
IOC_DIRSHIFT = IOC_SIZESHIFT + IOC_SIZEBITS
IOC_READ = 2L

def EVIOCGNAME(length):
    return IOC_READ << IOC_DIRSHIFT | length << IOC_SIZESHIFT | 69 << IOC_TYPESHIFT | 6 << IOC_NRSHIFT


class inputDevices:

    def __init__(self):
        self.Devices = {}
        self.currentDevice = ''
        self.getInputDevices()

    def getInputDevices(self):
        devices = listdir('/dev/input/')
        for evdev in devices:
            try:
                buffer = '\x00' * 512
                self.fd = os_open('/dev/input/' + evdev, O_RDWR | O_NONBLOCK)
                self.name = ioctl(self.fd, EVIOCGNAME(256), buffer)
                self.name = self.name[:self.name.find('\x00')]
                if str(self.name).find('Keyboard') != -1:
                    self.name = 'keyboard'
                os_close(self.fd)
            except (IOError, OSError) as err:
                print '[InputDevice] getInputDevices ' + evdev + ' <ERROR: ioctl(EVIOCGNAME): ' + str(err) + ' >'
                self.name = None

            if self.name:
                self.Devices[evdev] = {'name': self.name,
                 'type': self.getInputDeviceType(self.name),
                 'enabled': False,
                 'configuredName': None}
                if boxtype.startswith('et'):
                    self.setDefaults(evdev)

        return

    def getInputDeviceType(self, name):
        if 'remote control' in name:
            return 'remote'
        elif 'keyboard' in name:
            return 'keyboard'
        elif 'mouse' in name:
            return 'mouse'
        else:
            print '[InputDevice] Unknown device type:', name
            return None
            return None

    def getDeviceName(self, x):
        if x in self.Devices.keys():
            return self.Devices[x].get('name', x)
        else:
            return 'Unknown device name'

    def getDeviceList(self):
        return sorted(self.Devices.iterkeys())

    def setDeviceAttribute(self, device, attribute, value):
        if self.Devices.has_key(device):
            self.Devices[device][attribute] = value

    def getDeviceAttribute(self, device, attribute):
        if self.Devices.has_key(device):
            if self.Devices[device].has_key(attribute):
                return self.Devices[device][attribute]
        return None

    def setEnabled(self, device, value):
        oldval = self.getDeviceAttribute(device, 'enabled')
        self.setDeviceAttribute(device, 'enabled', value)
        if oldval is True and value is False:
            self.setDefaults(device)

    def setName(self, device, value):
        self.setDeviceAttribute(device, 'configuredName', value)

    def setDefaults(self, device):
        print '[InputDevice] setDefaults for device %s' % device
        self.setDeviceAttribute(device, 'configuredName', None)
        event_repeat = struct.pack('iihhi', 0, 0, 20, 1, 100)
        event_delay = struct.pack('iihhi', 0, 0, 20, 0, 700)
        fd = os_open('/dev/input/' + device, O_RDWR)
        os_write(fd, event_repeat)
        os_write(fd, event_delay)
        os_close(fd)
        return

    def setRepeat(self, device, value):
        if self.getDeviceAttribute(device, 'enabled'):
            print '[InputDevice] setRepeat for device %s to %d ms' % (device, value)
            event = struct.pack('iihhi', 0, 0, 20, 1, int(value))
            fd = os_open('/dev/input/' + device, O_RDWR)
            os_write(fd, event)
            os_close(fd)

    def setDelay(self, device, value):
        if self.getDeviceAttribute(device, 'enabled'):
            print '[InputDevice] setDelay for device %s to %d ms' % (device, value)
            event = struct.pack('iihhi', 0, 0, 20, 0, int(value))
            fd = os_open('/dev/input/' + device, O_RDWR)
            os_write(fd, event)
            os_close(fd)


class InitInputDevices:

    def __init__(self):
        self.currentDevice = ''
        self.createConfig()

    def createConfig(self, *args):
        config.inputDevices = ConfigSubsection()
        for device in sorted(iInputDevices.Devices.iterkeys()):
            self.currentDevice = device
            self.setupConfigEntries(self.currentDevice)
            self.currentDevice = ''

    def inputDevicesEnabledChanged(self, configElement):
        if self.currentDevice != '' and iInputDevices.currentDevice == '':
            iInputDevices.setEnabled(self.currentDevice, configElement.value)
        elif iInputDevices.currentDevice != '':
            iInputDevices.setEnabled(iInputDevices.currentDevice, configElement.value)

    def inputDevicesNameChanged(self, configElement):
        if self.currentDevice != '' and iInputDevices.currentDevice == '':
            iInputDevices.setName(self.currentDevice, configElement.value)
            if configElement.value != '':
                devname = iInputDevices.getDeviceAttribute(self.currentDevice, 'name')
                if devname != configElement.value:
                    cmd = 'config.inputDevices.' + self.currentDevice + '.enabled.value = False'
                    exec cmd
                    cmd = 'config.inputDevices.' + self.currentDevice + '.enabled.save()'
                    exec cmd
        elif iInputDevices.currentDevice != '':
            iInputDevices.setName(iInputDevices.currentDevice, configElement.value)

    def inputDevicesRepeatChanged(self, configElement):
        if self.currentDevice != '' and iInputDevices.currentDevice == '':
            iInputDevices.setRepeat(self.currentDevice, configElement.value)
        elif iInputDevices.currentDevice != '':
            iInputDevices.setRepeat(iInputDevices.currentDevice, configElement.value)

    def inputDevicesDelayChanged(self, configElement):
        if self.currentDevice != '' and iInputDevices.currentDevice == '':
            iInputDevices.setDelay(self.currentDevice, configElement.value)
        elif iInputDevices.currentDevice != '':
            iInputDevices.setDelay(iInputDevices.currentDevice, configElement.value)

    def setupConfigEntries(self, device):
        cmd = 'config.inputDevices.' + device + ' = ConfigSubsection()'
        exec cmd
        if boxtype == 'dm800' or boxtype == 'azboxhd':
            cmd = 'config.inputDevices.' + device + '.enabled = ConfigYesNo(default = True)'
        else:
            cmd = 'config.inputDevices.' + device + '.enabled = ConfigYesNo(default = False)'
        exec cmd
        cmd = 'config.inputDevices.' + device + '.enabled.addNotifier(self.inputDevicesEnabledChanged,config.inputDevices.' + device + '.enabled)'
        exec cmd
        cmd = 'config.inputDevices.' + device + '.name = ConfigText(default="")'
        exec cmd
        cmd = 'config.inputDevices.' + device + '.name.addNotifier(self.inputDevicesNameChanged,config.inputDevices.' + device + '.name)'
        exec cmd
        if boxtype in ('maram9', 'classm', 'axodin', 'axodinc', 'starsatlx', 'genius', 'evo', 'galaxym6'):
            cmd = 'config.inputDevices.' + device + '.repeat = ConfigSlider(default=400, increment = 10, limits=(0, 500))'
        elif boxtype == 'azboxhd':
            cmd = 'config.inputDevices.' + device + '.repeat = ConfigSlider(default=150, increment = 10, limits=(0, 500))'
        elif boxtype == 'mbmicro':
            cmd = 'config.inputDevices.' + device + '.repeat = ConfigSlider(default=30, increment = 10, limits=(0, 500))'
        elif boxtype == 'mbtwinplus':
            cmd = 'config.inputDevices.' + device + '.repeat = ConfigSlider(default=150, increment = 10, limits=(0, 500))'
        else:
            cmd = 'config.inputDevices.' + device + '.repeat = ConfigSlider(default=100, increment = 10, limits=(0, 500))'
        exec cmd
        cmd = 'config.inputDevices.' + device + '.repeat.addNotifier(self.inputDevicesRepeatChanged,config.inputDevices.' + device + '.repeat)'
        exec cmd
        if boxtype in ('maram9', 'classm', 'axodin', 'axodinc', 'starsatlx', 'genius', 'evo', 'galaxym6'):
            cmd = 'config.inputDevices.' + device + '.delay = ConfigSlider(default=200, increment = 100, limits=(0, 5000))'
        elif boxtype == 'mbmicro':
            cmd = 'config.inputDevices.' + device + '.delay = ConfigSlider(default=200, increment = 100, limits=(0, 5000))'
        elif boxtype == 'mbtwinplus':
            cmd = 'config.inputDevices.' + device + '.delay = ConfigSlider(default=400, increment = 100, limits=(0, 5000))'
        else:
            cmd = 'config.inputDevices.' + device + '.delay = ConfigSlider(default=700, increment = 100, limits=(0, 5000))'
        exec cmd
        cmd = 'config.inputDevices.' + device + '.delay.addNotifier(self.inputDevicesDelayChanged,config.inputDevices.' + device + '.delay)'
        exec cmd


iInputDevices = inputDevices()
config.plugins.remotecontroltype = ConfigSubsection()
config.plugins.remotecontroltype.rctype = ConfigInteger(default=0)

class RcTypeControl:

    def __init__(self):
        if pathExists('/proc/stb/ir/rc/type') and pathExists('/proc/stb/info/boxtype') and getBrandOEM() not in ('gigablue', 'odin', 'ini', 'entwopia', 'tripledot'):
            self.isSupported = True
            fd = open('/proc/stb/info/boxtype', 'r')
            self.boxType = fd.read()
            fd.close()
            if config.plugins.remotecontroltype.rctype.value != 0:
                self.writeRcType(config.plugins.remotecontroltype.rctype.value)
        else:
            self.isSupported = False

    def multipleRcSupported(self):
        return self.isSupported

    def getBoxType(self):
        return self.boxType

    def writeRcType(self, rctype):
        fd = open('/proc/stb/ir/rc/type', 'w')
        fd.write('%d' % rctype)
        fd.close()


iRcTypeControl = RcTypeControl()