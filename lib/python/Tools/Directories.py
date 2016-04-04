# Embedded file name: /usr/lib/enigma2/python/Tools/Directories.py
import os
import re
from stat import S_IMODE
from enigma import eEnv
SCOPE_TRANSPONDERDATA = 0
SCOPE_SYSETC = 1
SCOPE_FONTS = 2
SCOPE_SKIN = 3
SCOPE_SKIN_IMAGE = 4
SCOPE_USERETC = 5
SCOPE_CONFIG = 6
SCOPE_LANGUAGE = 7
SCOPE_HDD = 8
SCOPE_PLUGINS = 9
SCOPE_MEDIA = 10
SCOPE_PLAYLIST = 11
SCOPE_CURRENT_SKIN = 12
SCOPE_METADIR = 16
SCOPE_CURRENT_PLUGIN = 17
SCOPE_TIMESHIFT = 18
SCOPE_ACTIVE_SKIN = 19
SCOPE_LCDSKIN = 20
SCOPE_ACTIVE_LCDSKIN = 21
SCOPE_AUTORECORD = 22
PATH_CREATE = 0
PATH_DONTCREATE = 1
defaultPaths = {SCOPE_TRANSPONDERDATA: (eEnv.resolve('${sysconfdir}/'), PATH_DONTCREATE),
 SCOPE_SYSETC: (eEnv.resolve('${sysconfdir}/'), PATH_DONTCREATE),
 SCOPE_FONTS: (eEnv.resolve('${datadir}/fonts/'), PATH_DONTCREATE),
 SCOPE_CONFIG: (eEnv.resolve('${sysconfdir}/enigma2/'), PATH_CREATE),
 SCOPE_PLUGINS: (eEnv.resolve('${libdir}/enigma2/python/Plugins/'), PATH_CREATE),
 SCOPE_LANGUAGE: (eEnv.resolve('${datadir}/enigma2/po/'), PATH_DONTCREATE),
 SCOPE_SKIN: (eEnv.resolve('${datadir}/enigma2/'), PATH_DONTCREATE),
 SCOPE_LCDSKIN: (eEnv.resolve('${datadir}/enigma2/display/'), PATH_DONTCREATE),
 SCOPE_SKIN_IMAGE: (eEnv.resolve('${datadir}/enigma2/'), PATH_DONTCREATE),
 SCOPE_HDD: ('/media/hdd/movie/', PATH_DONTCREATE),
 SCOPE_TIMESHIFT: ('/media/hdd/timeshift/', PATH_DONTCREATE),
 SCOPE_AUTORECORD: ('/media/hdd/movie/', PATH_DONTCREATE),
 SCOPE_MEDIA: ('/media/', PATH_DONTCREATE),
 SCOPE_PLAYLIST: (eEnv.resolve('${sysconfdir}/enigma2/playlist/'), PATH_CREATE),
 SCOPE_USERETC: ('', PATH_DONTCREATE),
 SCOPE_METADIR: (eEnv.resolve('${datadir}/meta'), PATH_CREATE)}

def resolveFilename(scope, base = '', path_prefix = None):
    if base.startswith('~/'):
        base = os.path.join(path_prefix, base[2:])
    if base.startswith('/'):
        return base
    else:
        if scope == SCOPE_CURRENT_SKIN:
            from Components.config import config
            tmp = defaultPaths[SCOPE_CONFIG][0]
            if base and pathExists(tmp + base):
                path = tmp
            else:
                tmp = defaultPaths[SCOPE_SKIN][0]
                pos = config.skin.primary_skin.value.rfind('/')
                if pos != -1:
                    tmpfile = tmp + config.skin.primary_skin.value[:pos + 1] + base
                    if pathExists(tmpfile):
                        path = tmp + config.skin.primary_skin.value[:pos + 1]
                    else:
                        path = tmp
                else:
                    path = tmp
        elif scope == SCOPE_ACTIVE_SKIN:
            from Components.config import config
            tmp = defaultPaths[SCOPE_CONFIG][0]
            if base and pathExists(tmp + base):
                path = tmp
            elif base and pathExists(defaultPaths[SCOPE_SKIN][0] + base):
                path = defaultPaths[SCOPE_SKIN][0]
            else:
                tmp = defaultPaths[SCOPE_SKIN][0]
                pos = config.skin.primary_skin.value.rfind('/')
                if pos != -1:
                    tmpfile = tmp + config.skin.primary_skin.value[:pos + 1] + base
                    if pathExists(tmpfile) or ':' in tmpfile and pathExists(tmpfile.split(':')[0]):
                        path = tmp + config.skin.primary_skin.value[:pos + 1]
                    elif pathExists(tmp + base) or ':' in base and pathExists(tmp + base.split(':')[0]):
                        path = tmp
                    elif 'skin_default' not in tmp:
                        path = tmp + 'skin_default/'
                    else:
                        path = tmp
                elif pathExists(tmp + base):
                    path = tmp
                elif 'skin_default' not in tmp:
                    path = tmp + 'skin_default/'
                else:
                    path = tmp
        elif scope == SCOPE_ACTIVE_LCDSKIN:
            from Components.config import config
            tmp = defaultPaths[SCOPE_CONFIG][0]
            if base and pathExists(tmp + base):
                path = tmp
            elif base and pathExists(defaultPaths[SCOPE_LCDSKIN][0] + base):
                path = defaultPaths[SCOPE_LCDSKIN][0]
            else:
                tmp = defaultPaths[SCOPE_LCDSKIN][0]
                pos = config.skin.display_skin.value.rfind('/')
                if pos != -1:
                    tmpfile = tmp + config.skin.display_skin.value[:pos + 1] + base
                    if pathExists(tmpfile):
                        path = tmp + config.skin.display_skin.value[:pos + 1]
                    elif 'skin_default' not in tmp:
                        path = tmp + 'skin_default/'
                    else:
                        path = tmp
                elif 'skin_default' not in tmp:
                    path = tmp + 'skin_default/'
                else:
                    path = tmp
        elif scope == SCOPE_CURRENT_PLUGIN:
            tmp = defaultPaths[SCOPE_PLUGINS]
            from Components.config import config
            skintmp = defaultPaths[SCOPE_SKIN]
            pos = config.skin.primary_skin.value.rfind('/')
            if pos != -1:
                skintmpfile = skintmp[0] + config.skin.primary_skin.value[:pos + 1] + base
                if fileExists(skintmpfile):
                    path = skintmp[0] + config.skin.primary_skin.value[:pos + 1]
                else:
                    path = tmp[0]
            else:
                path = tmp[0]
        else:
            tmp = defaultPaths[scope]
            path = tmp[0]
        flags = tmp[1]
        if flags == PATH_CREATE:
            if not pathExists(path):
                try:
                    os.mkdir(path)
                except OSError:
                    print "resolveFilename: Couldn't create %s" % path
                    return None

        return path + base


pathExists = os.path.exists
isMount = os.path.ismount

def defaultRecordingLocation(candidate = None):
    if candidate and os.path.exists(candidate):
        return candidate
    try:
        path = os.readlink('/hdd')
    except:
        path = '/media/hdd'

    if not os.path.exists(path):
        path = ''
        from Components import Harddisk
        mounts = [ m for m in Harddisk.getProcMounts() if m[1].startswith('/media/') ]
        biggest = 0
        havelocal = False
        for candidate in mounts:
            try:
                islocal = candidate[1].startswith('/dev/')
                stat = os.statvfs(candidate[1])
                size = (stat.f_blocks + stat.f_bavail) * stat.f_bsize
                if islocal and not havelocal or islocal or not havelocal and size > biggest:
                    path = candidate[1]
                    havelocal = islocal
                    biggest = size
            except Exception as e:
                print '[DRL]', e

    if path:
        movie = os.path.join(path, 'movie')
        if os.path.isdir(movie):
            path = movie
        if not path.endswith('/'):
            path += '/'
    return path


def createDir(path, makeParents = False):
    try:
        if makeParents:
            os.makedirs(path)
        else:
            os.mkdir(path)
    except:
        return 0

    return 1


def removeDir(path):
    try:
        os.rmdir(path)
    except:
        return 0

    return 1


def fileExists(f, mode = 'r'):
    if mode == 'r':
        acc_mode = os.R_OK
    elif mode == 'w':
        acc_mode = os.W_OK
    else:
        acc_mode = os.F_OK
    return os.access(f, acc_mode)


def fileCheck(f, mode = 'r'):
    return fileExists(f, mode) and f


def getRecordingFilename(basename, dirname = None):
    non_allowed_characters = '/.\\:*?<>|"'
    filename = ''
    basename = basename.replace('\xc2\x86', '').replace('\xc2\x87', '')
    for c in basename:
        if c in non_allowed_characters or ord(c) < 32:
            c = '_'
        filename += c

    filename = filename[:247]
    if dirname is not None:
        if not dirname.startswith('/'):
            from Components.config import config
            dirname = os.path.join(defaultRecordingLocation(config.usage.default_path.value), dirname)
    else:
        from Components.config import config
        dirname = defaultRecordingLocation(config.usage.default_path.value)
    filename = os.path.join(dirname, filename)
    i = 0
    while True:
        path = filename
        if i > 0:
            path += '_%03d' % i
        try:
            open(path + '.ts')
            i += 1
        except IOError:
            return path

    return


def InitFallbackFiles():
    resolveFilename(SCOPE_CONFIG, 'userbouquet.favourites.tv')
    resolveFilename(SCOPE_CONFIG, 'bouquets.tv')
    resolveFilename(SCOPE_CONFIG, 'userbouquet.favourites.radio')
    resolveFilename(SCOPE_CONFIG, 'bouquets.radio')


def crawlDirectory(directory, pattern):
    list = []
    if directory:
        expression = re.compile(pattern)
        for root, dirs, files in os.walk(directory):
            for file in files:
                if expression.match(file) is not None:
                    list.append((root, file))

    return list


def copyfile(src, dst):
    try:
        f1 = open(src, 'rb')
        if os.path.isdir(dst):
            dst = os.path.join(dst, os.path.basename(src))
        f2 = open(dst, 'w+b')
        while True:
            buf = f1.read(16384)
            if not buf:
                break
            f2.write(buf)

        st = os.stat(src)
        mode = S_IMODE(st.st_mode)
        os.chmod(dst, mode)
        os.utime(dst, (st.st_atime, st.st_mtime))
    except:
        print 'copy', src, 'to', dst, 'failed!'
        return -1

    return 0


def copytree(src, dst, symlinks = False):
    names = os.listdir(src)
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
        if not os.path.isdir(dst):
            os.mkdir(dst)
    else:
        os.makedirs(dst)
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks)
            else:
                copyfile(srcname, dstname)
        except:
            print 'dont copy srcname (no file or link or folder)'

    try:
        st = os.stat(src)
        mode = S_IMODE(st.st_mode)
        os.chmod(dst, mode)
        os.utime(dst, (st.st_atime, st.st_mtime))
    except:
        print 'copy stats for', src, 'failed!'


def moveFiles(fileList):
    movedList = []
    try:
        try:
            for item in fileList:
                os.rename(item[0], item[1])
                movedList.append(item)

        except OSError as e:
            if e.errno == 18:
                print '[Directories] cannot rename across devices, trying slow move'
                import Tools.CopyFiles
                Tools.CopyFiles.moveFiles(fileList, item[0])
                print '[Directories] Moving in background...'
            else:
                raise

    except Exception as e:
        print '[Directories] Failed move:', e
        for item in movedList:
            try:
                os.rename(item[1], item[0])
            except:
                print '[Directories] Failed to undo move:', item
                raise


def getSize(path, pattern = '.*'):
    path_size = 0
    if os.path.isdir(path):
        files = crawlDirectory(path, pattern)
        for file in files:
            filepath = os.path.join(file[0], file[1])
            path_size += os.path.getsize(filepath)

    elif os.path.isfile(path):
        path_size = os.path.getsize(path)
    return path_size


def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"