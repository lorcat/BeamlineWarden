from plugin_memcached import set_key
import time
import re
import xml.etree.ElementTree as ET

def process_xml_root(worker, xml_root, root_ref=""):
    """
    All the fields with valid, non empty value field are saved
    Some post processing is possible here
    Processes the xml adding values with specific key - id equal to the root_ref, saving to the memcache data base
    :param worker: used for debugging purposes
    :param root_ref:
    :return:
    """
    try:
        # process all update values
        for child in xml_root.findall("update"):
            # get id
            id = unicode(child.find("id").text)

            # get value
            value = unicode(child.find("value").text)

            # skip entries with empty value or id
            if not worker.test(id):
                continue

            if not worker.test(value):
                continue

            if value == ".":
                continue

            # replace links and make full http link for image files
            pattern = re.compile(u"(.jpg)|(.png)|(.gif)")
            if len(pattern.findall(value)) > 0:
                # find http dir to use for the full link construction
                temp = ""
                match = re.compile(u"(.*\/)[^\/]*").match(worker.init_page)
                if worker.test(match):
                    temp = match.group(1)

                value = u"{}:{}{}{}".format(worker.HOST, worker.PORT, temp, value)
                child.find(u"value").text = value

            # setting the key
            id = u"{}{}".format(root_ref, id)

            # set memcache
            set_key(id, value, logger=worker)

            # set timestamp
            id = u"{}{}".format(root_ref, "timestamp")
            set_key(id, time.time(), logger=worker)

    except ET.ParseError as e:
        worker.error(u"Could not process data - invalid response from the server: {}".format(e))