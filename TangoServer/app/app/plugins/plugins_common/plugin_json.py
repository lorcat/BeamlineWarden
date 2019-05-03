import json
from plugin_memcached import *
import time

def dict2json(key, data, logger):
    """
    Converts a dictionary to a json, adds a timestamp value
    :param data:
    :return:
    """
    data["timestamp"] = time.time()

    # old_key = "{}.old".format(key)
    # old_val = get_key(key, logger)

    # set_key(old_key, old_val, logger)

    val = json.dumps(data)
    logger.debug(val)
    set_key(key, val, logger)

def json2dict(value):
    """
    Returns new json string or None
    :param value:
    :return:
    """
    res = None
    try:
        res = json.loads(value)
    except ValueError:
        pass
    return res