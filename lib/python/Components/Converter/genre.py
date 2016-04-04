# Embedded file name: /usr/lib/enigma2/python/Components/Converter/genre.py
maintype = [_('Reserved'),
 _('Movie/Drama'),
 _('News Current Affairs'),
 _('Show Games show'),
 _('Sports'),
 _('Children/Youth'),
 _('Music/Ballet/Dance'),
 _('Arts/Culture'),
 _('Social/Political/Economics'),
 _('Education/Science/...'),
 _('Leisure hobbies'),
 _('Other')]
subtype = {}
subtype[1] = [_('movie/drama (general)'),
 _('detective/thriller'),
 _('adventure/western/war'),
 _('science fiction/fantasy/horror'),
 _('comedy'),
 _('soap/melodram/folkloric'),
 _('romance'),
 _('serious/classical/religious/historical movie/drama'),
 _('adult movie/drama')]
subtype[2] = [_('news/current affairs (general)'),
 _('news/weather report'),
 _('news magazine'),
 _('documentary'),
 _('discussion/interview/debate')]
subtype[3] = [_('show/game show (general)'),
 _('game show/quiz/contest'),
 _('variety show'),
 _('talk show')]
subtype[4] = [_('sports (general)'),
 _('special events'),
 _('sports magazine'),
 _('football/soccer'),
 _('tennis/squash'),
 _('team sports'),
 _('athletics'),
 _('motor sport'),
 _('water sport'),
 _('winter sport'),
 _('equestrian'),
 _('martial sports')]
subtype[5] = [_("childrens's/youth program (general)"),
 _("pre-school children's program"),
 _('entertainment (6-14 year old)'),
 _('entertainment (10-16 year old)'),
 _('information/education/school program'),
 _('cartoon/puppets')]
subtype[6] = [_('music/ballet/dance (general)'),
 _('rock/pop'),
 _('serious music/classic music'),
 _('folk/traditional music'),
 _('jazz'),
 _('musical/opera'),
 _('ballet')]
subtype[7] = [_('arts/culture (without music, general)'),
 _('performing arts'),
 _('fine arts'),
 _('religion'),
 _('popular culture/traditional arts'),
 _('literature'),
 _('film/cinema'),
 _('experimental film/video'),
 _('broadcasting/press'),
 _('new media'),
 _('arts/culture magazine'),
 _('fashion')]
subtype[8] = [_('social/political issues/economics (general)'),
 _('magazines/reports/documentary'),
 _('economics/social advisory'),
 _('remarkable people')]
subtype[9] = [_('education/science/factual topics (general)'),
 _('nature/animals/environment'),
 _('technology/natural science'),
 _('medicine/physiology/psychology'),
 _('foreign countries/expeditions'),
 _('social/spiritual science'),
 _('further education'),
 _('languages')]
subtype[10] = [_('leisure hobbies (general)'),
 _('tourism/travel'),
 _('handicraft'),
 _('motoring'),
 _('fitness & health'),
 _('cooking'),
 _('advertisement/shopping'),
 _('gardening')]
subtype[11] = [_('original language'),
 _('black & white'),
 _('unpublished'),
 _('live broadcast')]

def getGenreStringMain(hn, ln):
    if hn == 15:
        return _('User defined')
    if 0 < hn < len(maintype):
        return maintype[hn]
    return ''


def getGenreStringSub(hn, ln):
    if hn == 15:
        return _('User defined') + ' ' + str(ln)
    if 0 < hn < len(maintype):
        if ln == 15:
            return _('User defined')
        if ln < len(subtype[hn]):
            return subtype[hn][ln]
    return ''


def getGenreStringLong(hn, ln):
    if hn == 15:
        return _('User defined') + ' ' + str(ln)
    if 0 < hn < len(maintype):
        return maintype[hn] + ': ' + getGenreStringSub(hn, ln)
    return ''