__author__ = 'Konstantin Glazyrin'

from app.plugins.plugins_common import *

from app.common import *
import time

# tackt - every 2 ticks (i.e. 0.2s)
TICKTACK = 10.
# shift by a one tick
TICKTACK_OFFSET = 0.
# root ref
ROOT_REF = "P022.tango.individuals.check"

def setup(obj):
    """
    Test for the correct initialization and parameter presence
    :param obj:
    :return:
    """
    global TICKTACK, TICKTACK_OFFSET, ROOT_REF
    if not obj.test(TICKTACK):
        raise NameError
    if not obj.test(TICKTACK_OFFSET):
        raise NameError
    if not obj.test(ROOT_REF):
        raise NameError

def work(unlock=False):
    """
    Main work done by the plugin
    :param obj:
    :return:
    """
    id = os.path.basename(__file__)

    global ROOT_REF
    root_key = ROOT_REF

    worker = MutexLock(def_file=id, debug_level=logging.DEBUG)

    # manual unlock
    if unlock:
        worker.debug("Manual unlock")
        worker.unlock()

    if worker.is_locked():
        worker.debug("Operation is locked")
        return

    worker.lock()

    try:

        # read data file containing the required processes - ASCII file line by line
        tmp = ["plugins_common", "requires_tango_servers_as_keys.conf"]
        server_file = os.path.join(os.path.dirname(__file__), *tmp )
        worker.debug("Using the configuration file ({})".format(server_file))

        # check if the file exists - open it if does not
        if not os.path.exists(server_file):
            fh = open(server_file, "w+")
            fh.write("# put servers one by on in a line\n# - symbol is used for comments\n")
            fh.close()
        try:
            required_keys = []
            # open the file - read it
            if os.path.exists(server_file) and os.path.isfile(server_file):
                with open(server_file, "r") as f:

                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()

                        worker.debug("Read a server file with a string ({})".format(line))

                        patt_comment = re.compile("^[\s]*#.*")
                        if len(line) > 0 and not patt_comment.match(line) and not line in required_keys:
                            worker.debug("Found a required server name ({}) file ({})".format(line, server_file))
                            required_keys.append(line)
            else:
                raise ValueError

            # data storage for the malfunctioning servers
            error_servers = []

            # process all keys from memcached - if any of them is False - report it
            for key in required_keys:
                key_val = get_key(key, worker)
                if key_val == False:
                    error_servers.append(key)

            # check if we have a new error
            bnewerr = is_new_error(root_key, error_servers, worker)
            report = {"new": bnewerr, "errors": len(error_servers), "servers": error_servers}

            worker.debug("Number of the crashed servers: ({})".format(len(error_servers)))
            worker.debug("New errors: ({})".format(bnewerr))

            # report even if there is no errors
            dict2json(root_key, report, worker)

        except ValueError:
            worker.error("Error with access to the server file ({}) or the file is empty".format(server_file))

    except Exception as e:
        worker.error("Critical error, message is:\n{}".format(e.message))

    # finish
    worker.unlock()


def is_new_error(root_key, error_servers, logger):
    """
    Gets the root, makes full key, checks the required values vs running, outputs them
    :return:
    """
    res = False
    try:
        old_values = get_key(root_key)
        logger.debug("Checking old values for the crashed servers ({})".format(old_values))
        logger.debug("Comparing new values ({})".format(error_servers))

        # if old data is absent - report the data
        if not logger.testString(old_values):
            res = True
            raise KeyError

        # if the json string is malformed - do not report an error
        try:
            old_values = json2dict(old_values)
        except ValueError:
            raise KeyError

        # we have dictionary, let's check if we have any old data
        if logger.test(old_values, dict):
            for server in error_servers:
                if server not in old_values["servers"]:
                    logger.debug("New error - server ({})".format(server))
                    res = True
                    break
                elif server in old_values["servers"]:
                    logger.debug("We found one of the old in the new ones ({})".format(server))
    except KeyError:
        pass
    return res


if __name__=="__main__":
    work(unlock=True)

#TODO: done 20170808