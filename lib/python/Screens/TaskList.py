# Embedded file name: /usr/lib/enigma2/python/Screens/TaskList.py
from enigma import eTimer
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Components.Sources.List import List
from Components.MultiContent import MultiContentEntryText
from Components.Task import job_manager

class TaskListScreen(Screen):
    skin = '\n\t\t<screen name="TaskListScreen" position="center,center" size="720,576" title="Task list" >\n\t\t\t<widget source="tasklist" render="Listbox" position="10,10" size="690,490" zPosition="7" scrollbarMode="showOnDemand">\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (5, 1), size = (675, 24), font=1, flags = RT_HALIGN_LEFT, text = 1), # name\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (5, 25), size = (150, 24), font=1, flags = RT_HALIGN_LEFT, text = 2), # state\n\t\t\t\t\t\t\tMultiContentEntryProgress(pos = (160, 25), size = (390, 20), percent = -3), # progress\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (560, 25), size = (100, 24), font=1, flags = RT_HALIGN_RIGHT, text = 4), # percentage\n\t\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 22),gFont("Regular", 18)],\n\t\t\t\t\t"itemHeight": 50\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t<ePixmap position="10,530" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_red" position="10,530" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1"/>\n\t\t</screen>'

    def __init__(self, session, tasklist):
        Screen.__init__(self, session)
        self.session = session
        self.tasklist = tasklist
        self['tasklist'] = List(self.tasklist)
        self['shortcuts'] = ActionMap(['ShortcutActions', 'WizardActions', 'MediaPlayerActions'], {'ok': self.keyOK,
         'back': self.keyCancel,
         'red': self.keyCancel}, -1)
        self['key_red'] = Button(_('Close'))
        self.onLayoutFinish.append(self.layoutFinished)
        self.onShown.append(self.setWindowTitle)
        self.onClose.append(self.__onClose)
        self.Timer = eTimer()
        self.Timer.callback.append(self.TimerFire)

    def __onClose(self):
        del self.Timer

    def layoutFinished(self):
        self.Timer.startLongTimer(2)

    def TimerFire(self):
        self.Timer.stop()
        self.rebuildTaskList()

    def rebuildTaskList(self):
        self.tasklist = []
        for job in job_manager.getPendingJobs():
            self.tasklist.append((job,
             job.name,
             job.getStatustext(),
             int(100 * job.progress / float(job.end)),
             str(100 * job.progress / float(job.end)) + '%'))

        self['tasklist'].setList(self.tasklist)
        self['tasklist'].updateList(self.tasklist)
        self.Timer.startLongTimer(2)

    def setWindowTitle(self):
        self.setTitle(_('Task list'))

    def keyOK(self):
        current = self['tasklist'].getCurrent()
        print current
        if current:
            job = current[0]
            from Screens.TaskView import JobView
            self.session.openWithCallback(self.JobViewCB, JobView, job)

    def JobViewCB(self, why):
        print 'WHY---', why

    def keyCancel(self):
        self.close()

    def keySave(self):
        self.close()