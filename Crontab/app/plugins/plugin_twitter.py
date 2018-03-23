import os
from TwitterAPI import TwitterAPI
from app.config import *

def twitter_imgmsg(msg, fnimage, logger):
    """
    Reports a message to the cloud
    :param msg:
    :param fnimage:
    :return:
    """
    if wrong_api_params():
        logger.error("Some access key is empty.. Aborting twitting.")
        return

    # use tweeter api
    api = TwitterAPI(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)

    image = open(fnimage, 'rb')
    data = image.read()
    r = api.request('statuses/update_with_media', {'status':msg}, {'media[]': data})

    logger.debug("Twitter has responded with ({})".format(r.status_code))
    image.close()

    # cleaning the image file
    if os.path.exists(fnimage):
        logger.debug("Removing the image ({})".format(fnimage))
        os.remove(fnimage)


def wrong_api_params():
    res = False
    global CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET
    tmp = [CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET]
    for arg in tmp:
        if len(arg) == 0:
            res = True
            break
    return res


# @TODO: make sure we can connect to tweeter
# @TODO: update the plugin to read twitter secret values from a local file - use configparser