# Embedded file name: /usr/lib/enigma2/python/Tools/FuzzyDate.py
from time import localtime, time

def FuzzyTime(t, inPast = False):
    d = localtime(t)
    nt = time()
    n = localtime()
    dayOfWeek = (_('Mon'),
     _('Tue'),
     _('Wed'),
     _('Thu'),
     _('Fri'),
     _('Sat'),
     _('Sun'))
    if d[:3] == n[:3]:
        date = _('Today')
    elif d[0] == n[0] and d[7] == n[7] - 1 and inPast:
        date = _('Yesterday')
    elif t - nt < 604800 and nt < t and not inPast:
        date = dayOfWeek[d[6]]
    elif d[0] == n[0]:
        if inPast:
            date = '%s %02d.%02d.' % (dayOfWeek[d[6]], d[2], d[1])
        else:
            date = '%02d.%02d.' % (d[2], d[1])
    else:
        date = '%02d.%02d.%d' % (d[2], d[1], d[0])
    timeres = '%02d:%02d' % (d[3], d[4])
    return (date, timeres)


if __name__ == '__main__':

    def _(x):
        return x


    print 'now: %s %s' % FuzzyTime(time())
    for i in range(1, 14):
        print '+%2s day(s):  %s ' % (i, FuzzyTime(time() + 86400 * i))

    for i in range(1, 14):
        print '-%2s day(s):  %s ' % (i, FuzzyTime(time() - 86400 * i, True))