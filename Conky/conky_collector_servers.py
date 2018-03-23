#!/usr/bin/env python

import os
import sys
import memcache
import json
import re

MEMCACHE_HOST="haspp02raspi02:55211"
COLOR_ERR = "color1"
COLOR_OK = "color2"

TMPLBAD = """
Tango Servers (${color red}malfunction$color): %ERR\n${font LCDMono:bold:size=14}${%COLOR}${voffset 4}%BODY$color${font LCDMono:bold:size=12}\n"""

TMPLOK = "Tango servers: ${color green}OK$color"

def main():
    mc = memcache.Client([MEMCACHE_HOST])

    key = "P022.tango.starter.check"
    value = mc.get(key)

    key = "P022.tango.individuals.check"
    value_individual = mc.get(key)

    output = ""
    if value is not None :
        # convert from json to string
        value = json.loads(value)
        value_individual = json.loads(value_individual)

        # combine entries on the faulty servers and show them
        try:
            value['servers'] = value['servers'] + value_individual['servers']
            if len(value['servers']) > 0:
                body = ""
                tmpl = TMPLBAD
                tmpl = tmpl.replace("%COLOR", COLOR_ERR)
                tmpl = tmpl.replace("%ERR", "{}".format(len(value['servers'])))

                patt = re.compile("[.*]Tango\.(.*)\.state")
                servers = sorted(value['servers'])
                for (i, el) in enumerate(servers):
                    temp_el = el

                    match = patt.findall(el)
                    if len(match) > 0:
                        temp_el = match[0]

                    body += "{};  ".format(temp_el)
                    if (i+1) % 3 == 0 and i > 0:
                        body += "\n"

                    if i > 8:
                        body += ".."
                tmpl = tmpl.replace("%BODY", body)
                output = tmpl
            else:
                output = TMPLOK
            print output
        except AttributeError:
            pass



if __name__=="__main__":
    main()
