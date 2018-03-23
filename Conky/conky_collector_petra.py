#!/usr/bin/env python

import os
import sys
import memcache
import json
import datetime
import time

MEMCACHE_HOST="haspp02raspi02:55211"
COLOR_ERR = "color1"
COLOR_OK = "color2"

TMPL = """${font LCDMono:bold:size=50}${color FFF176}%TIMESTAMP$color
${font LCDMono:bold:size=12}${color FFF176}Last update: Petra (%TSTAMPPETRA) Und. (%TSTAMPUND) DCM (%TSTAMPDCM)
${font LCDMono:bold:size=12}${color white}${voffset 10}Energy    : %ENERGY GeV
${voffset -20}${goto 250}Current: %CURRENT mA
${voffset 4}N. Bunch : %BUNCHES
${voffset -20}${goto 250}F. Orbit: %FORBIT
${voffset 6}TopUp  : %TOPUP

${voffset 4}Undulator : %UNDSTATE
${voffset -20}${goto 250}GAP: ${color green}%UNDGAP$color mm
${voffset 4}DCM Energy : ${color green}%DCMENERGY$color eV
${voffset -20}${goto 250}Offset: %DCMOFFSET mm
${voffset 5}${goto 52}Bragg: %DCMBRAGG
${voffset -20}${goto 250}Unit C.: %DCMUCBRAGG
${voffset 15}Message:
%EXP%MSG
"""

TMPL_MEMCACHE_ERROR = """
${font LCDMono:bold:size=12}${color red}Error communication with logging device$color
"""

TMPLON = "${color green}%VALUE$color"
TMPLOTHER = "${color purple}%VALUE $color"

def main():
    mc = memcache.Client([MEMCACHE_HOST])

    key_petra = "Petra"
    value_petra = mc.get(key_petra)

    key_und = "P022.undulator"
    value_und = mc.get(key_und)

    key_dcm = "P022.dcm"
    value_dcm = mc.get(key_dcm)

    key_dcm_bragg = "P022.dcm.bragg"
    value_dcm_bragg = mc.get(key_dcm_bragg)

    if value_petra is not None:
        value_petra = json.loads(value_petra)
        value_und = json.loads(value_und)
        value_dcm = json.loads(value_dcm)
        value_dcm_bragg = json.loads(value_dcm_bragg)

        # print(value_petra)
        # print(value_und)
        # print(value_dcm)
        # print(value_dcm_bragg)

        tmpl = TMPL

        res = ""
        try:
            # main timestamp - current time
            timestamp = int(time.time())
            timestamp = datetime.datetime.fromtimestamp(timestamp).strftime('${font LCDMono:bold:size=30}%d/%m ${color white}Petra-III$color\n${color FFF176}${font LCDMono:bold:size=50}%H:%M:%S${font LCDMono:bold:size=20}')
            tmpl = tmpl.replace("%TIMESTAMP", "{}".format(timestamp))

            # timestamp petra
            timestamp = int(set_value(value_petra, "timestamp"))
            timestamp = datetime.datetime.fromtimestamp(timestamp).strftime(
                '%H:%M:%S')
            tmpl = tmpl.replace("%TSTAMPPETRA", "{}".format(timestamp))

            # timestamp undulator
            timestamp = int(set_value(value_und, "timestamp"))
            timestamp = datetime.datetime.fromtimestamp(timestamp).strftime(
                '%H:%M:%S')
            tmpl = tmpl.replace("%TSTAMPUND", "{}".format(timestamp))

            # timestamp dcm
            timestamp = int(set_value(value_dcm, "timestamp"))
            timestamp = datetime.datetime.fromtimestamp(timestamp).strftime(
                '%H:%M:%S')
            tmpl = tmpl.replace("%TSTAMPDCM", "{}".format(timestamp))


            # energy
            energy = set_value(value_petra, "Energy")
            tmpl = tmpl.replace("%ENERGY", "{:0.1f}".format(energy))

            # beamcurrent
            current = set_value(value_petra, "BeamCurrent")
            if current <= 25.:
                current = "${color red}"+"{:03.1f}".format(current)+"$color"
            elif current >= 75.:
                current = "${color green}" + "{:03.1f}".format(current) + "$color"
            else:
                current = "${color0}" + "{:03.1f}".format(current) + "$color"
            tmpl = tmpl.replace("%CURRENT", "{}".format(current))

            bunches = int(set_value(value_petra, "NumberOfBunches"))
            tmpl = tmpl.replace("%BUNCHES", "{}".format(bunches))


            fob = int(set_value(value_petra, "FastOrbitFBStatus"))
            if fob == 1:
                fob = "${color green}ON$color"
            else:
                fob = "${color green}OFF$color"
            tmpl = tmpl.replace("%FORBIT", "{}".format(fob))

            msg_machine = set_value(value_petra, "MachineStateText", def_value="")
            tmpl = tmpl.replace("%EXP", "{}".format(msg_machine))

            msg_topup = set_value(value_petra, "TopUpStatusText", def_value="")
            tmpl = tmpl.replace("%TOPUP", "{}".format(msg_topup))

            msgtext = set_value(value_petra, "MessageText", def_value="")
            if len(str(msgtext)) > 0:
                msgtext = "\n"+msgtext
            tmpl = tmpl.replace("%MSG", "{}".format(msgtext))

            # DCM
                # Energy
            dcm_energy = set_value(value_dcm, "Position", def_value=0.)
            if isinstance(dcm_energy, float):
                dcm_energy = "{:.0f}".format(dcm_energy)
            tmpl = tmpl.replace("%DCMENERGY", "{}".format(dcm_energy))

                # Offset
            dcm_offset = set_value(value_dcm, "ExitOffset")
            if isinstance(dcm_offset, float):
                dcm_offset = "{:.2f}".format(dcm_offset)
            tmpl = tmpl.replace("%DCMOFFSET", "{}".format(dcm_offset))
                # Bragg
            dcm_bragg = set_value(value_dcm, "BraggAngle")
            if isinstance(dcm_bragg, float):
                dcm_bragg = "{:.5f}".format(dcm_bragg)
            tmpl = tmpl.replace("%DCMBRAGG", "{}".format(dcm_bragg))
                # unit calibration
            dcm_ucal = set_value(value_dcm_bragg, "UnitCalibration")
            if isinstance(dcm_ucal, float):
                dcm_ucal = "{:.5f}".format(dcm_ucal)
            tmpl = tmpl.replace("%DCMUCBRAGG", "{}".format(dcm_ucal))

            # undulator
                # state
            und_state = set_value(value_und, "State", def_value="")
            tmpl_temp = TMPLON
            if und_state.lower() != "on":
                tmpl_temp = TMPLOTHER
            und_state = tmpl_temp.replace("%VALUE", und_state)
            tmpl = tmpl.replace("%UNDSTATE", "{}".format(und_state))

                # gap
            und_gap = set_value(value_und, "Gap", def_value=-1.)
            if isinstance(und_gap, float):
                und_gap = "{:.3f}".format(und_gap)
            tmpl = tmpl.replace("%UNDGAP", "{}".format(und_gap))


            # final result
            res = tmpl
        except KeyError:
            pass

        print res
    else:
        # print that there is an error with communication to the logging device
        print TMPL_MEMCACHE_ERROR

def set_value(data, key, def_value=0.):
    """
    Returns a value or a default one
    :param data:
    :param key:
    :param def_value:
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

def reformat(value, type, value_format, def_format="{}"):
    """
    changes the type of the value with respect to the format
    :param value:
    :param type:
    :param format:
    :param def_format:
    :return:
    """
    res = def_format.format(value)
    if isinstance(value, type):
        res = value_format.format(value)
    return res

if __name__=="__main__":
    main()


# @TODO: check values for None
# @TODO: split DCM, undulator and petra into separate functions