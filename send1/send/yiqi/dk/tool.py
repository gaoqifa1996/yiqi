import tornado.ioloop
import tornado.web
import tornado.httpclient
import json
import sys
import os
import time
import urllib


def get_file():
    return "/files/upload/up.json"


def log(host, info, ret):
    t = time.strftime("%Y-%m-%dT%H:%M:%S")
    print("%s: \n\r\tret: %s\n\r\thost:%s\n\r\tcmd: %s\n\r" % (t, ret, host, info))


def json_get(http_client, host, cmd):
    try:
        tmp = json.dumps(cmd)
        arg = urllib.parse.quote(tmp)
        response = http_client.fetch("%s%s" % (host, arg))

        ret = json.loads(response.body)

        log(host, tmp, ret)

        return ret
    except tornado.httpclient.HTTPError as e:
        print("Http Error: " + str(e))
        log(host, cmd, str(e))
    except Exception as e:
        print("Error: " + str(e))
        log(host, cmd, str(e))

    return None


def json_post(http_client, host, cmd):
    try:
        body = json.dumps(cmd)

        arg = tornado.httpclient.HTTPRequest(
                url=host,
                method="POST",
                headers={'Content-Type': 'application/json'},
                body=body)

        response = http_client.fetch(arg)
        ret = json.loads(response.body)

        log(host, body, ret)

        return ret
    except tornado.httpclient.HTTPError as e:
        print("Http Error: " + str(e))
        log(host, cmd, str(e))
    except Exception as e:
        print("Error: " + str(e))
        log(host, cmd, str(e))

    return None


def read_cfg():
    if not os.path.exists(get_file()):
        return None

    with open(get_file(), 'r') as f:
        ret = json.load(f)
        return ret

    return None


def write_cfg(d):
    with open(get_file(), 'w') as f:
        json.dump(d, f)


def host():
    argv = sys.argv
    host = "http://dockerhost"
    if len(argv) > 1:
        host = "127.0.0.1"

    return host


def host_xmljson():
    h = host()
    ret = "%s/xmljson/put" % h
    if h == "127.0.0.1":
        ret = "http://%s/xmljson/put" % h

    return ret


def host_timedb():
    h = host()
    ret = "%s/timedb/get" % h
    if h == "127.0.0.1":
        ret = "http://%s/timedb/get" % h

    return ret


def host_timedbput():
    h = host()
    ret = "%s/timedb" % h
    if h == "127.0.0.1":
        ret = "http://%s/timedb" % h

    return ret


def host_graphdb():
    h = host()
    ret = "%s/graphdb/md" % h
    if h == "127.0.0.1":
        ret = "http://%s/graphdb/md" % h

    return ret


def host_graphdbget():
    h = host()
    ret = "%s/graphdb/get/line-one" % h
    if h == "127.0.0.1":
        ret = "http://%s/graphdb/get/line-one" % h

    return ret


def host_real_task():
    h = host()
    ret = "%s/real/task/line-one" % h
    if h == "127.0.0.1":
        ret = "http://%s/real/task/line-one" % h

    return ret


def host_filecmd():
    h = host()
    ret = "%s/filecmd" % h
    if h == "127.0.0.1":
        ret = "http://%s:9992/filecmd" % h

    return ret


def get_item(data, key):
    if key in data:
        return data[key]
    return ""


def get_data(client, cfg, tab):
    st = None
    if tab in cfg:
        st = cfg[tab]

    if st is None:
        ret = json_post(client, host_timedb(), {
            "n": tab,
            "obj": "*",
            "opt": {
                "limit": 1
                }
            })
    else:
        ret = json_post(client, host_timedb(), {
            "n": tab,
            "obj": "*",
            "opt": {
                "limit": 20,
                "and": [
                    {"gt": "time", "v": st},
                    ]
                }
            })

    if ret is not None:
        data = ret[tab]
        cfg[tab] = data[u'end']
        return data[u'data']

    return None
