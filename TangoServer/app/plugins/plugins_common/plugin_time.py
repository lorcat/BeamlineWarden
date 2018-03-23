import re
import time
from plugin_memcached import set_key


def set_timestamp(root_ref="", logger=None):
    """
    returns a tuple with key, value
    :param root_ref:
    :return:
    """
    # avoid unnecessary dot
    patt = re.compile("(.*)\.$")
    match = patt.match(root_ref)
    if match is not None:
        root_ref = match.groups()[0]

    key, value = u"{}.timestamp".format(root_ref), time.time()

    if logger is not None:
        logger.debug("Timestamp ({}/{})".format(key, value))

    set_key(key, value, logger=logger)
