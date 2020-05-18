import xmltodict
import json
import time
from wxml import json_xml


def log(cmd, data, ret):
    t = time.strftime("%Y-%m-%dT%H:%M:%S")
    print("%s: \n\r\tcmd: %s\n\r\tdata:%s\n\r\tret: %s\n\r" % (t, cmd, data, ret))


def do_post_cmd(cmd, data):
    if cmd == "xmljson":
        ret = xmltodict.parse(data)

        log(cmd, data, json.dumps(ret, ensure_ascii=False))

        return ret
    elif cmd == "jsonxml":
        ret = json_xml(data)

        log(cmd, data, ret)

        if ret is None:
            return "Fail"

        return {"v": ret}

    return "Fail"
