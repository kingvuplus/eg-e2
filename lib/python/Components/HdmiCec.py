# Embedded file name: /usr/lib/enigma2/python/Components/HdmiCec.py
import struct
import os
from fcntl import ioctl
from sys import maxint
from enigma import eTimer, eHdmiCEC, eActionMap
from config import config, ConfigSelection, ConfigYesNo, ConfigSubsection, ConfigText
from Tools.StbHardware import getFPWasTimerWakeup
from Tools.Directories import fileExists
config.hdmicec = ConfigSubsection()
config.hdmicec.enabled = ConfigYesNo(default=False)
config.hdmicec.control_tv_standby = ConfigYesNo(default=True)
config.hdmicec.control_tv_wakeup = ConfigYesNo(default=True)
config.hdmicec.report_active_source = ConfigYesNo(default=True)
config.hdmicec.report_active_menu = ConfigYesNo(default=True)
config.hdmicec.handle_tv_standby = ConfigYesNo(default=True)
config.hdmicec.handle_tv_wakeup = ConfigYesNo(default=True)
config.hdmicec.tv_wakeup_detection = ConfigSelection(choices={'wakeup': _('Wakeup'),
 'tvreportphysicaladdress': _('TV physical address report'),
 'sourcerequest': _('Source request'),
 'streamrequest': _('Stream request'),
 'osdnamerequest': _('OSD name request'),
 'activity': _('Any activity')}, default='streamrequest')
config.hdmicec.fixed_physical_address = ConfigText(default='0.0.0.0')
config.hdmicec.volume_forwarding = ConfigYesNo(default=False)
config.hdmicec.control_receiver_wakeup = ConfigYesNo(default=False)
config.hdmicec.control_receiver_standby = ConfigYesNo(default=False)
config.hdmicec.handle_deepstandby_events = ConfigYesNo(default=False)
config.hdmicec.preemphasis = ConfigYesNo(default=False)
choicelist = []
for i in (10,
 50,
 100,
 150,
 250,
 500,
 750,
 1000,
 1500,
 2000,
 4000):
    choicelist.append(('%d' % i, '%d ms' % i))

config.hdmicec.minimum_send_interval = ConfigSelection(default='0', choices=[('0', _('Disabled'))] + choicelist)

class HdmiCec():
    instance = None

    def __init__(self):
        if config.hdmicec.enabled.value:
            HdmiCec.instance = self
            self.wait = eTimer()
            self.wait.timeout.get().append(self.sendCmd)
            self.queue = []
            eHdmiCEC.getInstance().messageReceived.get().append(self.messageReceived)
            config.misc.standbyCounter.addNotifier(self.onEnterStandby, initial_call=False)
            config.misc.DeepStandby.addNotifier(self.onEnterDeepStandby, initial_call=False)
            self.setFixedPhysicalAddress(config.hdmicec.fixed_physical_address.value)
            self.volumeForwardingEnabled = False
            self.volumeForwardingDestination = 0
            eActionMap.getInstance().bindAction('', -maxint - 1, self.keyEvent)
            config.hdmicec.volume_forwarding.addNotifier(self.configVolumeForwarding)
            config.hdmicec.enabled.addNotifier(self.configVolumeForwarding)
            if config.hdmicec.handle_deepstandby_events.value:
                if not getFPWasTimerWakeup():
                    self.wakeupMessages()
            dummy = self.checkifPowerupWithoutWakingTv()

    def getPhysicalAddress(self):
        physicaladdress = eHdmiCEC.getInstance().getPhysicalAddress()
        hexstring = '%04x' % physicaladdress
        return hexstring[0] + '.' + hexstring[1] + '.' + hexstring[2] + '.' + hexstring[3]

    def setFixedPhysicalAddress(self, address):
        if address != config.hdmicec.fixed_physical_address.value:
            config.hdmicec.fixed_physical_address.value = address
            config.hdmicec.fixed_physical_address.save()
        hexstring = address[0] + address[2] + address[4] + address[6]
        eHdmiCEC.getInstance().setFixedPhysicalAddress(int(float.fromhex(hexstring)))

    def sendMessage(self, address, message):
        if config.hdmicec.enabled.value:
            cmd = 0
            data = ''
            if message == 'wakeup':
                cmd = 4
            elif message == 'sourceactive':
                address = 15
                cmd = 130
                physicaladdress = eHdmiCEC.getInstance().getPhysicalAddress()
                data = str(struct.pack('BB', int(physicaladdress / 256), int(physicaladdress % 256)))
            elif message == 'standby':
                cmd = 54
            elif message == 'sourceinactive':
                physicaladdress = eHdmiCEC.getInstance().getPhysicalAddress()
                cmd = 157
                data = str(struct.pack('BB', int(physicaladdress / 256), int(physicaladdress % 256)))
            elif message == 'menuactive':
                cmd = 142
                data = str(struct.pack('B', 0))
            elif message == 'menuinactive':
                cmd = 142
                data = str(struct.pack('B', 1))
            elif message == 'givesystemaudiostatus':
                cmd = 125
                address = 5
            elif message == 'setsystemaudiomode':
                cmd = 112
                address = 5
                physicaladdress = eHdmiCEC.getInstance().getPhysicalAddress()
                data = str(struct.pack('BB', int(physicaladdress / 256), int(physicaladdress % 256)))
            elif message == 'osdname':
                cmd = 71
                data = os.uname()[1]
                data = data[:14]
            elif message == 'poweractive':
                cmd = 144
                data = str(struct.pack('B', 0))
            elif message == 'powerinactive':
                cmd = 144
                data = str(struct.pack('B', 1))
            elif message == 'reportaddress':
                address = 15
                cmd = 132
                physicaladdress = eHdmiCEC.getInstance().getPhysicalAddress()
                devicetype = eHdmiCEC.getInstance().getDeviceType()
                data = str(struct.pack('BBB', int(physicaladdress / 256), int(physicaladdress % 256), devicetype))
            elif message == 'vendorid':
                cmd = 135
                data = '\x00\x00\x00'
            elif message == 'keypoweron':
                cmd = 68
                data = str(struct.pack('B', 109))
            elif message == 'keypoweroff':
                cmd = 68
                data = str(struct.pack('B', 108))
            if cmd:
                if config.hdmicec.minimum_send_interval.value != '0' and message != 'standby':
                    self.queue.append((address, cmd, data))
                    if not self.wait.isActive():
                        self.wait.start(int(config.hdmicec.minimum_send_interval.value), True)
                else:
                    eHdmiCEC.getInstance().sendMessage(address, cmd, data, len(data))

    def sendCmd(self):
        if len(self.queue):
            address, cmd, data = self.queue.pop(0)
            eHdmiCEC.getInstance().sendMessage(address, cmd, data, len(data))
            self.wait.start(int(config.hdmicec.minimum_send_interval.value), True)

    def sendMessages(self, address, messages):
        for message in messages:
            self.sendMessage(address, message)

    def wakeupMessages(self):
        if config.hdmicec.enabled.value:
            if self.checkifPowerupWithoutWakingTv() == 'True':
                print "[HdmiCec] Skip waking TV, found 'True' in '/tmp/powerup_without_waking_tv.txt' (usually written by openWebif)"
            else:
                messages = []
                if config.hdmicec.control_tv_wakeup.value:
                    messages.append('wakeup')
                if config.hdmicec.report_active_source.value:
                    messages.append('sourceactive')
                if config.hdmicec.report_active_menu.value:
                    messages.append('menuactive')
                if messages:
                    self.sendMessages(0, messages)
                if config.hdmicec.control_receiver_wakeup.value:
                    self.sendMessage(5, 'keypoweron')
                    self.sendMessage(5, 'setsystemaudiomode')

    def standbyMessages(self):
        if config.hdmicec.enabled.value:
            messages = []
            if config.hdmicec.control_tv_standby.value:
                messages.append('standby')
            else:
                if config.hdmicec.report_active_source.value:
                    messages.append('sourceinactive')
                if config.hdmicec.report_active_menu.value:
                    messages.append('menuinactive')
            if messages:
                self.sendMessages(0, messages)
            if config.hdmicec.control_receiver_standby.value:
                self.sendMessage(5, 'keypoweroff')
                self.sendMessage(5, 'standby')

    def onLeaveStandby(self):
        self.wakeupMessages()

    def onEnterStandby(self, configElement):
        from Screens.Standby import inStandby
        inStandby.onClose.append(self.onLeaveStandby)
        self.standbyMessages()

    def onEnterDeepStandby(self, configElement):
        if config.hdmicec.handle_deepstandby_events.value:
            self.standbyMessages()

    def standby(self):
        from Screens.Standby import Standby, inStandby
        if not inStandby:
            from Tools import Notifications
            Notifications.AddNotification(Standby)

    def wakeup(self):
        from Screens.Standby import Standby, inStandby
        if inStandby:
            inStandby.Power()

    def messageReceived(self, message):
        if config.hdmicec.enabled.value:
            from Screens.Standby import inStandby
            cmd = message.getCommand()
            data = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            length = message.getData(data, len(data))
            if cmd == 0:
                if data[0] == 'D':
                    print 'eHdmiCec: volume forwarding not supported by device %02x' % message.getAddress()
                    self.volumeForwardingEnabled = False
            elif cmd == 70:
                self.sendMessage(message.getAddress(), 'osdname')
            elif cmd == 126 or cmd == 114:
                if data[0] == '\x01':
                    self.volumeForwardingDestination = 5
                else:
                    self.volumeForwardingDestination = 0
                if config.hdmicec.volume_forwarding.value:
                    print 'eHdmiCec: volume forwarding to device %02x enabled' % self.volumeForwardingDestination
                    self.volumeForwardingEnabled = True
            elif cmd == 143:
                if inStandby:
                    self.sendMessage(message.getAddress(), 'powerinactive')
                else:
                    self.sendMessage(message.getAddress(), 'poweractive')
            elif cmd == 131:
                self.sendMessage(message.getAddress(), 'reportaddress')
            elif cmd == 134:
                physicaladdress = ord(data[0]) * 256 + ord(data[1])
                ouraddress = eHdmiCEC.getInstance().getPhysicalAddress()
                if physicaladdress == ouraddress:
                    if not inStandby:
                        if config.hdmicec.report_active_source.value:
                            self.sendMessage(message.getAddress(), 'sourceactive')
            elif cmd == 133:
                if not inStandby:
                    if config.hdmicec.report_active_source.value:
                        self.sendMessage(message.getAddress(), 'sourceactive')
            elif cmd == 140:
                self.sendMessage(message.getAddress(), 'vendorid')
            elif cmd == 141:
                requesttype = ord(data[0])
                if requesttype == 2:
                    if inStandby:
                        self.sendMessage(message.getAddress(), 'menuinactive')
                    else:
                        self.sendMessage(message.getAddress(), 'menuactive')
            if cmd == 54 and config.hdmicec.handle_tv_standby.value:
                self.standby()
            if config.hdmicec.handle_tv_wakeup.value:
                if cmd == 4 and config.hdmicec.tv_wakeup_detection.value == 'wakeup':
                    self.wakeup()
                elif cmd == 132 and config.hdmicec.tv_wakeup_detection.value == 'tvreportphysicaladdress':
                    if ord(data[0]) * 256 + ord(data[1]) == 0 and ord(data[2]) == 0:
                        self.wakeup()
                elif cmd == 133 and config.hdmicec.tv_wakeup_detection.value == 'sourcerequest':
                    self.wakeup()
                elif cmd == 134 and config.hdmicec.tv_wakeup_detection.value == 'streamrequest':
                    physicaladdress = ord(data[0]) * 256 + ord(data[1])
                    ouraddress = eHdmiCEC.getInstance().getPhysicalAddress()
                    if physicaladdress == ouraddress:
                        self.wakeup()
                elif cmd == 70 and config.hdmicec.tv_wakeup_detection.value == 'osdnamerequest':
                    self.wakeup()
                elif cmd != 54 and config.hdmicec.tv_wakeup_detection.value == 'activity':
                    self.wakeup()

    def configVolumeForwarding(self, configElement):
        if config.hdmicec.enabled.value and config.hdmicec.volume_forwarding.value:
            self.volumeForwardingEnabled = True
            self.sendMessage(5, 'givesystemaudiostatus')
        else:
            self.volumeForwardingEnabled = False

    def keyEvent(self, keyCode, keyEvent):
        if not self.volumeForwardingEnabled:
            return
        cmd = 0
        data = ''
        if keyEvent == 0:
            if keyCode == 115:
                cmd = 68
                data = str(struct.pack('B', 65))
            if keyCode == 114:
                cmd = 68
                data = str(struct.pack('B', 66))
            if keyCode == 113:
                cmd = 68
                data = str(struct.pack('B', 67))
        if keyEvent == 2:
            if keyCode == 115:
                cmd = 68
                data = str(struct.pack('B', 65))
            if keyCode == 114:
                cmd = 68
                data = str(struct.pack('B', 66))
            if keyCode == 113:
                cmd = 68
                data = str(struct.pack('B', 67))
        if keyEvent == 1:
            if keyCode == 115 or keyCode == 114 or keyCode == 113:
                cmd = 69
        if cmd:
            eHdmiCEC.getInstance().sendMessage(self.volumeForwardingDestination, cmd, data, len(data))
            return 1
        else:
            return 0

    def sethdmipreemphasis(self):
        try:
            if config.hdmicec.preemphasis.value == True:
                file = open('/proc/stb/hdmi/preemphasis', 'w')
                file.write('on')
                file.close()
            else:
                file = open('/proc/stb/hdmi/preemphasis', 'w')
                file.write('off')
                file.close()
        except:
            return

    def checkifPowerupWithoutWakingTv(self):
        try:
            f = open('/tmp/powerup_without_waking_tv.txt', 'r')
            powerupWithoutWakingTv = f.read()
            f.close()
        except:
            powerupWithoutWakingTv = 'False'

        try:
            f = open('/tmp/powerup_without_waking_tv.txt', 'w')
            f.write('False')
            f.close()
        except:
            print '[HdmiCec] failed writing /tmp/powerup_without_waking_tv.txt'

        return powerupWithoutWakingTv


hdmi_cec = HdmiCec()