__author__ = 'Konstantin Glazyrin'

from app.plugins.plugins_common import *

from app.workers import *
import threading

# tackt - every 10 ticks (i.e. 10x0.1s)
TICKTACK = 20.
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

    # process vacuum components #1
    ntask, root_ref = 1, "P022.vacuum.oh1."
    worker = HTTPWorker("/web2cToolkit/Web2c?param=(open)p3_02info.xml,0", def_file=id, host="hasyvac.desy.de",
                        port=8080, debug_level=logging.INFO)
    xml_root = worker.start()

    worker.lock()

    # link should be http://hasyvac.desy.de:8080/web2cToolkit/userdocs/greenicon.jpg for icons

    if worker.test(xml_root):
        process_xml_root(worker, xml_root, root_ref=root_ref)
        worker.debug(
            u"The worker ({}; thread: {}) has successfully finished the task ({})".format(id, threading.currentThread(),
                                                                                         ntask))
    else:
        worker.debug(u"Unfortunately, the worker ({}; thread: {}) has not successfully finished the task ({})".format(id,
                                                                                                                     threading.currentThread(),
                                                                                                                     ntask))
    worker.unlock()

