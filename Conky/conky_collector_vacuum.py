#!/usr/bin/env python

import os
import sys
import memcache
import json

MEMCACHE_HOST = "haspp02raspi02:55211"
COLOR_ERR = "color1"
COLOR_OK = "color2"

TMPLFAULT = """${font LCDMono:bold:size=14}${color red}Vacuum interlock error!
${voffset 7}Please notify your local contact
${font LCDMono:bold:size=12}${voffset 7}%ERROR$color\n"""

TMPLWARNING = """\n${font LCDMono:bold:size=14}${color orange}Attention Required for interlock devices:
${font LCDMono:bold:size=12}${voffset 7}%ERROR$color"""

TMPLOK = "Vacuum interlock devices: ${color green}OK$color"


def main():
    mc = memcache.Client([MEMCACHE_HOST])

    key = "P022.vacuum.interlock"
    value_petra = mc.get(key)

    output = ""

    # petra
    if value_petra is not None:
        value_petra = value_petra.replace("\\n", "")
        data = json.loads(str(value_petra))

        bok = True
        # decide if we have an error
        berror, errormsg = iserror(data)
        if berror:
            tmpl = TMPLFAULT
            tmpl = tmpl.replace("%ERROR", errormsg)
            output += tmpl

        # decide if we have a warning
        bwarning, errormsg = iswarning(data)
        if bwarning:
            tmpl = TMPLWARNING
            tmpl = tmpl.replace("%ERROR", errormsg)
            output += tmpl

        # otherwise - report positive
        bok = not (berror or bwarning)
        if bok:
            tmpl = TMPLOK
            output += tmpl
        print output



def iserror(data):
    """

    :param data:
    :return:
    """
    berror = False
    errormsg = ""
    valves = []

    CLOSED = 1

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

    for valve in sorted(valve2check):
        try:
            if data[valve] == CLOSED:
                valves.append(valve)
        except KeyError:
            pass

    if len(valves) > 0:
        berror = True
        valvemsg = ""
        for (i, valve) in enumerate(valves):
            if i % 4 == 0:
                valvemsg += "{}\n".format(valve)
            else:
                valvemsg += "{} ".format(valve)

        if len(valvemsg) > 30:
            valvemsg = valvemsg[:100]+".."

        errormsg = "Some of the critical vacuum valves are closed:\n{}".format(valvemsg)
    return (berror, errormsg)


def iswarning(data):
    """

    :param data:
    :return:
    """
    berror = False
    errormsg = ""
    valves2close = []
    valves2open = []

    CLOSED = 1
    OPEN = 2

    valve2check_close = ["LM_20", "LM_21"]
    valve2check_open = ["LM_0", "LM_1"]

    # check the valves which should be closed
    for valve in sorted(valve2check_close):
        try:
            if data[valve] != CLOSED and data[valve] != None:
                valves2close.append(valve)
        except KeyError:
            pass

    # check the valves which should be open
    for valve in sorted(valve2check_open):
        try:
            if data[valve] != OPEN and data[valve] != None:
                valves2open.append(valve)
        except KeyError:
            pass

    errormsg = ""
    if len(valves2open) > 0:
        berror = True
        valvemsg = ""
        for (i, valve) in enumerate(valves2open):
            if i % 4 == 0:
                valvemsg += "{}\n".format(valve)
            else:
                valvemsg += "{}".format(valve)
        errormsg += "The following valves should be opened:\n{}\n".format(valvemsg)

    if len(valves2close) > 0:
        berror = True
        valvemsg = ""
        for (i, valve) in enumerate(valves2close):
            if i % 4 == 0:
                valvemsg = "{}\n".format(valve)
            else:
                valvemsg = "{}".format(valve)
        errormsg += "The following valves should be closed:\n{}\n".format(valvemsg)
    return (berror, errormsg)


if __name__ == "__main__":
    main()

