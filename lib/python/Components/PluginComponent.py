# Embedded file name: /usr/lib/enigma2/python/Components/PluginComponent.py
import os
from shutil import rmtree
from bisect import insort
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS
from Tools.Import import my_import
from Tools.Profile import profile
from Plugins.Plugin import PluginDescriptor
import keymapparser

class PluginComponent:
    firstRun = True
    restartRequired = False

    def __init__(self):
        self.plugins = {}
        self.pluginList = []
        self.installedPluginList = []
        self.setPluginPrefix('Plugins.')
        self.resetWarnings()

    def setPluginPrefix(self, prefix):
        self.prefix = prefix

    def addPlugin(self, plugin):
        if self.firstRun or not plugin.needsRestart:
            self.pluginList.append(plugin)
            for x in plugin.where:
                insort(self.plugins.setdefault(x, []), plugin)
                if x == PluginDescriptor.WHERE_AUTOSTART:
                    plugin(reason=0)

        else:
            self.restartRequired = True

    def removePlugin(self, plugin):
        self.pluginList.remove(plugin)
        for x in plugin.where:
            self.plugins[x].remove(plugin)
            if x == PluginDescriptor.WHERE_AUTOSTART:
                plugin(reason=1)

    def loadBasePlugins(self, directory):
        new_plugins = []
        for c in os.listdir(directory):
            directory_category = os.path.join(directory, c)
            if not os.path.isdir(directory_category):
                continue
            for pluginname in os.listdir(directory_category):
                path = os.path.join(directory_category, pluginname)
                if pluginname.endswith('Wizard') or pluginname in ('EGAMIPluginSpeedUp', 'OpenWebif', 'WeatherPlugin', 'WeatherComponentHandler', 'EGAMIPermanentClock', 'NumberZapExt', 'CamdMenager', 'EGAMIBoot'):
                    if os.path.isdir(path):
                        profile('plugin ' + pluginname)
                        try:
                            plugin = my_import('.'.join(['Plugins',
                             c,
                             pluginname,
                             'plugin']))
                            plugins = plugin.Plugins(path=path)
                        except Exception as exc:
                            print '[PluginComponent] Plugin ', c + '/' + pluginname, 'failed to load:', exc
                            for fn in ('plugin.py', 'plugin.pyc', 'plugin.pyo'):
                                if os.path.exists(os.path.join(path, fn)):
                                    self.warnings.append((c + '/' + pluginname, str(exc)))
                                    from traceback import print_exc
                                    print_exc()
                                    break
                            else:
                                if path.find('WebInterface') == -1:
                                    print '[PluginComponent] Plugin probably removed, but not cleanly in', path
                                    print '[PluginComponent] trying to remove:', path
                                    rmtree(path)

                            continue

                        if not isinstance(plugins, list):
                            plugins = [plugins]
                        for p in plugins:
                            p.path = path
                            p.updateIcon(path)
                            new_plugins.append(p)

                        keymap = os.path.join(path, 'keymap.xml')
                        if fileExists(keymap):
                            try:
                                keymapparser.readKeymap(keymap)
                            except Exception as exc:
                                print '[PluginComponent] keymap for plugin %s/%s failed to load: ' % (c, pluginname), exc
                                self.warnings.append((c + '/' + pluginname, str(exc)))

        plugins_added = [ p for p in new_plugins if p not in self.pluginList ]
        plugins_removed = [ p for p in self.pluginList if not p.internal and p not in new_plugins ]
        for p in plugins_removed:
            for pa in plugins_added:
                if pa.path == p.path and pa.where == p.where:
                    pa.needsRestart = False

        for p in plugins_removed:
            self.removePlugin(p)

        for p in plugins_added:
            if self.firstRun or p.needsRestart is False:
                self.addPlugin(p)
            else:
                for installed_plugin in self.installedPluginList:
                    if installed_plugin.path == p.path:
                        if installed_plugin.where == p.where:
                            p.needsRestart = False

                self.addPlugin(p)

        if self.firstRun:
            self.firstRun = False
            self.installedPluginList = self.pluginList

    def readPluginList(self, directory):
        new_plugins = []
        for c in os.listdir(directory):
            directory_category = os.path.join(directory, c)
            if not os.path.isdir(directory_category):
                continue
            for pluginname in os.listdir(directory_category):
                path = os.path.join(directory_category, pluginname)
                if os.path.isdir(path):
                    profile('plugin ' + pluginname)
                    try:
                        plugin = my_import('.'.join(['Plugins',
                         c,
                         pluginname,
                         'plugin']))
                        plugins = plugin.Plugins(path=path)
                    except Exception as exc:
                        print 'Plugin ', c + '/' + pluginname, 'failed to load:', exc
                        for fn in ('plugin.py', 'plugin.pyc', 'plugin.pyo'):
                            if os.path.exists(os.path.join(path, fn)):
                                self.warnings.append((c + '/' + pluginname, str(exc)))
                                from traceback import print_exc
                                print_exc()
                                break
                        else:
                            if path.find('WebInterface') == -1:
                                print '[PluginComponent] Plugin probably removed, but not cleanly in', path
                                print '[PluginComponent] trying to remove:', path
                                rmtree(path)

                        continue

                    if not isinstance(plugins, list):
                        plugins = [plugins]
                    try:
                        for p in plugins:
                            p.path = path
                            p.updateIcon(path)
                            new_plugins.append(p)

                    except Exception as exc:
                        pass

                    keymap = os.path.join(path, 'keymap.xml')
                    if fileExists(keymap):
                        try:
                            keymapparser.readKeymap(keymap)
                        except Exception as exc:
                            print 'keymap for plugin %s/%s failed to load: ' % (c, pluginname), exc
                            self.warnings.append((c + '/' + pluginname, str(exc)))

        plugins_added = [ p for p in new_plugins if p not in self.pluginList ]
        plugins_removed = [ p for p in self.pluginList if not p.internal and p not in new_plugins ]
        for p in plugins_removed:
            for pa in plugins_added:
                if pa.path == p.path and pa.where == p.where:
                    pa.needsRestart = False

        for p in plugins_removed:
            self.removePlugin(p)

        for p in plugins_added:
            if self.firstRun or p.needsRestart is False:
                self.addPlugin(p)
            else:
                for installed_plugin in self.installedPluginList:
                    if installed_plugin.path == p.path:
                        if installed_plugin.where == p.where:
                            p.needsRestart = False

                self.addPlugin(p)

        if self.firstRun:
            self.firstRun = False
            self.installedPluginList = self.pluginList

    def getPlugins(self, where):
        if not isinstance(where, list):
            return self.plugins.get(where, [])
        res = []
        for x in where:
            for p in self.plugins.get(x, []):
                insort(res, p)

        return res

    def getPluginsForMenu(self, menuid):
        res = []
        for p in self.getPlugins(PluginDescriptor.WHERE_MENU):
            res += p(menuid)

        return res

    def clearPluginList(self):
        self.pluginList = []
        self.plugins = {}

    def reloadPlugins(self, dummy = False):
        self.clearPluginList()
        self.readPluginList(resolveFilename(SCOPE_PLUGINS))

    def shutdown(self):
        for p in self.pluginList[:]:
            self.removePlugin(p)

    def resetWarnings(self):
        self.warnings = []

    def getNextWakeupTime(self, getPluginIdent = False):
        wakeup = -1
        pident = ''
        for p in self.pluginList:
            current = p.getWakeupTime()
            if current > -1 and (wakeup > current or wakeup == -1):
                wakeup = current
                pident = str(p.name) + ' | ' + str(p.path and p.path.split('/')[-1])

        if getPluginIdent:
            return (int(wakeup), pident)
        return int(wakeup)


plugins = PluginComponent()