import tornado.ioloop
import tornado.web
import tornado.httpclient
import json
import sys
import os
import time
import datetime
from urllib.parse import quote


def get_log():
    return "/files/upload/log/"


def get_file():
    return "/files/upload/up.json"


def init_log():
    if not os.path.exists(get_log()):
        os.makedirs(get_log())


def log(host, info, ret):
    d = time.strftime("%Y%m%d")
    path = "%s/%s.txt" % (get_log(), d)

    with open(path, 'a') as f:
        t = time.strftime("%Y-%m-%dT%H:%M:%S")
        f.write("%s: \n\r" % t)
        f.write("\tret: %s \n\r" % ret)
        f.write("\thost: %s\n\r" % host)
        f.write("\tcmd: %s\n\r\n\r" % info)


def json_get(http_client, host, cmd):
    try:
        tmp = json.dumps(cmd)
        arg = quote(tmp)
        # print(arg)
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
    print(host)
    try:
        body = json.dumps(cmd)
        arg = tornado.httpclient.HTTPRequest(
                url=host,
                method="POST",
                headers={'Content-Type': 'application/json'},
                body=body)

        response = http_client.fetch(arg)
        ret = json.loads(response.body)
	
        #log(host, body, ret)

        return ret
    except tornado.httpclient.HTTPError as e:
	
        print("Http Error: " + str(e))
        #log(host, cmd, str(e))
    except Exception as e:
        print("Error: " + str(e))
        #log(host, cmd, str(e))

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


def host_cfg():
    h = host()
    ret = "%s/cfg" % h
    if h == "127.0.0.1":
        ret = "http://%s:9998" % h

    return ret


def host_timedb():
    h = host()
    ret = "%s/timedb/get" % h
    if h == "127.0.0.1":
        ret = "http://%s" % h
    # print(ret)
    return ret

def host_timedbput():
    h = host()
    ret = "%s/timedb" % h
    if h == "127.0.0.1":
        ret = "http://%s" % h
    # print(ret)
    return ret


def host_graphdb():
    h = host()
    ret = "%s/graphdb/md" % h
    if h == "127.0.0.1":
        ret = "http://%s" % h
    # print(ret)
    return ret

def host_graphdbget():
    h = host()
    ret = "%s/graphdb/get/line-one" % h
    if h == "127.0.0.1":
        ret = "http://%s" % h
    # print(ret)
    return ret

def host_real_task():
    h = host()
    ret = "%s/real/task/line-one" % h
    if h == "127.0.0.1":
        ret = "http://%s" % h
    # print(ret)
    return ret

def host_filecmd():
    h = host()
    ret = "%s/filecmd" % h
    if h == "127.0.0.1":
        ret = "http://%s:9992" % h

    return ret


def get_model():
    cfg_host = host_cfg()

    http_client = tornado.httpclient.HTTPClient()
    model = json_post(http_client, cfg_host, {
        "cmd": "get",
        "key": "client"
        })
    http_client.close()

    return model


def do_compress():
    d = datetime.datetime.now()
    w = d.weekday()
    if w != 0:
        return

    h = d.hour
    if h < 2 or h > 7:
        return

    d = time.strftime("%Y%m%d.txt")

    ret = []

    dirpath = get_log()

    for x in os.listdir(dirpath):
        if x.endswith('.txt'):
            if x != d:
                ret.append(x)

    if len(ret) <= 0:
        return

    host = host_filecmd()
    http_client = tornado.httpclient.HTTPClient()

    for x in ret:
        json_post(http_client, host, {
            "cmd": "gzip",
            "path": "upload/log/%s" % x
            })

    http_client.close()
