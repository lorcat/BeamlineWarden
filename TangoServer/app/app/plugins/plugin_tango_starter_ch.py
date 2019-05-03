__author__ = 'Konstantin Glazyrin'

from app.plugins.plugins_common import *

from app.workers import *
import threading

# tackt - every 2 ticks (i.e. 0.2s)
TICKTACK = 10.
# shift by a one tick
TICKTACK_OFFSET = 6.
# root ref
ROOT_REF = "P022.tango.starter.perk01."
# PyTango Device
DEV_NAME = "haspp02oh1:10000/tango/admin/haspp022perk01"


def setup(obj):
    """
    Test for the correct initialization and parameter presence
    :param obj:
    :return:
    """
    global TICKTACK, TICKTACK_OFFSET, DEV_NAME, ROOT_REF
    if not obj.test(TICKTACK):
        raise NameError
    if not obj.test(TICKTACK_OFFSET):
        raise NameError
    if not obj.test(DEV_NAME):
        raise NameError
    if not obj.test(ROOT_REF):
        raise NameError

def work(unlock=False):
    """
    Main work done by the plugin
    :param obj:
    :return:
    """
    global ROOT_REF, DEV_NAME
    id = os.path.basename(__file__)

    # process vacuum components #1
    ntask, root_ref = 1, ROOT_REF

    worker = PyTangoWorker(DEV_NAME, def_file=id, debug_level=logging.INFO)

    # manual unlock
    if unlock:
        worker.debug("Manual unlock")
        worker.unlock()

    # check lock
    if worker.is_locked():
        worker.debug("Operation is locked")
        return

    # lock
    worker.lock()

    try:
        attr_r, attr_s = "RunningServers", "StoppedServers"

        attr_run = worker.read_attribute(attr_r)
        attr_stop = worker.read_attribute(attr_s)

        # even None is OK - means empty list
        if not worker.test(attr_run):
            attr_run = [None, []]
        if not worker.test(attr_stop):
            attr_stop = [None, []]

        # we set values if both of them are set - in any case
        if worker.test(attr_run) and worker.test(attr_stop):
            runs, stops = attr_run[1], attr_stop[1]

            if not worker.test(runs):
                runs = ()
            if not worker.test(stops):
                stops = ()

            process_tango_starter(worker, runs, root_ref="{}{}".format(root_ref, attr_r))
            process_tango_starter(worker, stops, root_ref="{}{}".format(root_ref, attr_s))

            worker.debug(u"The worker ({}; thread: {}) has successfully finished the task ({})".format(id,
                                                                                                       threading.currentThread(),
                                                                                                       ntask))
        else:
            worker.debug(
                u"Unfortunately, the worker ({}; thread: {}) has not successfully finished the task ({})".format(id,
                                                                                                                 threading.currentThread(),
                                                                                                                 ntask))
    except Exception as e:
        worker.error("Critical error, message is:\n{}".format(e.message))

    # unlock
    worker.unlock()


if __name__ == "__main__":
    work(unlock=True)

#@TODO: done 20170808