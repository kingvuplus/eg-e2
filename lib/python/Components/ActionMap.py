# Embedded file name: /usr/lib/enigma2/python/Components/ActionMap.py
from enigma import eActionMap

class ActionMap:

    def __init__(self, contexts = None, actions = None, prio = 0):
        if not actions:
            actions = {}
        if not contexts:
            contexts = []
        self.actions = actions
        self.contexts = contexts
        self.prio = prio
        self.p = eActionMap.getInstance()
        self.bound = False
        self.exec_active = False
        self.enabled = True

    def setEnabled(self, enabled):
        self.enabled = enabled
        self.checkBind()

    def doBind(self):
        if not self.bound:
            for ctx in self.contexts:
                self.p.bindAction(ctx, self.prio, self.action)

            self.bound = True

    def doUnbind(self):
        if self.bound:
            for ctx in self.contexts:
                self.p.unbindAction(ctx, self.action)

            self.bound = False

    def checkBind(self):
        if self.exec_active and self.enabled:
            self.doBind()
        else:
            self.doUnbind()

    def execBegin(self):
        self.exec_active = True
        self.checkBind()

    def execEnd(self):
        self.exec_active = False
        self.checkBind()

    def action(self, context, action):
        print ' '.join(('[ActionMap]', context, action))
        if self.actions.has_key(action):
            res = self.actions[action]()
            if res is not None:
                return res
            return 1
        else:
            print '[ActionMap] unknown action %s/%s! typo in keymap?' % (context, action)
            return 0
            return

    def destroy(self):
        pass


class NumberActionMap(ActionMap):

    def action(self, contexts, action):
        numbers = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')
        if action in numbers and self.actions.has_key(action):
            res = self.actions[action](int(action))
            if res is not None:
                return res
            return 1
        else:
            return ActionMap.action(self, contexts, action)
            return


class HelpableActionMap(ActionMap):

    def __init__(self, parent, context, actions = None, prio = 0):
        if not actions:
            actions = {}
        alist = []
        adict = {}
        for action, funchelp in actions.iteritems():
            if isinstance(funchelp, tuple):
                alist.append((action, funchelp[1]))
                adict[action] = funchelp[0]
            else:
                adict[action] = funchelp

        ActionMap.__init__(self, [context], adict, prio)
        parent.helpList.append((self, context, alist))


class HelpableNumberActionMap(ActionMap):

    def __init__(self, parent, context, actions = None, prio = 0):
        if not actions:
            actions = {}
        alist = []
        adict = {}
        for action, funchelp in actions.iteritems():
            if isinstance(funchelp, tuple):
                alist.append((action, funchelp[1]))
                adict[action] = funchelp[0]
            else:
                adict[action] = funchelp

        ActionMap.__init__(self, [context], adict, prio)
        parent.helpList.append((self, context, alist))

    def action(self, contexts, action):
        numbers = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')
        if action in numbers and self.actions.has_key(action):
            res = self.actions[action](int(action))
            if res is not None:
                return res
            return 1
        else:
            return ActionMap.action(self, contexts, action)
            return