__author__ = 'Konstantin Glazyrin'

import os
import time
import glob
import logging

# Logger class
class Logger(object):
    DEFAULTLEVEL = logging.DEBUG

    DEFAULTFILE = "{}{}".format(os.path.basename(__file__), ".log")

    DEBUG_LEVELS = "INFO: {}; WARNING: {}; DEBUG: {}".format(logging.INFO, logging.WARNING, logging.DEBUG)

    def __init__(self, def_file = None, debug_level = None):
        if debug_level is not None:
            self.DEFAULTLEVEL = debug_level

        logging.basicConfig(level=self.DEFAULTLEVEL,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filemode='w')

        if def_file is None:
            self._logger = logging.getLogger("{}/{}".format(__file__, self.__class__.__name__))
        else:
            self._logger = logging.getLogger("{}/{}/{}".format(__file__, self.__class__.__name__, str(def_file)))

        self._fh = None

        self.debug_level = self.DEFAULTLEVEL
        self.setDebugLevel(self.debug_level)


        try:
            if def_file is not None:
                self.DEFAULTFILE = "{}.log".format(def_file)

            if self.DEFAULTFILE is not None and len(self.DEFAULTFILE)>0 :

                # creating a log file
                temp = ["log", self.DEFAULTFILE]
                self.DEFAULTFILE = os.path.join(os.path.dirname(__file__), *temp)

                self.DEFAULTFILE = self.DEFAULTFILE.replace(".pyc", "")
                self.DEFAULTFILE = self.DEFAULTFILE.replace(".py", "")

                # check that we can use file
                if os.path.exists(self.DEFAULTFILE) and not os.path.isfile(self.DEFAULTFILE):
                    self.error("Cannot create a log file ({})".format(self.DEFAULTFILE))
                    raise AttributeError
                else:
                    self.addFileHandler(self.DEFAULTFILE)
        except (AttributeError):
            pass

        # check the global settings
        self.prepare_dl()

    @property
    def logger(self):
        return self._logger

    def prepare_dl(self):
        global DEBUG_LEVEL
        try:
            if self.test(DEBUG_LEVEL):
                self.setDebugLevel(DEBUG_LEVEL)
        except NameError:
            self.debug("global DEBUG_LEVEL is not defined")
        finally:
            self.debug("Using the DEBUG_LEVEL ({})".format(self.debug_level))

    def setDebugLevel(self, level):
        self.debug_level = level
        self.logger.setLevel(level)

        for h in self.logger.handlers:
            h.setLevel(level)

    def info(self, msg):
        msg = self._check_msg(msg)
        self._logger.info(msg)

    def debug(self, msg):
        msg = self._check_msg(msg)
        self._logger.debug(msg)

    def error(self, msg):
        msg = self._check_msg(msg)
        self._logger.error(msg)

    def warning(self, msg):
        msg = self._check_msg(msg)
        self._logger.error(msg)

    def _check_msg(self, msg):
        if msg is not None:
            if isinstance(msg, str) or isinstance(msg, unicode):
                pass
            else:
                msg = str(msg)
        else:
            msg = str(msg)
        return msg

    def confError(self, key, def_value, e=None):
        self.error("Configuration key {0} does not exist, using default value {1}".format(key, def_value))
        if e is not None:
            self.error("Error message as follows:\n{0}".format(e))

    def confIndexError(self, index, def_value):
        self.error("Configuration index {0} does not exist, reporting default value".format(index, def_value))

    def defFailedError(self, device_path, e=None):
        self.error("Device {0} reports DevFailed error".format(device_path))
        if e is not None:
            self.error("Error message as follows:\n{0}".format(e))

    def addFileHandler(self, filename):
        self.debug("Using default filename for logging ({})".format(filename))
        fh = logging.FileHandler(filename, "w+")
        fh.setLevel(self.debug_level)
        self.logger.addHandler(fh)

    def __del__(self):
        self.debug("Removing handlers")
        handlers = self._logger.handlers[:]
        for handler in handlers:
            handler.close()
            self._logger.removeHandler(handler)


# Wrapper to test specific value types
class Tester(Logger):
    def __init__(self, def_file=None, debug_level = None):
        Logger.__init__(self, def_file=def_file, debug_level=debug_level)

        self.debug("Class initialization.")

    def test(self, value=None, type=None):
        """
        Main function testing values
        :param value:
        :param type:
        :return:
        """
        res = False

        if value is not None:
            if type is not None and isinstance(value, type):
                res = True
            elif type is None:
                res = True

        return res

    def testString(self, value):
        """
        Tests value for being a string
        :param value:
        :return:
        """
        res = False
        if self.test(value, str) or self.test(value, unicode):
            res = True
        return res

    def testFloat(self, value):
        """
        Tests value for being a float
        :param value:
        :return:
        """
        return self.test(value, float)

    def testInt(self, value):
        """
        Tests value for being an integer
        :param value:
        :return:
        """
        return self.test(value, int)

    def get_dict_value(self, data, key, def_value=""):
        """
        Returns a default value
        :param data:
        :param key:
        :return:
        """
        res = None
        try:
            res = data[key]
            if res is None:
                res = def_value
        except KeyError:
            res = def_value
        return res


class MutexLock(Tester):
    DEFAULT_FILE = "lock"
    DEFAULT_DIR = "/tmp/"
    DEF_APP_DIR = "locks"

    def __init__(self, def_file=None, debug_level=None):
        super(MutexLock, self).__init__(def_file=def_file, debug_level=debug_level)

        if not self.test(def_file):
            def_file = self.DEFAULTFILE

        def_file = "{}.lock".format(def_file)
        temp = [self.DEF_APP_DIR, def_file]

        # setting a proper log dir
        self.lock_name, self.lock_dir = None, None
        if not os.path.exists(self.DEFAULT_DIR) or not os.path.isdir(self.DEFAULT_DIR):
            self.lock_name = os.path.join(os.path.dirname(__file__), *temp)
            self.lock_dir = os.path.join(os.path.dirname(__file__), self.DEF_APP_DIR)
        else:
            self.lock_name = os.path.join(self.DEFAULT_DIR, def_file)
            self.lock_dir = self.DEFAULT_DIR

        self.lock_name = self.lock_name.replace(".pyc", "")
        self.lock_name = self.lock_name.replace(".py", "")

        self.debug("Using a lock file ({})".format(self.lock_name))

    def is_locked(self):
        """
        Returns True if the file lock exists and false otherwise
        :return:
        """
        res = False
        if os.path.exists(self.lock_name):
            res = True
        return res

    def lock(self):
        """
        Creates a lock file
        :return:
        """
        res = True
        if not os.path.exists(self.lock_name):
            tstampt = "{}".format(time.time())
            try:
                fh = open(self.lock_name, "w")
                fh.write(tstampt)
                fh.flush()
                fh.close()
            except IOError as e:
                self.error("Lock file creation error ({})".format(e.message))
        elif not os.path.isfile(self.lock_name):
            self.error("Cannot create a lock file ({})".format(self.lock_name))
            res = False
        return res

    def unlock(self):
        """
        Deletes a lock file
        :return:
        """
        res = True
        self.debug("Unlocking the process")
        if os.path.exists(self.lock_name) and os.path.isfile(self.lock_name):
            self.debug("Removing a lock file ({})".format(self.lock_name))
            try:
                os.remove(self.lock_name)
            except WindowsError:
                self.error("Windows cannot find the lock file ({})".format(self.lock_name))
        else:
            self.error("A lock file entry is not a file ({})".format(self.lock_name))
        return res

    def unlock_all(self):
        """
        Removes all lock files - i.e. startup procedure
        :return:
        """
        path = os.path.join(self.lock_dir, "*.lock")
        files = glob.glob(path)

        for file in files:
            self.debug("Removing old mutex file ({})".format(file))
            os.remove(file)

