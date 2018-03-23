__author__ = "Konstantin Glazyrin (lorcat@gmail.com)"

from app.common import *

from PyTango import DeviceProxy, DevFailed, DevState

class PyTangoWorker(MutexLock):
    def __init__(self, device=None, def_file=None, debug_level=None):
        super(PyTangoWorker, self).__init__(def_file=def_file, debug_level=debug_level)

        self.device = device

    def read_attribute(self, attr):
        """
        Reads attribute value, returns none in case of na error
        :param attr:
        :return:
        """
        res = None
        try:
            if not self.test(self.device):
                raise ValueError

            d = DeviceProxy(self.device)
            d.ping()

            self.debug("Device ({}) is online".format(self.device))

            state = d.state()
            value = None

            # read value only if the state is fine
            if state != DevState.FAULT and state != DevState.UNKNOWN:
                value = d.read_attribute(attr).value

            self.debug("Attribute value ({}/{}/{})".format(state, attr, value))
            res = (state, value)
        except DevFailed:
            self.error("There is an error with access to the device ({})".format(self.device))
        except ValueError:
            self.error("User has not provided a valid device name")

        return res

    def read_attributes(self, attrs):
        """
        Reads attribute value, returns none in case of na error
        :param attr:
        :return:
        """
        res = []
        try:
            if not self.test(self.device):
                raise ValueError

            d = DeviceProxy(self.device)
            d.ping()

            self.debug("Device ({}) is online".format(self.device))

            state = d.state()
            values = None

            # read value only if the state is fine
            if state != DevState.FAULT and state != DevState.UNKNOWN:
                values = d.read_attributes(attrs)

                for value in values:
                    res.append(value.value)

            self.debug("Attributes value ({}/{}/{})".format(state, attrs, res))
        except DevFailed:
            self.error("There is an error with access to the device ({})".format(self.device))
        except ValueError:
            self.error("User has not provided a valid device name")

        return res

    def make_test(self, attr=None):
        """
        Performs a full test of the tango server device
        If the attribute is given - trying to read it as well
        :param attr:
        :return:
        """
        #@TODO : test database
        res = True
        try:
            d = DeviceProxy(self.device)
            self.debug("Device ({}) ping value ({})".format(self.device, d.ping()))

            state = d.state()

            if state == DevState.FAULT or state == DevState.UNKNOWN:
                raise DevFailed

            if self.testString(attr):
                v = d.read_attribute(attr)

        except (DevFailed, AttributeError) as e:
            res = False

        return res