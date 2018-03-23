import os

import json
from config import *
from plugin_file import *

def notify_email(subj, message, json, logger=None):
    """
    Reads a list with emails - sends emails to other people
    :param subj:
    :param message:
    :param json:
    :return:
    """

    fname = os.path.join(os.path.dirname(__file__), "config_emails.conf")
    elist = read_file_aslist(fname, logger)

    if logger is not None:
        logger.debug("""
Subject: {}
Message: {}
Json: {}
Emails: {}
        """.format(subj, message, json, elist))

#@TODO: actual email reporting
