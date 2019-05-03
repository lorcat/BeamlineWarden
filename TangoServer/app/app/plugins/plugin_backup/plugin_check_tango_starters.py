__author__ = 'Konstantin Glazyrin'

from app.plugins.plugins_common import *

from app.common import *
import time

# tackt - every 2 ticks (i.e. 0.2s)
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

    root_key = "P022.tango.starter.check"

    worker = MutexLock(def_file=id, debug_level=logging.INFO)

    if worker.is_locked():
        worker.debug("Operation is locked")
        return

    worker.lock()

    # read data file containing the required processes - ASCII file line by line
    tmp = ["plugins_common", "requires_tango_servers.conf"]
    server_file = os.path.join(os.path.dirname(__file__), *tmp )
    worker.debug("Using the configuration file ({})".format(server_file))

    # check if the file exists - open it if does not
    if not os.path.exists(server_file):
        fh = open(server_file, "w+")
        fh.write("# put servers one by on in a line\n# - symbol is used for comments\n")
        fh.close()

    try:
        required = []
        # open the file - read it
        if os.path.exists(server_file) and os.path.isfile(server_file):
            with open(server_file, "r") as f:

                lines = f.readlines()
                for line in lines:
                    line = line.strip()

                    worker.debug("Read a server file with a string ({})".format(line))

                    patt_comment = re.compile("^[\s]*#.*")
                    if len(line) > 0 and not patt_comment.match(line) and not line in required:
                        worker.debug("Found a required server name ({}) file ({})".format(line, server_file))
                        required.append(line)
        else:
            raise ValueError


        # data storage for the malfunctioning servers
        error_proc = []
        running = []

        # check servers one by one
            # Starter OH
        root = "P022.tango.starter.oh1."
        attr_r = "RunningServers"
        running += get_running(root, attr_r, worker)

        root = "P022.tango.starter.eh2a."
        running += get_running(root, attr_r, worker)

        root = "P022.tango.starter.eh2b."
        running += get_running(root, attr_r, worker)

        error_proc = get_errors(running, required, worker)

        # process the errors
        process_errors(root_key, error_proc, worker)
    except ValueError:
        worker.error("Error with access to the server file ({}) or the file is empty".format(server_file))

    # finish
    worker.unlock()

def get_running(root, attr, logger):
    """
    Obtains values for the running services, converts to the list
    :param key:
    :return:
    """
    res = []

    data = get_key("{}{}".format(root, attr), logger)

    # data is available
    if logger.test(data):

        p = re.compile("[^%]+")
        m = p.findall(data)
        if logger.test(m):
            res = m
            logger.debug("Reading: obtained Running Keys: ({})".format(res))
    return res

def get_errors(data, required, logger):
    """
    Gets the root, makes full key, checks the required values vs running, outputs them
    :return:
    """
    res = []
    if len(data) > 0 and len(required)>0:
        for req_el in required:
            if not req_el in data:
                res.append(req_el)
                logger.error("Server ({}) is offline".format(req_el))
    return res

def process_errors(key, errors, logger):
    """
    Reads the error array, creates an new JSON entry, compares with previous value
    :param errors:
    :return:
    """
    oldv = get_key(key, logger)

    if oldv is None:
        oldv = ""

    new_errs = []

    bnew = False
    for err in errors:
        if err not in oldv:
            bnew = True
            new_errs.append(err)

    tmp_errors = {"servers": copy.deepcopy(errors), "new": bnew, "errors": len(errors)}
    output = json.dumps(tmp_errors)

    logger.debug("Dumping a JSON string({}) to a key ({})".format(output, key))

    set_key(key, output)

    if not bnew:
        notify_email("P02.2 error (TangoServer/s crashed)",
                     "Here is the list of the newly crashed tango servers: ({})".format(new_errs), output)


