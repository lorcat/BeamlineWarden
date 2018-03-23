#!/usr/bin/env python

__author__ = 'Konstantin Glazyrin'

"""
Reads values from the memcache server, parses them and produces a tweet
depending on the situation.
Common situations:
Petra machine is down. (working)
Petra machine is recovering.(working)
Problem with a tango server. (to be implemented)

Values are only reported if they have changed.
"""

import os
import sys

sys.path.append(os.path.dirname(__file__))

import memcache
import json
import datetime

from app import *
from app.worker_crontab import *

MEMCACHE_HOST = "haspp02raspi02:55211"

def work(debug=False):
    mc = memcache.Client([MEMCACHE_HOST])
    id = "crontab_daemon"

    key_petra = "Petra"
    value_petra = mc.get(key_petra)

    key = "P022.vacuum.interlock"
    value_vacuum = mc.get(key)

    key = "P022.tango.starter.check"
    value_servers = mc.get(key)

    key = "P022.tango.individuals.check"
    value_indservers = mc.get(key)


    worker = CrontabWorker(debug_level=logging.DEBUG, def_file=id)

    if debug:
        worker.unlock()

    worker.debug("Values obtained: \n{}\n{}\n{}".format(value_petra, value_vacuum, value_servers))

    # we do not do anything if the previos worker is running
    if worker.is_locked():
        worker.debug("Worker is locked")
        return

    # lock operation
    worker.lock()

    # we test if there is a connection to the memcache and the plugins are running
    # petra
    if value_petra is not None:
        value_petra = json.loads(value_petra)

        # process petra values
        worker.process_petra_data(value_petra)

    # vacuum
    if value_vacuum is not None:
        value_vacuum = json.loads(value_vacuum)

        # process petra values
        worker.process_vacuum(value_petra)

    # servers
    if value_servers is not None:
        value_servers = json.loads(value_servers)

        # process petra values
        worker.process_tango_servers(value_servers)

    if value_indservers is not None:
        value_indservers = json.loads(value_indservers)

        # process petra values
        worker.process_tango_individual_servers(value_indservers)

    # unlock operation
    worker.unlock()

if __name__=="__main__":
    work(debug=True)
