import os
import re

def read_file_aslist(fname, logger=None):
    res = []
    # check if the file exists - open it if does not
    if not os.path.exists(fname):
        fh = open(fname, "w+")
        fh.write("# put values one by on in a line\n# - symbol is used for comments\n")
        fh.close()

    # open the file - read it
    if os.path.exists(fname) and os.path.isfile(fname):
        with open(fname, "r") as f:

            lines = f.readlines()
            for line in lines:
                line = line.strip()

                if logger is not None:
                    logger.debug("Read a file ({}) with a string ({})".format(fname, line))

                patt_comment = re.compile("^[\s]*#.*")
                if len(line) > 0 and not line in res and not patt_comment.match(line):
                    if logger is not None:
                        logger.debug("Found a value ({}) in the file ({})".format(line, fname))
                    res.append(line)
    return res