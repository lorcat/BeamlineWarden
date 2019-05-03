__author__ = 'Konstantin Glazyrin'

from app.plugins.plugins_common import *

from app.workers import *
import threading

# tackt=2- in units of 2 base ticks (i.e. 0.2s for daemon basetick = 0.1s)
TICKTACK = 10.
# an offset shift by a some ticks
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


def work(debug=False):
    """
    Main work done by the plugin
    :param obj:
    :return:
    """
    id = os.path.basename(__file__)

    # process vacuum components #1
    root_ref = "Petra"

    worker = PyTangoWorker("haspp02oh1:10000/petra/globals/keyword", def_file=id, debug_level=logging.DEBUG)

    # unlock for stand along run
    if debug == True:
        worker.unlock()

    # check lock
    if worker.is_locked():
        worker.debug("Operation is locked")

        return

    # lock
    worker.lock()

    attrs = ["BeamCurrent",
            "BeamLifetime",
            "BeamPerm",
            "Energy",
            "FastOrbitFBStatus",
            "MachineStateText",
            "MessageText",
            "NumberOfBunches",
            "TopUpStatusText"]

    # get all values - in sequence
    data = {}
    values = worker.read_attributes(attrs)


    worker.debug("attr. values {}".format(values))

    bfailed = False
    if not worker.test(values):
        bfailed = True

    for (i, attr) in enumerate(attrs):
        if not bfailed:
            value = values[i]
            if attr.lower() == "state":
                value = str(value)
            data[attr] = value
        else:
            data[attr] = 0

    # worker.debug("dict. values {}".format(data))

    # convert dict to json string, save the key
    dict2json(root_ref, data, worker)

    # unlock
    worker.unlock()

if __name__=="__main__":
    work(debug=True)