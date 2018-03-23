import sys
import re
from app.common import Tester
from app.daemon import Daemon as MainWorker
import logging

DEBUG_LEVEL = logging.INFO

def usage():
    print("""{} [--help] [--debug=DEBUG|INFO]
    DEBUG - debug level used for the program
            Please be aware that each plugin has its own debug level
    """.format(__file__))

def prep_sysargs():
    """
    Converts the program arguments into the script parameters
    :return:
    """
    global DEBUG_LEVEL
    if len(sys.argv) > 0:
        try:
            if "--help" in sys.argv or "-h" in sys.argv:
                raise ValueError

            t = Tester(def_file="parsing", debug_level=logging.DEBUG)
            for arg in sys.argv:
                pdebug = re.compile("--debug=(.*)")

                mdebug = pdebug.search(arg)
                if mdebug:
                    tlevel = mdebug.group(1)
                    if "info" in tlevel.lower():
                        DEBUG_LEVEL = logging.INFO
                    else:
                        DEBUG_LEVEL = logging.DEBUG
                    t.debug("Debug level is changed to ({})".format(DEBUG_LEVEL))

        except ValueError:
            usage()

def main():
    global DEBUG_LEVEL
    prep_sysargs()

    w = MainWorker(debug_level=DEBUG_LEVEL)
    w.start()

if __name__=="__main__":
    main()


#@TODO: make it as a TangoServer or as a daemon
