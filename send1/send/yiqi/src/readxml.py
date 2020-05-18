from tool import json_post, host_xmljson


def xml2json(client, xml):
    if xml is None:
        return None

    ret = json_post(client, host_xmljson(), {
        "cmd": "xmljson",
        "data": str(xml)
    })

    if ret == "Fail" or ret is None:
        return None


    env = ret["env:Envelope"]

    body = env["Body"]
    data = body["Data"]
    raw = data["Raw"]
    detail = raw["Detail"]

    ret = {}

    for d in detail:
        ret[d["Key"]] = d["Value"]

    return ret


def json2xml(client, k, v):
    if v is None:
        return None

    ret = json_post(client, host_xmljson(), {
        "cmd": "jsonxml",
        "data": {
            "k": k,
            "v": v
            }
        })

    if ret == "Fail" or ret is None:
        return None

    return ret["v"]
