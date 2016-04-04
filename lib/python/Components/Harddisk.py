# Embedded file name: /usr/lib/enigma2/python/Components/Harddisk.py
import os
import time
from Tools.CList import CList
from SystemInfo import SystemInfo
from Components.Console import Console
from Tools.HardwareInfo import HardwareInfo
from boxbranding import getMachineName, getBoxType
import Task

def readFile(filename):
    file = open(filename)
    data = file.read().strip()
    file.close()
    return data


def getProcMounts():
    try:
        mounts = open('/proc/mounts', 'r')
        result = []
        tmp = [ line.strip().split(' ') for line in mounts ]
        mounts.close()
        for item in tmp:
            item[1] = item[1].replace('\\040', ' ')
            result.append(item)

        return result
    except IOError as ex:
        print '[Harddisk] Failed to open /proc/mounts', ex
        return []


def isFileSystemSupported(filesystem):
    try:
        file = open('/proc/filesystems', 'r')
        for fs in file:
            if fs.strip().endswith(filesystem):
                file.close()
                return True

        file.close()
        return False
    except Exception as ex:
        print '[Harddisk] Failed to read /proc/filesystems:', ex


def findMountPoint(path):
    path = os.path.abspath(path)
    while not os.path.ismount(path):
        path = os.path.dirname(path)

    return path


DEVTYPE_UDEV = 0
DEVTYPE_DEVFS = 1

class Harddisk():

    def __init__(self, device, removable = False):
        self.device = device
        if os.access('/dev/.udev', 0):
            self.type = DEVTYPE_UDEV
        elif os.access('/dev/.devfsd', 0):
            self.type = DEVTYPE_DEVFS
        else:
            print '[Harddisk] Unable to determine structure of /dev'
        self.max_idle_time = 0
        self.idle_running = False
        self.last_access = time.time()
        self.last_stat = 0
        self.timer = None
        self.is_sleeping = False
        self.dev_path = ''
        self.disk_path = ''
        self.mount_path = None
        self.mount_device = None
        self.phys_path = os.path.realpath(self.sysfsPath('device'))
        if self.type == DEVTYPE_UDEV:
            self.dev_path = '/dev/' + self.device
            self.disk_path = self.dev_path
        elif self.type == DEVTYPE_DEVFS:
            tmp = readFile(self.sysfsPath('dev')).split(':')
            s_major = int(tmp[0])
            s_minor = int(tmp[1])
            for disc in os.listdir('/dev/discs'):
                dev_path = os.path.realpath('/dev/discs/' + disc)
                disk_path = dev_path + '/disc'
                try:
                    rdev = os.stat(disk_path).st_rdev
                except OSError:
                    continue

                if s_major == os.major(rdev) and s_minor == os.minor(rdev):
                    self.dev_path = dev_path
                    self.disk_path = disk_path
                    break

        print '[Harddisk] new Harddisk', self.device, '->', self.dev_path, '->', self.disk_path
        if not removable:
            self.startIdle()
        return

    def __lt__(self, ob):
        return self.device < ob.device

    def partitionPath(self, n):
        if self.type == DEVTYPE_UDEV:
            if self.dev_path.startswith('/dev/mmcblk'):
                return self.dev_path + 'p' + n
            else:
                return self.dev_path + n
        elif self.type == DEVTYPE_DEVFS:
            return self.dev_path + '/part' + n

    def sysfsPath(self, filename):
        return os.path.join('/sys/block/', self.device, filename)

    def stop(self):
        if self.timer:
            self.timer.stop()
            self.timer.callback.remove(self.runIdle)

    def bus(self):
        ret = _('External')
        if self.type == DEVTYPE_UDEV:
            card = 'sdhci' in self.phys_path
            type_name = ' (SD/MMC)'
        elif self.type == DEVTYPE_DEVFS:
            card = self.device[:2] == 'hd' and 'host0' not in self.dev_path
            type_name = ' (CF)'
        hw_type = HardwareInfo().get_device_name()
        if hw_type == 'elite' or hw_type == 'premium' or hw_type == 'premium+' or hw_type == 'ultra':
            internal = 'ide' in self.phys_path
        else:
            internal = ('pci' or 'ahci') in self.phys_path
        if card:
            ret += type_name
        elif internal:
            ret = _('Internal')
        return ret

    def diskSize(self):
        cap = 0
        try:
            line = readFile(self.sysfsPath('size'))
            cap = int(line)
        except:
            dev = self.findMount()
            if dev:
                stat = os.statvfs(dev)
                cap = int(stat.f_blocks * stat.f_bsize)
                return cap / 1000 / 1000
            else:
                return cap

        return cap / 1000 * 512 / 1000

    def capacity(self):
        cap = self.diskSize()
        if cap == 0:
            return ''
        if cap < 1000:
            return '%03d MB' % cap
        return '%d.%03d GB' % (cap / 1000, cap % 1000)

    def model(self):
        try:
            if self.device[:2] == 'hd':
                return readFile('/proc/ide/' + self.device + '/model')
            if self.device[:2] == 'sd':
                vendor = readFile(self.phys_path + '/vendor')
                model = readFile(self.phys_path + '/model')
                return vendor + '(' + model + ')'
            if self.device.startswith('mmcblk'):
                return readFile(self.sysfsPath('device/name'))
            raise Exception, 'no hdX or sdX or mmcX'
        except Exception as e:
            print '[Harddisk] Failed to get model:', e
            return '-?-'

    def free(self):
        dev = self.findMount()
        if dev:
            if not os.path.exists(dev):
                os.mkdir(dev)
            stat = os.statvfs(dev)
            return int(stat.f_bfree / 1000 * (stat.f_bsize / 1024))
        return -1

    def numPartitions(self):
        numPart = -1
        if self.type == DEVTYPE_UDEV:
            try:
                devdir = os.listdir('/dev')
            except OSError:
                return -1

            for filename in devdir:
                if filename.startswith(self.device):
                    numPart += 1

        elif self.type == DEVTYPE_DEVFS:
            try:
                idedir = os.listdir(self.dev_path)
            except OSError:
                return -1

            for filename in idedir:
                if filename.startswith('disc'):
                    numPart += 1
                if filename.startswith('part'):
                    numPart += 1

        return numPart

    def mountDevice(self):
        for parts in getProcMounts():
            if os.path.realpath(parts[0]).startswith(self.dev_path):
                self.mount_device = parts[0]
                self.mount_path = parts[1]
                return parts[1]

    def enumMountDevices(self):
        for parts in getProcMounts():
            if os.path.realpath(parts[0]).startswith(self.dev_path):
                yield parts[1]

    def findMount(self):
        if self.mount_path is None:
            return self.mountDevice()
        else:
            return self.mount_path

    def unmount(self):
        dev = self.mountDevice()
        if dev is None:
            return 0
        else:
            cmd = 'umount ' + dev
            print '[Harddisk]', cmd
            res = os.system(cmd)
            return res >> 8

    def createPartition(self):
        cmd = 'printf "8,\n;0,0\n;0,0\n;0,0\ny\n" | sfdisk -f -uS ' + self.disk_path
        res = os.system(cmd)
        return res >> 8

    def mkfs(self):
        return 1

    def mount(self):
        if self.mount_device is None:
            dev = self.partitionPath('1')
        else:
            dev = self.mount_device
        try:
            fstab = open('/etc/fstab')
            lines = fstab.readlines()
            fstab.close()
        except IOError:
            return -1

        for line in lines:
            parts = line.strip().split(' ')
            fspath = os.path.realpath(parts[0])
            if fspath == dev:
                print '[Harddisk] mounting:', fspath
                cmd = 'mount -t auto ' + fspath
                res = os.system(cmd)
                return res >> 8

        res = -1
        if self.type == DEVTYPE_UDEV:
            res = os.system('hdparm -z ' + self.disk_path)
            from time import sleep
            sleep(3)
        return res >> 8

    def fsck(self):
        return 1

    def killPartitionTable(self):
        zero = 512 * '\x00'
        h = open(self.dev_path, 'wb')
        for i in range(9):
            h.write(zero)

        h.close()

    def killPartition(self, n):
        zero = 512 * '\x00'
        part = self.partitionPath(n)
        h = open(part, 'wb')
        for i in range(3):
            h.write(zero)

        h.close()

    def createInitializeJob(self):
        job = Task.Job(_('Initializing storage device...'))
        size = self.diskSize()
        print '[Harddisk] [HD] size: %s MB' % size
        task = UnmountTask(job, self)
        task = Task.PythonTask(job, _('Removing partition table'))
        task.work = self.killPartitionTable
        task.weighting = 1
        task = Task.LoggingTask(job, _('Rereading partition table'))
        task.weighting = 1
        task.setTool('hdparm')
        task.args.append('-z')
        task.args.append(self.disk_path)
        task = Task.ConditionTask(job, _('Waiting for partition'), timeoutCount=20)
        task.check = lambda : not os.path.exists(self.partitionPath('1'))
        task.weighting = 1
        if os.path.exists('/usr/sbin/parted'):
            use_parted = True
        elif size > 2097151:
            addInstallTask(job, 'parted')
            use_parted = True
        else:
            use_parted = False
        task = Task.LoggingTask(job, _('Creating partition'))
        task.weighting = 5
        if use_parted:
            task.setTool('parted')
            if size < 1024:
                alignment = 'min'
            else:
                alignment = 'opt'
            if size > 2097151:
                parttype = 'gpt'
            else:
                parttype = 'msdos'
            task.args += ['-a',
             alignment,
             '-s',
             self.disk_path,
             'mklabel',
             parttype,
             'mkpart',
             'primary',
             '0%',
             '100%']
        else:
            task.setTool('sfdisk')
            task.args.append('-f')
            task.args.append('-uS')
            task.args.append(self.disk_path)
            if size > 128000:
                print '[Harddisk] [HD] Detected >128GB disk, using 4k alignment'
                task.initial_input = '8,\n;0,0\n;0,0\n;0,0\ny\n'
            else:
                task.initial_input = '0,\n;\n;\n;\ny\n'
        task = Task.ConditionTask(job, _('Waiting for partition'))
        task.check = lambda : os.path.exists(self.partitionPath('1'))
        task.weighting = 1
        task = MkfsTask(job, _('Creating file system'))
        big_o_options = ['dir_index']
        if isFileSystemSupported('ext4'):
            task.setTool('mkfs.ext4')
            if size > 20000:
                try:
                    file = open('/proc/version', 'r')
                    version = map(int, file.read().split(' ', 4)[2].split('.', 2)[:2])
                    file.close()
                    if version[0] > 3 or version[0] > 2 and version[1] >= 2:
                        task.args += ['-C', '262144']
                        big_o_options.append('bigalloc')
                except Exception as ex:
                    print '[Harddisk] Failed to detect Linux version:', ex

        else:
            task.setTool('mkfs.ext3')
        if size > 250000:
            task.args += ['-T',
             'largefile',
             '-N',
             '262144']
            big_o_options.append('sparse_super')
        elif size > 16384:
            task.args += ['-T', 'largefile']
            big_o_options.append('sparse_super')
        elif size > 2048:
            task.args += ['-T',
             'largefile',
             '-N',
             str(size * 32)]
        task.args += ['-L',
         getMachineName(),
         '-m0',
         '-O',
         ','.join(big_o_options),
         self.partitionPath('1')]
        task = MountTask(job, self)
        task.weighting = 3
        task = Task.ConditionTask(job, _('Waiting for mount'), timeoutCount=20)
        task.check = self.mountDevice
        task.weighting = 1
        return job

    def initialize(self):
        return -5

    def check(self):
        return -5

    def createCheckJob(self):
        job = Task.Job(_('Checking file system...'))
        if self.findMount():
            UnmountTask(job, self)
            dev = self.mount_device
        else:
            dev = self.partitionPath('1')
        task = Task.LoggingTask(job, 'fsck')
        if isFileSystemSupported('ext4'):
            task.setTool('fsck.ext4')
        else:
            task.setTool('fsck.ext3')

        class FsckReturncodePostCondition(Task.ReturncodePostcondition):

            def check(self, task):
                return task.returncode < 4

        task.postconditions = [FsckReturncodePostCondition()]
        task.args += ['-D',
         '-f',
         '-p',
         dev]
        MountTask(job, self)
        task = Task.ConditionTask(job, _('Waiting for mount'))
        task.check = self.mountDevice
        return job

    def createExt4ConversionJob(self):
        if not isFileSystemSupported('ext4'):
            raise Exception, _('You system does not support ext4')
        job = Task.Job(_('Converting ext3 to ext4...'))
        if not os.path.exists('/sbin/tune2fs'):
            addInstallTask(job, 'e2fsprogs-tune2fs')
        if self.findMount():
            UnmountTask(job, self)
            dev = self.mount_device
        else:
            dev = self.partitionPath('1')
        task = Task.LoggingTask(job, 'fsck')
        task.setTool('fsck.ext3')
        task.args.append('-p')
        task.args.append(dev)
        task = Task.LoggingTask(job, 'tune2fs')
        task.setTool('tune2fs')
        task.args.append('-O')
        task.args.append('extent,flex_bg,uninit_bg,dir_index,filetype')
        task.args.append('-o')
        task.args.append('journal_data_writeback')
        task.args.append(dev)
        task = Task.LoggingTask(job, 'fsck')
        task.setTool('fsck.ext4')
        task.postconditions = []
        task.args.append('-f')
        task.args.append('-p')
        task.args.append('-D')
        task.args.append(dev)
        MountTask(job, self)
        task = Task.ConditionTask(job, _('Waiting for mount'))
        task.check = self.mountDevice
        return job

    def getDeviceDir(self):
        return self.dev_path

    def getDeviceName(self):
        return self.disk_path

    def readStats(self):
        if os.path.exists('/sys/block/%s/stat' % self.device):
            f = open('/sys/block/%s/stat' % self.device)
            l = f.read()
            f.close()
            data = l.split(None, 5)
            return (int(data[0]), int(data[4]))
        else:
            return (-1, -1)
            return

    def startIdle(self):
        from enigma import eTimer
        if self.bus() == _('External'):
            Console().ePopen(('sdparm',
             'sdparm',
             '--set=SCT=0',
             self.disk_path))
            Console().ePopen(('hdparm',
             'hdparm',
             '-S0',
             self.disk_path))
        else:
            Console().ePopen(('hdparm',
             'hdparm',
             '-S0',
             self.disk_path))
        self.timer = eTimer()
        self.timer.callback.append(self.runIdle)
        self.idle_running = True
        self.setIdleTime(self.max_idle_time)

    def runIdle(self):
        if not self.max_idle_time:
            return
        t = time.time()
        idle_time = t - self.last_access
        stats = self.readStats()
        l = sum(stats)
        if l != self.last_stat and l >= 0:
            self.last_stat = l
            self.last_access = t
            idle_time = 0
            self.is_sleeping = False
        if idle_time >= self.max_idle_time and not self.is_sleeping:
            self.setSleep()
            self.is_sleeping = True

    def setSleep(self):
        if self.bus() == _('External'):
            Console().ePopen(('sdparm',
             'sdparm',
             '--flexible',
             '--readonly',
             '--command=stop',
             self.disk_path))
            Console().ePopen(('hdparm',
             'hdparm',
             '-y',
             self.disk_path))
        else:
            Console().ePopen(('hdparm',
             'hdparm',
             '-y',
             self.disk_path))

    def setIdleTime(self, idle):
        self.max_idle_time = idle
        if self.idle_running:
            if not idle:
                self.timer.stop()
            else:
                self.timer.start(idle * 100, False)

    def isSleeping(self):
        return self.is_sleeping


class Partition():

    def __init__(self, mountpoint, device = None, description = '', force_mounted = False):
        self.mountpoint = mountpoint
        self.description = description
        self.force_mounted = mountpoint and force_mounted
        self.is_hotplug = force_mounted
        self.device = device

    def __str__(self):
        return 'Partition(mountpoint=%s,description=%s,device=%s)' % (self.mountpoint, self.description, self.device)

    def stat(self):
        if self.mountpoint:
            return os.statvfs(self.mountpoint)
        raise OSError, 'Device %s is not mounted' % self.device

    def free(self):
        try:
            s = self.stat()
            return s.f_bavail * s.f_bsize
        except OSError:
            return None

        return None

    def total(self):
        try:
            s = self.stat()
            return s.f_blocks * s.f_bsize
        except OSError:
            return None

        return None

    def tabbedDescription(self):
        if self.mountpoint.startswith('/media/net') or self.mountpoint.startswith('/media/autofs'):
            return self.description
        return self.description + '\t' + self.mountpoint

    def mounted(self, mounts = None):
        if self.force_mounted:
            return True
        else:
            if self.mountpoint:
                if mounts is None:
                    mounts = getProcMounts()
                for parts in mounts:
                    if self.mountpoint.startswith(parts[1]):
                        return True

            return False

    def filesystem(self, mounts = None):
        if self.mountpoint:
            if mounts is None:
                mounts = getProcMounts()
            for fields in mounts:
                if self.mountpoint.endswith('/') and not self.mountpoint == '/':
                    if fields[1] + '/' == self.mountpoint:
                        return fields[2]
                elif fields[1] == self.mountpoint:
                    return fields[2]

        return ''


DEVICEDB = {'ini-2000sv': {'/devices/platform/ohci-brcm.0/usb2/2-2/': 'Front USB Slot',
                '/devices/platform/ohci-brcm.0/usb2/2-1/': 'Back USB Slot',
                '/devices/platform/ehci-brcm.0/usb1/1-2/': 'Front USB Slot',
                '/devices/platform/ehci-brcm.0/usb1/1-1/': 'Back USB Slot',
                '/devices/platform/strict-ahci.0/ata1/': 'Internal HDD'},
 'ini-5000sv': {'/devices/platform/ohci-brcm.1/usb4/4-1/': 'Front USB Slot',
                '/devices/platform/ohci-brcm.0/usb3/3-2/': 'Back, upper USB Slot',
                '/devices/platform/ohci-brcm.0/usb3/3-1/': 'Back, lower USB Slot',
                '/devices/platform/ehci-brcm.1/usb2/2-1/': 'Front USB Slot',
                '/devices/platform/ehci-brcm.0/usb1/1-2/': 'Back, upper USB Slot',
                '/devices/platform/ehci-brcm.0/usb1/1-1/': 'Back, lower USB Slot',
                '/devices/pci0000:01/0000:01:00.0/ata1/': 'Internal HDD',
                '/devices/pci0000:01/0000:01:00.0/ata2/': 'eSATA HDD'},
 'ini-8000sv': {'/devices/platform/ohci-brcm.2/usb7/7-1/': 'Front USB Slot',
                '/devices/platform/ohci-brcm.1/usb6/6-1/': 'Back, upper USB Slot',
                '/devices/platform/ohci-brcm.0/usb5/5-1/': 'Back, lower USB Slot',
                '/devices/platform/ehci-brcm.2/usb3/3-1/': 'Front USB Slot',
                '/devices/platform/ehci-brcm.1/usb2/2-1/': 'Back, upper USB Slot',
                '/devices/platform/ehci-brcm.0/usb1/1-1/': 'Back, lower USB Slot',
                '/devices/platform/strict-ahci.0/ata1/': 'Internal HDD',
                '/devices/platform/strict-ahci.0/ata2/': 'eSATA HDD'},
 'dm8000': {'/devices/pci0000:01/0000:01:00.0/host1/target1:0:0/1:0:0:0': _('SATA'),
            '/devices/platform/brcm-ehci.0/usb1/1-1/1-1.1/1-1.1:1.0': _('Front USB'),
            '/devices/platform/brcm-ehci.0/usb1/1-1/1-1.1/1-1.1.': _('Front USB'),
            '/devices/platform/brcm-ehci.0/usb1/1-1/1-1.2/1-1.2:1.0': _('Back, upper USB'),
            '/devices/platform/brcm-ehci.0/usb1/1-1/1-1.2/1-1.2.': _('Back, upper USB'),
            '/devices/platform/brcm-ehci.0/usb1/1-1/1-1.3/1-1.3:1.0': _('Back, lower USB'),
            '/devices/platform/brcm-ehci.0/usb1/1-1/1-1.3/1-1.3.': _('Back, lower USB'),
            '/devices/platform/brcm-ehci-1.1/usb2/2-1/2-1:1.0/': _('Internal USB'),
            '/devices/platform/brcm-ohci-1.1/usb4/4-1/4-1:1.0/': _('Internal USB'),
            '/devices/platform/brcm-ehci.0/usb1/1-1/1-1.4/1-1.4.': _('Internal USB')},
 'dm7020hd': {'/devices/pci0000:01/0000:01:00.0/host0/target0:0:0/0:0:0:0': _('SATA'),
              '/devices/pci0000:01/0000:01:00.0/host1/target1:0:0/1:0:0:0': _('eSATA'),
              '/devices/platform/brcm-ehci-1.1/usb2/2-1/2-1:1.0': _('Front USB'),
              '/devices/platform/brcm-ehci-1.1/usb2/2-1/2-1.': _('Front USB'),
              '/devices/platform/brcm-ehci.0/usb1/1-2/1-2:1.0': _('Back, upper USB'),
              '/devices/platform/brcm-ehci.0/usb1/1-2/1-2.': _('Back, upper USB'),
              '/devices/platform/brcm-ehci.0/usb1/1-1/1-1:1.0': _('Back, lower USB'),
              '/devices/platform/brcm-ehci.0/usb1/1-1/1-1.': _('Back, lower USB')},
 'dm7080': {'/devices/pci0000:00/0000:00:00.0/usb9/9-1/': _('Back USB 3.0'),
            '/devices/pci0000:00/0000:00:00.0/usb9/9-2/': _('Front USB 3.0'),
            '/devices/platform/ehci-brcm.0/': _('Back, lower USB'),
            '/devices/platform/ehci-brcm.1/': _('Back, upper USB'),
            '/devices/platform/ehci-brcm.2/': _('Internal USB'),
            '/devices/platform/ehci-brcm.3/': _('Internal USB'),
            '/devices/platform/ohci-brcm.0/': _('Back, lower USB'),
            '/devices/platform/ohci-brcm.1/': _('Back, upper USB'),
            '/devices/platform/ohci-brcm.2/': _('Internal USB'),
            '/devices/platform/ohci-brcm.3/': _('Internal USB'),
            '/devices/platform/sdhci-brcmstb.0/': _('eMMC'),
            '/devices/platform/sdhci-brcmstb.1/': _('SD'),
            '/devices/platform/strict-ahci.0/ata1/': _('SATA'),
            '/devices/platform/strict-ahci.0/ata2/': _('SATA')},
 'dm800': {'/devices/pci0000:01/0000:01:00.0/host0/target0:0:0/0:0:0:0': _('SATA'),
           '/devices/platform/brcm-ehci.0/usb1/1-2/1-2:1.0': _('Upper USB'),
           '/devices/platform/brcm-ehci.0/usb1/1-1/1-1:1.0': _('Lower USB')},
 'dm820': {'/devices/platform/ehci-brcm.0/': _('Back, lower USB'),
           '/devices/platform/ehci-brcm.1/': _('Back, upper USB'),
           '/devices/platform/ehci-brcm.2/': _('Internal USB'),
           '/devices/platform/ehci-brcm.3/': _('Internal USB'),
           '/devices/platform/ohci-brcm.0/': _('Back, lower USB'),
           '/devices/platform/ohci-brcm.1/': _('Back, upper USB'),
           '/devices/platform/ohci-brcm.2/': _('Internal USB'),
           '/devices/platform/ohci-brcm.3/': _('Internal USB'),
           '/devices/platform/sdhci-brcmstb.0/': _('eMMC'),
           '/devices/platform/sdhci-brcmstb.1/': _('SD'),
           '/devices/platform/strict-ahci.0/ata1/': _('SATA'),
           '/devices/platform/strict-ahci.0/ata2/': _('SATA')},
 'dm800se': {'/devices/pci0000:01/0000:01:00.0/host0/target0:0:0/0:0:0:0': _('SATA'),
             '/devices/pci0000:01/0000:01:00.0/host1/target1:0:0/1:0:0:0': _('eSATA'),
             '/devices/platform/brcm-ehci.0/usb1/1-2/1-2:1.0': _('Upper USB'),
             '/devices/platform/brcm-ehci.0/usb1/1-1/1-1:1.0': _('Lower USB')},
 'dm500hd': {'/devices/pci0000:01/0000:01:00.0/host1/target1:0:0/1:0:0:0': _('eSATA'),
             '/devices/pci0000:01/0000:01:00.0/host0/target0:0:0/0:0:0:0': _('eSATA')},
 'dm800sev2': {'/devices/pci0000:01/0000:01:00.0/host0/target0:0:0/0:0:0:0': _('SATA'),
               '/devices/pci0000:01/0000:01:00.0/host1/target1:0:0/1:0:0:0': _('eSATA'),
               '/devices/platform/brcm-ehci.0/usb1/1-2/1-2:1.0': _('Upper USB'),
               '/devices/platform/brcm-ehci.0/usb1/1-1/1-1:1.0': _('Lower USB')},
 'dm500hdv2': {'/devices/pci0000:01/0000:01:00.0/host1/target1:0:0/1:0:0:0': _('eSATA'),
               '/devices/pci0000:01/0000:01:00.0/host0/target0:0:0/0:0:0:0': _('eSATA')},
 'dm7025': {'/devices/pci0000:00/0000:00:14.1/ide1/1.0': 'Compact Flash',
            '/devices/pci0000:00/0000:00:14.1/ide0/0.0': 'Internal Harddisk'}}

def addInstallTask(job, package):
    task = Task.LoggingTask(job, 'update packages')
    task.setTool('opkg')
    task.args.append('update')
    task = Task.LoggingTask(job, 'Install ' + package)
    task.setTool('opkg')
    task.args.append('install')
    task.args.append(package)


class HarddiskManager():

    def __init__(self):
        self.hdd = []
        self.cd = ''
        self.partitions = []
        self.devices_scanned_on_init = []
        self.on_partition_list_change = CList()
        self.enumerateBlockDevices()
        self.enumerateNetworkMounts()
        p = [('/', _('Internal Flash')), ('/media/upnp', _('DLNA'))]
        self.partitions.extend([ Partition(mountpoint=x[0], description=x[1]) for x in p ])

    def getBlockDevInfo(self, blockdev):
        devpath = '/sys/block/' + blockdev
        error = False
        removable = False
        blacklisted = False
        is_cdrom = False
        partitions = []
        try:
            if os.path.exists(devpath + '/removable'):
                removable = bool(int(readFile(devpath + '/removable')))
            if os.path.exists(devpath + '/dev'):
                dev = int(readFile(devpath + '/dev').split(':')[0])
            else:
                dev = None
            if getBoxType() in 'vusolo4k':
                devlist = [1,
                 7,
                 31,
                 253,
                 254,
                 179]
            else:
                devlist = [1,
                 7,
                 31,
                 253,
                 254]
            if dev in devlist:
                blacklisted = True
            if blockdev[0:2] == 'sr':
                is_cdrom = True
            if blockdev[0:2] == 'hd':
                try:
                    media = readFile('/proc/ide/%s/media' % blockdev)
                    if 'cdrom' in media:
                        is_cdrom = True
                except IOError:
                    error = True

            if not is_cdrom and os.path.exists(devpath):
                for partition in os.listdir(devpath):
                    if partition[0:len(blockdev)] != blockdev:
                        continue
                    partitions.append(partition)

            else:
                self.cd = blockdev
        except IOError:
            error = True

        medium_found = True
        try:
            if os.path.exists('/dev/' + blockdev):
                open('/dev/' + blockdev).close()
        except IOError as err:
            if err.errno == 159:
                medium_found = False

        return (error,
         blacklisted,
         removable,
         is_cdrom,
         partitions,
         medium_found)

    def enumerateBlockDevices(self):
        print '[Harddisk] enumerating block devices...'
        for blockdev in os.listdir('/sys/block'):
            error, blacklisted, removable, is_cdrom, partitions, medium_found = self.addHotplugPartition(blockdev)
            if not error and not blacklisted and medium_found:
                for part in partitions:
                    self.addHotplugPartition(part)

                self.devices_scanned_on_init.append((blockdev,
                 removable,
                 is_cdrom,
                 medium_found))

    def enumerateNetworkMounts(self):
        print '[Harddisk] enumerating network mounts...'
        netmount = os.path.exists('/media/net') and os.listdir('/media/net') or ''
        if len(netmount) > 0:
            for fil in netmount:
                if os.path.ismount('/media/net/' + fil):
                    print '[Harddisk] new Network Mount', fil, '->', os.path.join('/media/net/', fil)
                    self.partitions.append(Partition(mountpoint=os.path.join('/media/net/', fil + '/'), description=fil))

        autofsmount = os.path.exists('/media/autofs') and os.listdir('/media/autofs') or ''
        if len(autofsmount) > 0:
            for fil in autofsmount:
                if os.path.ismount('/media/autofs/' + fil) or os.path.exists('/media/autofs/' + fil):
                    print '[Harddisk] new Network Mount', fil, '->', os.path.join('/media/autofs/', fil)
                    self.partitions.append(Partition(mountpoint=os.path.join('/media/autofs/', fil + '/'), description=fil))

        if os.path.ismount('/media/hdd') and '/media/hdd/' not in [ p.mountpoint for p in self.partitions ]:
            print '[Harddisk] new Network Mount being used as HDD replacement -> /media/hdd/'
            self.partitions.append(Partition(mountpoint='/media/hdd/', description='/media/hdd'))

    def getAutofsMountpoint(self, device):
        r = self.getMountpoint(device)
        if r is None:
            return '/media/' + device
        else:
            return r

    def getMountpoint(self, device):
        dev = '/dev/%s' % device
        for item in getProcMounts():
            if item[0] == dev:
                return item[1] + '/'

        return None

    def addHotplugPartition(self, device, physdev = None):
        if not physdev:
            dev, part = self.splitDeviceName(device)
            try:
                physdev = os.path.realpath('/sys/block/' + dev + '/device')[4:]
            except OSError:
                physdev = dev
                print "[Harddisk] couldn't determine blockdev physdev for device", device

        error, blacklisted, removable, is_cdrom, partitions, medium_found = self.getBlockDevInfo(self.splitDeviceName(device)[0])
        hw_type = HardwareInfo().get_device_name()
        if hw_type == 'elite' or hw_type == 'premium' or hw_type == 'premium+' or hw_type == 'ultra':
            if device[0:3] == 'hda':
                blacklisted = True
        if not blacklisted and medium_found:
            description = self.getUserfriendlyDeviceName(device, physdev)
            p = Partition(mountpoint=self.getMountpoint(device), description=description, force_mounted=True, device=device)
            self.partitions.append(p)
            if p.mountpoint:
                self.on_partition_list_change('add', p)
            l = len(device)
            if l and (not device[l - 1].isdigit() or device.startswith('mmcblk')):
                self.hdd.append(Harddisk(device, removable))
                self.hdd.sort()
                SystemInfo['Harddisk'] = True
        return (error,
         blacklisted,
         removable,
         is_cdrom,
         partitions,
         medium_found)

    def removeHotplugPartition(self, device):
        for x in self.partitions[:]:
            if x.device == device:
                self.partitions.remove(x)
                if x.mountpoint:
                    self.on_partition_list_change('remove', x)

        l = len(device)
        if l and not device[l - 1].isdigit():
            for hdd in self.hdd:
                if hdd.device == device:
                    hdd.stop()
                    self.hdd.remove(hdd)
                    break

            SystemInfo['Harddisk'] = len(self.hdd) > 0

    def HDDCount(self):
        return len(self.hdd)

    def HDDList(self):
        list = []
        for hd in self.hdd:
            hdd = hd.model() + ' - ' + hd.bus()
            cap = hd.capacity()
            if cap != '':
                hdd += ' (' + cap + ')'
            list.append((hdd, hd))

        return list

    def getCD(self):
        return self.cd

    def getMountedPartitions(self, onlyhotplug = False, mounts = None):
        if mounts is None:
            mounts = getProcMounts()
        parts = [ x for x in self.partitions if (x.is_hotplug or not onlyhotplug) and x.mounted(mounts) ]
        devs = set([ x.device for x in parts ])
        for devname in devs.copy():
            if not devname:
                continue
            dev, part = self.splitDeviceName(devname)
            if part and dev in devs:
                devs.remove(dev)

        return [ x for x in parts if not x.device or x.device in devs ]

    def splitDeviceName(self, devname):
        dev = devname[:3]
        part = devname[3:]
        for p in part:
            if not p.isdigit():
                return (devname, 0)

        return (dev, part and int(part) or 0)

    def getUserfriendlyDeviceName(self, dev, phys):
        dev, part = self.splitDeviceName(dev)
        description = _('External Storage %s') % dev
        try:
            description = readFile('/sys' + phys + '/model')
        except IOError as s:
            print "[Harddisk] couldn't read model: ", s

        from Tools.HardwareInfo import HardwareInfo
        for physdevprefix, pdescription in DEVICEDB.get(HardwareInfo().device_name, {}).items():
            if phys.startswith(physdevprefix):
                description = pdescription

        if part and part != 1:
            description += _(' (Partition %d)') % part
        return description

    def addMountedPartition(self, device, desc):
        for x in self.partitions:
            if x.mountpoint == device:
                return

        self.partitions.append(Partition(mountpoint=device, description=desc))

    def removeMountedPartition(self, mountpoint):
        for x in self.partitions[:]:
            if x.mountpoint == mountpoint:
                self.partitions.remove(x)
                self.on_partition_list_change('remove', x)

    def setDVDSpeed(self, device, speed = 0):
        ioctl_flag = int(21282)
        if not device.startswith('/'):
            device = '/dev/' + device
        try:
            from fcntl import ioctl
            cd = open(device)
            ioctl(cd.fileno(), ioctl_flag, speed)
            cd.close()
        except Exception as ex:
            print '[Harddisk] Failed to set %s speed to %s' % (device, speed), ex


class UnmountTask(Task.LoggingTask):

    def __init__(self, job, hdd):
        Task.LoggingTask.__init__(self, job, _('Unmount'))
        self.hdd = hdd
        self.mountpoints = []

    def prepare(self):
        try:
            dev = self.hdd.disk_path.split('/')[-1]
            open('/dev/nomount.%s' % dev, 'wb').close()
        except Exception as e:
            print '[UnmountTask] ERROR: Failed to create /dev/nomount file:', e

        self.setTool('umount')
        self.args.append('-f')
        for dev in self.hdd.enumMountDevices():
            self.args.append(dev)
            self.postconditions.append(Task.ReturncodePostcondition())
            self.mountpoints.append(dev)

        if not self.mountpoints:
            print '[UnmountTask] No mountpoints found?'
            self.cmd = 'true'
            self.args = [self.cmd]

    def afterRun(self):
        for path in self.mountpoints:
            try:
                os.rmdir(path)
            except Exception as ex:
                print "[UnmountTask] Failed to remove path '%s':" % path, ex


class MountTask(Task.LoggingTask):

    def __init__(self, job, hdd):
        Task.LoggingTask.__init__(self, job, _('Mount'))
        self.hdd = hdd

    def prepare(self):
        try:
            dev = self.hdd.disk_path.split('/')[-1]
            os.unlink('/dev/nomount.%s' % dev)
        except Exception as e:
            print '[MountTask] ERROR: Failed to remove /dev/nomount file:', e

        if self.hdd.mount_device is None:
            dev = self.hdd.partitionPath('1')
        else:
            dev = self.hdd.mount_device
        fstab = open('/etc/fstab')
        lines = fstab.readlines()
        fstab.close()
        for line in lines:
            parts = line.strip().split(' ')
            fspath = os.path.realpath(parts[0])
            if os.path.realpath(fspath) == dev:
                self.setCmdline('mount -t auto ' + fspath)
                self.postconditions.append(Task.ReturncodePostcondition())
                return

        if self.hdd.type == DEVTYPE_UDEV:
            self.setCmdline('sleep 2; hdparm -z ' + self.hdd.disk_path)
            self.postconditions.append(Task.ReturncodePostcondition())
        return


class MkfsTask(Task.LoggingTask):

    def prepare(self):
        self.fsck_state = None
        return

    def processOutput(self, data):
        print '[MkfsTask] [Mkfs]', data
        if 'Writing inode tables:' in data:
            self.fsck_state = 'inode'
        elif 'Creating journal' in data:
            self.fsck_state = 'journal'
            self.setProgress(80)
        elif 'Writing superblocks ' in data:
            self.setProgress(95)
        elif self.fsck_state == 'inode':
            if '/' in data:
                try:
                    d = data.strip(' \x08\r\n').split('/', 1)
                    if '\x08' in d[1]:
                        d[1] = d[1].split('\x08', 1)[0]
                    self.setProgress(80 * int(d[0]) / int(d[1]))
                except Exception as e:
                    print '[MkfsTask] [Mkfs] E:', e

                return
        self.log.append(data)


harddiskmanager = HarddiskManager()

def internalHDDNotSleeping():
    if harddiskmanager.HDDCount():
        for hdd in harddiskmanager.HDDList():
            if ('pci' in hdd[1].phys_path or 'ahci' in hdd[1].phys_path) and hdd[1].max_idle_time and not hdd[1].isSleeping():
                return True

    return False


SystemInfo['ext4'] = isFileSystemSupported('ext4')