__author__ = 'Konstantin Glazyrin'

from app.plugins.plugins_common import *

from app.workers import *
import threading

# tackt - every 2 ticks (i.e. 0.2s)
TICKTACK = 10.
# shift by a one tick
TICKTACK_OFFSET = 4.


def setup(obj):
    """
    Test for the correct initialization and parameter presence
    :param obj:
    :return:
    """
    global TICKTACK, TICKTACK_OFFSET
    if not obj.test(TICKTACK):
        raise NameError
    if not obj.test(TICKTACK_OFFSET):
        raise NameError


def work():
    """
    Main work done by the plugin
    :param obj:
    :return:
    """
    id = os.path.basename(__file__)

    # process vacuum components #1
    ntask, root_ref = 1, "P022.tango.starter.eh2b."

    worker = PyTangoWorker("haspp02oh1:10000/tango/admin/haspp02eh2b", def_file=id, debug_level=logging.INFO)
    if worker.is_locked():
        worker.debug("Operation is locked")
        return

    worker.lock()

    attr_r, attr_s = "RunningServers", "StoppedServers"
    attr_run = worker.read_attribute(attr_r)
    attr_stop = worker.read_attribute(attr_s)

    # even Null is OK
    if not worker.test(attr_r):
        attr_r = []
    if not worker.test(attr_stop):
        attr_stop = []

    if worker.test(attr_run) and worker.test(attr_stop):
        runs, stops = attr_run[1], attr_stop[1]
        if not worker.test(runs):
            runs = ()
        if not worker.test(stops):
            stops = ()

        process_tango_starter(worker, runs, root_ref="{}{}".format(root_ref, attr_r))
        process_tango_starter(worker, stops, root_ref="{}{}".format(root_ref, attr_s))

        worker.debug(u"The worker ({}; thread: {}) has successfully finished the task ({})".format(id, threading.currentThread(),
                                                                                         ntask))
    else:
        worker.debug(u"Unfortunately, the worker ({}; thread: {}) has not successfully finished the task ({})".format(id,
                                                                                                                     threading.currentThread(),
                                                                                                                     ntask))
    worker.unlock()

