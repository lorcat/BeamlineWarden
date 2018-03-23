__author__ = "Konstantin Glazyrin (lorcat@gmail.com)"

from app import *
from app.common import *
from app.plugins import *
from app.config import *

class CrontabWorker(MutexLock):
    REF_FILE = __file__

    STORAGE_DIR = "storage"
    STORAGE_FILE_PETRA = "petra.log"
    STORAGE_FILE_TANGO = "tango.log"
    STORAGE_FILE_TANGO_INDIVIDUAL = "tango_individual.log"
    STORAGE_FILE_VACUUM = "vacuum.log"

    IMAGE_ERROR = "twitter_msg_err.png"
    IMAGE_OK = "twitter_msg_ok.png"
    IMAGE_VALVE = "twitter_msg_valve.png"
    IMAGE_TANGO_CRASH = "twitter_msg_tango.png"

    P3_DUMP_CONDITIOM = 20.
    P3_RECOVERY_CONDITION = 70.

    VALVES_CLOSED = 1

    COLOR_GREY = (128, 127, 127)
    COLOR_RED = (255, 0, 0)
    COLOR_GREEN = (0, 255, 0)
    COLOR_DGREEN = (0, 102, 0)
    COLOR_WHITE = (255, 255, 255)

    KEY_CURRENT = "BeamCurrent"
    KEY_SERVERS = "servers"

    FONT = FONT_TEXT

    def __init__(self, def_file=None, debug_level=None):
        super(CrontabWorker, self).__init__(def_file=def_file, debug_level=debug_level)

        self.petra_down = False
        self.petra_up = False

        self.tango_down = False

    def get_storage_file(self, key):
        """
        Recovers the common directory
        :param key:
        :return:
        """
        res = None
        temp = [self.STORAGE_DIR, key]
        file_path = os.path.join(os.path.dirname(self.REF_FILE), *temp)
        self.debug("Using storage path ({})".format(file_path))

        if not os.path.exists(file_path) or os.path.isfile(file_path):
            res = file_path
        return res

    def process_petra_data(self, data):
        """
        Process data for petra and make a statement
        :param data:
        :return:
        """
        self.debug("Processing Petra-3 data")
        fn = self.get_storage_file(self.STORAGE_FILE_PETRA)

        if self.test(fn):
            old_data = None

            # new file - no data exists - we report everything
            if os.path.exists(fn):
                old_data = self.get_pickled_data(self.get_storage_file(self.STORAGE_FILE_PETRA))
                self.debug("Old data is ({})".format(old_data))

            if isinstance(data, dict) and not data.has_key(self.KEY_CURRENT):
                self.error("Could not get current value - key is missing ({})".format(self.KEY_CURRENT))
                return

            # process current
            if data[self.KEY_CURRENT] <= self.P3_DUMP_CONDITIOM:
                # check beamdump condition
                self.debug("Petra current satisfies dump conditions")
                try:
                    if self.test(old_data, dict) and old_data.has_key(self.KEY_CURRENT) and old_data[self.KEY_CURRENT] > self.P3_DUMP_CONDITIOM:
                        raise ValueError
                    elif not self.test(old_data):
                        raise ValueError
                except ValueError:
                    # report a beamdump
                    self.debug("P3 Beamdump")
                    self.report_p3beamdump(data)

            elif data[self.KEY_CURRENT] >= self.P3_RECOVERY_CONDITION:
                # check beam recovery condition
                try:
                    if self.test(old_data, dict) and old_data.has_key(self.KEY_CURRENT) and old_data[self.KEY_CURRENT] < self.P3_RECOVERY_CONDITION:
                        raise ValueError
                except ValueError:
                    # beamdump
                    self.debug("P3 recovery")
                    self.report_p3recovery(data)


        # save data for the next use
        self.save_pickled_data(fn, data)

    def process_vacuum(self, data):
        """
        Processes the values related to the vacuum system
        :param data:
        :return:
        """
        self.debug("Processing vaccuum data")
        fn = self.get_storage_file(self.STORAGE_FILE_VACUUM)

        if self.test(fn):
            old_data = None

            # new file - no data exists - we report everything
            if os.path.exists(fn):
                old_data = self.get_pickled_data(self.get_storage_file(self.STORAGE_FILE_VACUUM))
                self.debug("Old data is ({})".format(old_data))

            valve2check = ["V_0",
                           "V_1",
                           "V_10",
                           "V_11",
                           "V_12",
                           "V_20",
                           "V_21",
                           "V_22",
                           "V_23",
                           "V_24",
                           "PS_2"]
            bnew = False
            err_valves = []
            new_valves = []
            for valve in sorted(valve2check):
                try:
                    if data[valve] == self.VALVES_CLOSED:
                        err_valves.append(valve)
                        if self.test(old_data) and not valve in old_data:
                            new_valves.append(valve)
                except KeyError:
                    pass

            # if the valve is new
            if len(new_valves) > 0:
                self.report_vacuumvalve(new_valves)

            # save data for the next use
            self.save_pickled_data(fn, err_valves)

    def process_tango_servers(self, data):
        """
        Processes the values related to the vacuum system
        :param data:
        :return:
        """
        self.debug("Processing tango server data ({})".format(data))
        fn = self.get_storage_file(self.STORAGE_FILE_TANGO)

        if self.test(fn):
            old_data = None

            # new file - no data exists - we report everything
            if os.path.exists(fn):
                old_data = self.get_pickled_data(self.get_storage_file(self.STORAGE_FILE_TANGO))
                self.debug("Old data is ({})".format(old_data))

            if isinstance(data, dict) and not data.has_key(self.KEY_SERVERS):
                self.error("Could not get current value - key is missing ({})".format(self.KEY_SERVERS))
                return

            bnew = False
            new_servers = []
            for server in sorted(data[self.KEY_SERVERS]):
                try:

                    if old_data is None or not server in old_data :
                        new_servers.append(server)
                except KeyError:
                    pass

            # if the valve is new
            if len(new_servers) > 0:
                self.report_tango_servers(new_servers)

            # save data for the next use
            self.save_pickled_data(fn, data[self.KEY_SERVERS])

    def process_tango_individual_servers(self, data):
        """
        Processes the values related to the vacuum system
        :param data:
        :return:
        """
        self.debug("Processing individual tango server data ({})".format(data))
        fn = self.get_storage_file(self.STORAGE_FILE_TANGO_INDIVIDUAL)

        if self.test(fn):
            old_data = None

            # new file - no data exists - we report everything
            if os.path.exists(fn):
                old_data = self.get_pickled_data(self.get_storage_file(self.STORAGE_FILE_TANGO_INDIVIDUAL))
                self.debug("Old data is ({})".format(old_data))

            if isinstance(data, dict) and not data.has_key(self.KEY_SERVERS):
                self.error("Could not get current value - key is missing ({})".format(self.KEY_SERVERS))
                return

            bnew = False
            new_servers = []
            self.debug("Server values are: ({})".format(type(data)))
            for server in sorted(data[self.KEY_SERVERS]):
                patt = re.compile("[.*]Tango\.(.*)\.state")
                try:
                    if old_data is None or not server in old_data:
                        tmp_server = server
                        match = patt.findall(server)
                        if len(match) > 0:
                            tmp_server = match[0]
                        new_servers.append(tmp_server)
                except KeyError:
                    pass

            # if the valve is new
            if len(new_servers) > 0:
                self.report_tango_servers(new_servers)

            # save data for the next use
            self.save_pickled_data(fn, data[self.KEY_SERVERS])

    def report_p3beamdump(self, data):
        """
        Creates an image and a posts on the tweeter account
        :return:
        """
        tfn = self.get_tempimagefile()
        errfn = self.get_imageerr_path()

        self.debug("Using the following filenames ({}/{})".format(tfn, errfn))

        texts = []
        texts.append(pil_text_dict("Beamdump:(", (75, 56), self.COLOR_WHITE, [self.FONT, 40]))
        texts.append(pil_text_dict("Petra Current:", (75, 120), self.COLOR_WHITE, [self.FONT, 36]))

        current = "{:.0f} mA".format(self.get_dict_value(data, self.KEY_CURRENT, def_value=0.))
        texts.append(pil_text_dict(current, (290, 120), self.COLOR_WHITE, [self.FONT, 36]))

        # create image
        pil_report_petra_msg(errfn, tfn, texts, self)

        # report twitter
        msg = "Sad news - we got a beamdump"
        twitter_imgmsg(msg, tfn, self)

    def report_p3recovery(self, data):
        """
        Creates an image and a posts on the tweeter account
        :return:
        """
        tfn = self.get_tempimagefile()
        okfn = self.get_imageok_path()

        self.debug("Using the following filenames ({}/{})".format(tfn, okfn))

        texts = []
        texts.append(pil_text_dict("Petra3 is recovering:)", (75, 56), self.COLOR_DGREEN, [self.FONT, 40]))
        texts.append(pil_text_dict("Petra Current:", (75, 120), self.COLOR_DGREEN, [self.FONT, 36]))

        current = "{:.0f} mA".format(self.get_dict_value(data, self.KEY_CURRENT, def_value=0.))
        texts.append(pil_text_dict(current, (290, 120), self.COLOR_WHITE, [self.FONT, 36]))

        # create image
        pil_report_petra_msg(okfn, tfn, texts, self)

        # report twitter
        msg = "Good news - Petra is recovering"
        twitter_imgmsg(msg, tfn, self)

    def report_vacuumvalve(self, data):
        """
        Creates an image and a posts on the tweeter account
        :return:
        """
        tfn = self.get_tempimagefile()
        valvefn = self.get_imagevalve_path()

        self.debug("Using the following filenames ({}/{})".format(tfn, valvefn))

        texts = []
        texts.append(pil_text_dict("Vacuum valve closed", (75, 56), self.COLOR_GREY, [self.FONT, 40]))

        valves_msg = ""
        if len(data) > 0:
            valves_msg = ", ".join(data)
        texts.append(pil_text_dict(valves_msg, (75, 120), self.COLOR_GREY, [self.FONT, 28]))

        # create image
        pil_report_petra_msg(valvefn, tfn, texts, self)

        # report twitter
        msg = "Attention - some valves are closed: {}".format(valves_msg)
        twitter_imgmsg(msg, tfn, self)

    def report_tango_servers(self, data):
        """
        Creates an image and a posts on the tweeter account
        :return:
        """
        tfn = self.get_tempimagefile()
        tangofn = self.get_imagetangocrash_path()

        self.debug("Using the following filenames ({}/{})".format(tfn, tangofn))

        texts = []
        texts.append(pil_text_dict("Tango Server Crashed", (75, 56), self.COLOR_GREY, [self.FONT, 40]))

        tango_full_msg = ""
        tango_full_msg = ""
        if len(data) > 0:
            tango_full_msg = ", ".join(data)
            tango_msg = "{}..".format(data[0])

        texts.append(pil_text_dict(tango_msg, (75, 120), self.COLOR_RED, [self.FONT, 28]))

        # create image
        pil_report_petra_msg(tangofn, tfn, texts, self)

        # report twitter
        msg = "Attention - tango server crash: {}".format(tango_full_msg)
        twitter_imgmsg(msg, tfn, self)

    def save_pickled_data(self, filename, data):
        """
        Transformes the data into a pickle and saves it
        :param filename:
        :param data:
        :return:
        """
        try:
            self.debug("Saving pickled data ({})".format(filename))
            fh = open(filename, "w")
            pickle.dump(data, fh)
            fh.close()
        except IOError as e:
            self.error("Error upon accessing the file ({})".format(filename))
            self.error(e)

    def get_pickled_data(self, filename):
        """
        Reads a file and returns its content unpickled
        :param filename:
        :param data:
        :return:
        """
        res = None
        try:
            fh = open(filename, "r")
            temp_data = pickle.load(fh)
            if self.test(temp_data):
                res = temp_data
            fh.close()
        except IOError as e:
            self.error("Error upon accessing the file ({})".format(filename))
            self.error(e)
        return res

    def get_image_path(self, output_file):
        """
        Returns the path for the OK image template
        :return:
        """
        temp = ["images", output_file]
        return os.path.join(os.path.dirname(self.REF_FILE), *temp)

    def get_imageok_path(self):
        """
        Returns the path for the OK image template
        :return:
        """
        return self.get_image_path(self.IMAGE_OK)

    def get_imagevalve_path(self):
        """
        Returns the path for the valve image template
        :return:
        """
        return self.get_image_path(self.IMAGE_VALVE)

    def get_imageerr_path(self):
        """
        Returns the path for the OK image template
        :return:
        """
        return self.get_image_path(self.IMAGE_ERROR)

    def get_imagetangocrash_path(self):
        """
        Returns the path for the OK image template
        :return:
        """
        return self.get_image_path(self.IMAGE_TANGO_CRASH)

    def get_tempimagefile(self):
        """
        Creates a temporary file and returns its name
        :return:
        """
        bd = os.path.join(os.path.dirname(self.REF_FILE), "images")
        self.debug("Temporary image directory ({})".format(bd))

        # generate a temporary filename
        tfh = tempfile.NamedTemporaryFile(suffix='.png',
                                   prefix='image_',
                                   dir=bd)
        self.debug("Obtained an temporary image file ({})".format(tfh.name))
        name = tfh.name
        tfh.close()
        return name

