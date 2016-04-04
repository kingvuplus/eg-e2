# Embedded file name: /usr/lib/enigma2/python/Tools/BugHunting.py
import sys
import inspect

def getFrames(deep = 2):
    if deep is None or deep == 0:
        deep = 1
    frames = []
    for x in range(2, 3 + deep):
        try:
            frames.append(sys._getframe(x))
        except:
            break

    return frames


def printCallSequence(deep = 1):
    if deep is None or deep == 0:
        deep = 1
    frames = getFrames(abs(deep))
    print '\x1b[36m%s:%s' % (frames[0].f_code.co_filename, frames[0].f_code.co_firstlineno),
    if deep >= 0:
        for x in range(0, len(frames)):
            if not x:
                print '\x1b[96m%s' % frames[x].f_code.co_name,
            else:
                print '\x1b[94m<-- \x1b[95m%s(%s:%s)' % (frames[x].f_code.co_name, frames[x].f_code.co_filename.split('/')[-1], frames[x].f_lineno),

    else:
        for x in range(len(frames) - 1, -1, -1):
            if not x:
                print '\x1b[96m%s' % frames[x].f_code.co_name,
            else:
                print '\x1b[95m%s(%s:%s) \x1b[94m-->' % (frames[x].f_code.co_name, frames[x].f_code.co_filename.split('/')[-1], frames[x].f_lineno),

    print '\x1b[0m'
    del frames
    return


def printCallSequenceRawData(deep = 1):
    if deep is None or deep == 0:
        deep = 1
    deep = abs(deep)
    frames = getFrames(deep)
    print '\x1b[36m%s:%s' % (frames[0].f_code.co_filename, frames[0].f_code.co_firstlineno),
    for x in range(0, len(frames)):
        if not x:
            print '\x1b[96m%s \x1b[33m%s' % (frames[x].f_code.co_name, inspect.getargvalues(frames[x]))
        else:
            print '\x1b[94m<-- \x1b[95m%s(%s:%s)\x1b[33m%s' % (frames[x].f_code.co_name,
             frames[x].f_code.co_filename.split('/')[-1],
             frames[x].f_lineno,
             inspect.getargvalues(frames[x]))

    print '\x1b[0m',
    del frames
    return