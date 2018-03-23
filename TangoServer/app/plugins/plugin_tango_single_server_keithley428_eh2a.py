__author__ = 'Konstantin Glazyrin'

from app.plugins.plugins_common import *

from app.workers import *
import threading

# tackt=2- in units of 2 base ticks (i.e. 0.2s for daemon basetick = 0.1s)
TICKTACK = 50.
# an offset shift by a some ticks
TICKTACK_OFFSET = 10.
# root ref
ROOT_REF = "P022.EH2.Tango.Keithley428.eh2a.state"
# PyTango Device
DEV_NAME = "haspp02oh1:10000/p02/keithley428/eh2a.01"
# More settings
TANGO_ATTR = "Gain"

def setup(obj):
    """
    Test for the correct initialization and parameter presence
    :param obj:
    :return:
    """
    global TICKTACK, TICKTACK_OFFSET, TANGO_ATTR, DEV_NAME, ROOT_REF
    if not obj.test(TICKTACK):
        raise NameError
    if not obj.test(TICKTACK_OFFSET):
        raise NameError
    if not obj.test(TANGO_ATTR):
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
    global ROOT_REF, TANGO_ATTR, DEV_NAME
    id = os.path.basename(__file__)

    # process vacuum components #1
    root_ref = ROOT_REF

    tango_server, attr_test = DEV_NAME, TANGO_ATTR
    worker = PyTangoWorker(tango_server, def_file=id, debug_level=logging.DEBUG)

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
        # make test
        btango_state = worker.make_test(attr=attr_test)

        worker.debug("TangoServer ({}) has an operational state ({})".format(tango_server, btango_state))

        # convert dict to json string, save the key
        set_key(root_ref, btango_state, worker)

    except Exception as e:
        worker.error("Critical error, message is:\n{}".format(e.message))

    # unlock
    worker.unlock()

if __name__ == "__main__":
    work(unlock=True)

# @TODO: done 20170808