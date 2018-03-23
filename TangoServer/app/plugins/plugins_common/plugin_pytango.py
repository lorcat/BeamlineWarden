from plugin_memcached import set_key
from config import *

from plugin_time import *

def process_tango_starter(worker, params, root_ref=""):
    """
    processes output from the starter; servers are written into a single string
    :param worker:
    :param params:
    :return:
    """
    if params is None:
        worker.error("Invalid response from the starter device ({})".format(worker.device))
        return

    value = ""
    for (i, el) in enumerate(params):
        if i != len(params)-1:
            value += "{}%".format(el)
        else:
            value += "{}".format(el)

    key = root_ref
    set_key(key, value, logger=worker)

    # timestamp
    set_timestamp(root_ref=root_ref, logger=worker)
