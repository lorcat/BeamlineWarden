import os

# Configuration for the daemon

# Tick interval - daemon sleep time is set by DAEMON_TIME_TICK/DAEMON_TIME_DIVIDER
DAEMON_TIME_TICK = 0.1
DAEMON_TIME_DIVIDER = 1.

# root file param for application purposes
FILE_ROOT = os.path.dirname(__file__)

# Logging
LOGGING_MAIN_FORMAT = '%(asctime)s %(levelname)-8s %(process)-8d %(thread)-10d %(threadName)-16s %(name)-12s: %(message)s'
LOGGING_MAIN_DATE = '%m-%d %H:%M'

LOGGING_FILE_FORMAT = '%(asctime)s %(levelname)-8s %(process)-8d %(thread)-10d %(threadName)-16s %(name)-12s: %(message)s'
LOGGING_FILE_DATE = '%Y-%m-%d %H:%M:%S'

# Locking dir - local, app specific
LOCKING_LOCAL_DIR = "locks"
# default dir for locking - local to app
LOCKING_DIR = '/tmp/'