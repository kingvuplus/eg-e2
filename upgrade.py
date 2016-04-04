# Embedded file name: /usr/lib/enigma2/python/upgrade.py
import os
opkgDestinations = ['/']
opkgStatusPath = ''

def findMountPoint(path):
    path = os.path.abspath(path)
    while not os.path.ismount(path):
        path = os.path.dirname(path)

    return path


def opkgExtraDestinations():
    global opkgDestinations
    return ''.join([ ' --add-dest %s:%s' % (i, i) for i in opkgDestinations ])


def opkgAddDestination(mountpoint):
    if mountpoint not in opkgDestinations:
        opkgDestinations.append(mountpoint)
        print '[Ipkg] Added to OPKG destinations:', mountpoint


mounts = os.listdir('/media')
for mount in mounts:
    mount = os.path.join('/media', mount)
    if mount and not mount.startswith('/media/net'):
        if opkgStatusPath == '':
            opkgStatusPath = 'var/lib/opkg/status'
            if not os.path.exists(os.path.join('/', opkgStatusPath)):
                opkgStatusPath = 'usr/lib/opkg/status'
        if os.path.exists(os.path.join(mount, opkgStatusPath)):
            opkgAddDestination(mount)

os.system('opkg ' + opkgExtraDestinations() + ' upgrade 2>&1 | tee /home/root/ipkgupgrade.log && reboot')