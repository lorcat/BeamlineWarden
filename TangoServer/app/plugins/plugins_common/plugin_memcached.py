import memcache
from config import *

def set_key(key, value, logger=None):
    """
    Sets the values for the logger
    :param key:
    :param value:
    :param logger:
    :return:
    """
    if logger is not None:
        try:
            logger.debug("Setting memcache values ({}/{}/{})".format(MEMCACHED_HOST, key, value))
        except UnicodeEncodeError:
            logger.debug(u"Setting memcache values ({}/{}/{})".format(MEMCACHED_HOST, unicode(key), unicode(value)))

    mc = memcache.Client([MEMCACHED_HOST], debug=0)
    mc.set(str(key), value)


def append_key(key, value, logger=None):
    """
    Sets the values for the logger
    :param key:
    :param value:
    :param logger:
    :return:
    """
    if logger is not None:
        try:
            logger.debug("Appending memcache values ({}/{}/{})".format(MEMCACHED_HOST, key, value))
        except UnicodeEncodeError:
            logger.debug(u"Appending memcache values ({}/{}/{})".format(MEMCACHED_HOST, unicode(key), unicode(value)))
    mc = memcache.Client([MEMCACHED_HOST], debug=0)
    mc.append(str(key), value)


def get_key(key, logger=None):
    """
    Gets the values for the logger
    :param key:
    :param value:
    :param logger:
    :return:
    """
    res = None
    if logger is not None:
        try:
            logger.debug("Getting memcache values ({}/{})".format(MEMCACHED_HOST, key))
        except UnicodeEncodeError:
            logger.debug(u"Getting memcache values ({}/{})".format(MEMCACHED_HOST, unicode(key)))

    mc = memcache.Client([MEMCACHED_HOST], debug=0)
    res = mc.get(str(key))

    if logger is not None:
        logger.debug("Value is ({})".format(res))
    return res