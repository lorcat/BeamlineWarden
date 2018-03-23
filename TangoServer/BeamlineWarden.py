import os
import sys

sys.path.append(os.path.dirname(__file__))

from app.common import *
from app.daemon import Daemon as MainWorker

from PyTango import DeviceProxy, DevFailed, Device_4Impl, DeviceClass, DevState
from PyTango.server import Device, DeviceMeta, run, attribute, command

import threading

# main debug level
DEBUG_LEVEL = logging.INFO

class BeamlineWarden(Device):
    __metaclass__ =  DeviceMeta

    # Attributes
    TickTackPeriod = attribute(label="Server Internal tick period, s", dtype=float, fget="getbase_tick_tack")
    NumThreads = attribute(label="Thread number", dtype=int, fget="getbase_threads")

    STATE = DevState.ON
    THREAD_DEMON = None

    logger = None

    def init_device(self):
        global DEBUG_LEVEL
        self.logger = Tester(def_file="BeamlineWatchDaemon", debug_level=DEBUG_LEVEL)
        self.logger.debug("Server is stopped")

        self.set_state(DevState.ON)

        #setup a worker
        self.worker = self.get_worker()
        self.thread = None

        self.Start()

    def delete_device(self):
        self.logger.debug("Server is stopped")
        self.Stop()

    @command()
    def Start(self):
        """
        Starts the daemon processing
        """
        self.logger.debug("Starting procedure")

        th = threading.Thread(target=self.worker.start)
        th.setDaemon(True)

        # saving a reference
        self.thread = th

        th.start()

        self.set_state(DevState.RUNNING)
        return DevState.RUNNING

    @command()
    def Stop(self):
        """
        Stops the daemon processing
        """
        self.logger.debug("Stopping procedure")

        if self.th is not None:
            self.worker.stop()

        threads = threading.enumerate()

        self.logger.debug("Worker thread ({})".format(self.thread))
        self.logger.debug("Threads on stop ({})".format(threads))

        for th in threads:
            main_thread = threading.currentThread()
            if th == main_thread:
                continue
            else:
                self.logger.debug("Joining {}".format(th.getName()))
                th.join(1)

        # cleanup th
        self.thread = None

        self.set_state(DevState.ON)
        return DevState.ON

    def getbase_tick_tack(self):
        return self.worker.TICKTACK

    def getbase_threads(self):
        return len(threading.enumerate())

    def get_worker(self):
        res = None
        try:
            if not self.worker:
                raise AttributeError
            else:
                res = self.worker
        except AttributeError:
            res = MainWorker(debug_level=self.logger.debug_level)
        return res


if __name__ == "__main__":
    run([BeamlineWarden])