__author__ = 'Konstantin Glazyrin'

from app.plugins.plugins_common import *

from app.common import *
import time

# tackt - every 2 ticks (i.e. 0.2s)
TICKTACK = 2.
# shift by a one tick
TICKTACK_OFFSET = 0.

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

    t = MutexLock(def_file=id, debug_level=logging.INFO)

    if t.is_locked():
        t.debug("Operation is locked")
        return
    t.lock()
    t.debug("Working with plugin ({})".format(__file__))
    time.sleep(2)
    t.unlock()