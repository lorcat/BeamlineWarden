__author__ = 'Konstantin Glazyrin'

import os
import time
from functools import partial
from pluginbase import PluginBase
from app.common import *

import threading

import app.config as config

here = os.path.abspath(os.path.dirname(__file__))
get_path = partial(os.path.join, here)

plugin_base = PluginBase(package='app.daemon',
                         searchpath=[get_path('./plugins')])

class Daemon(Tester):
    ID = "daemon"

    TICKTACK = config.DAEMON_TIME_TICK
    MAX_COUNTER = 10000.
    DIVIDER = config.DAEMON_TIME_DIVIDER

    BREAK = False

    def __init__(self, debug_level=None):
        Tester.__init__(self, def_file=self.ID, debug_level=debug_level)

        global plugin_base
        self.plugin_base = plugin_base.make_plugin_source(
            identifier=self.ID,
            searchpath=[get_path('./plugins')])

        self.plugins = []

        for plugin_name in self.plugin_base.list_plugins():
            self.debug("Found a plugin with name ({})".format(plugin_name))

            plugin = self.plugin_base.load_plugin(plugin_name)
            try:
                # simple test of the plugin validity
                plugin.setup(self)

                self.debug("Plugin ({}) is valid, adding it".format(plugin_name))
                self.plugins.append(plugin)
                self.debug("Plugin ({}) has a tact of ({})".format(plugin_name, plugin.TICKTACK))

                # test plugin tact
                if plugin.TICKTACK < self.TICKTACK:
                    self.error("Plugin ({}) has low TICKTACK value ({}), matching it with default ({})".format(plugin_name, plugin.TICKTACK, self.TICKTACK))
                    plugin.TICKTACK = self.TICKTACK
            except (NameError, AttributeError):
                self.error("Plugin ({}) is invalid".format(plugin_name))

        # internal counter
        self.counter = 1
        self.remove_locks()

    def start(self):
        """
        Main procedure - performs a while loop with tact matching
        :return:
        """
        self.BREAK = False
        while not self.BREAK:
            if len(self.plugins) == 0:
                self.error("No plugins found, exiting")
                break

            for plugin in self.plugins:
                tact = int(plugin.TICKTACK)
                # base_tact = int(self.counter * self.TICKTACK * self.MULTIPLIER) + plugin.TICKTACK_OFFSET
                base_tact = int(self.counter) - plugin.TICKTACK_OFFSET

                # start new thread if a proper tact has come
                if not base_tact % tact:
                    self.debug("Running a plugin ({}); main tact ({}) plugin tact ({}); time ({})".format(plugin, base_tact, tact, time.time()))
                    self.start_thread(plugin)

                # start new thread if a proper tact has come
                if base_tact > 0 and not base_tact % tact:
                    self.debug("Firing a tact ({}:{}:{})".format(self.counter, self.TICKTACK,
                                                                 self.counter * self.TICKTACK))
                    self.debug("Running a plugin ({}); main tact ({}) plugin tact ({}); time ({})".format(plugin, base_tact, tact, time.time()))
                    self.start_thread(plugin)

            # sleep for a tact
            sleep_time = float(self.TICKTACK) / float(self.DIVIDER)
            self.debug("Sleeping a tact ({}:{}:{})".format(self.counter, self.TICKTACK, self.counter*self.TICKTACK))
            time.sleep(sleep_time)
            self.counter = self.counter + 1

            # reset counter in order to avoid overflow
            if self.counter == self.MAX_COUNTER:
                if not self.MAX_COUNTER % 2:
                    self.counter = 2
                else:
                    self.counter = 1

    def start_thread(self, plugin):
        """
        Start a thread with a specific plugin
        :param plugin:
        :return:
        """
        self.debug("Starting a plugin thread ({})".format(plugin))
        th = threading.Thread(target=plugin.work)
        th.start()

    def remove_locks(self):
        """
        Removes old lock files on the startup
        :return:
        """
        m = MutexLock(def_file="lock_remover")
        m.unlock_all()

    def stop(self):
        """
        Sets the parameter and quits the thread
        :return:
        """
        self.debug("Received an exit message, quiting")
        self.BREAK = True
        time.sleep(0.1)