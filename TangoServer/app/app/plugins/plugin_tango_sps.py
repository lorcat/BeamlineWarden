__author__ = 'Konstantin Glazyrin'

from app.plugins.plugins_common import *

from app.workers import *
import threading

# tackt=2- in units of 2 base ticks (i.e. 0.2s for daemon basetick = 0.1s)
TICKTACK = 50.
# an offset shift by a some ticks
TICKTACK_OFFSET = 1.
# root ref
ROOT_REF = "P022.sps"
# PyTango Device
DEV_NAME = "tango://haspp02oh1:10000/p02/spseh2/eh2a.01"

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
    root_ref = ROOT_REF

    worker = PyTangoWorker(DEV_NAME, def_file=id, debug_level=logging.DEBUG)

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

        attrs = ['GPValve1',
                'GPValve2',
                'GPValve3',
                'GPValve4',
                'GPValve5',
                'GPValve6',
                'GPValve7',
                'GPValve8',
                'LHValve1',
                'LHValve10',
                'LHValve11',
                'LHValve12',
                'LHValve13',
                'LHValve14',
                'LHValve15',
                'LHValve16',
                'LHValve17',
                'LHValve18',
                'LHValve19',
                'LHValve2',
                'LHValve20',
                'LHValve3',
                'LHValve4',
                'LHValve5',
                'LHValve6',
                'LHValve7',
                'LHValve8',
                'LHValve9']

        # get all values - in sequence
        data = {}
        values = worker.read_attributes(attrs)

        bfailed = False
        if (not worker.test(values)) or len(values) == 0 or (None in values):
            worker.debug("There is an error with a device - we can only set default values")
            bfailed = True

        for (i, attr) in enumerate(attrs):
            if not bfailed:
                value = values[i]
                if attr.lower() == "state":
                    value = str(value)
                data[attr] = value
            else:
                data[attr] = None

        # worker.debug("dict. values {}".format(data))

        # convert dict to json string, save the key
        dict2json(root_ref, data, worker)
    except Exception as e:
        worker.error("Critical error, message is:\n{}".format(e.message))

    # unlock
    worker.unlock()

if __name__=="__main__":
    work()

#@TODO: done 20170808