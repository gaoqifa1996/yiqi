import pymqi
from tool import (get_data, log, get_item, read_cfg, write_cfg, json_post, host_timedb, host_graphdb, host_graphdbget, host_real_task, host_timedbput)
import tornado
import tornado.httpclient
from readxml import xml2json, json2xml
import datetime
import time

qmgr = pymqi.QueueManager(None)


def mq_put(q, v):
    try:
        queue = pymqi.Queue(qmgr, q)
        queue.put(v)
        queue.close()

        log(q, "mq put", v)
    except Exception as e:
        log(q, "mq put error", e)


def mq_get(client, q):
    try:
        queue = pymqi.Queue(qmgr, q)
        ret = queue.get()
        queue.close()

        log(q, "mq get", ret)

        ret = xml2json(client, ret)

        return ret
    except Exception as e:
        log(q, "mq get error", e)
        return None


def put_bzd(client, cfg):
    mdata = get_data(client, cfg, "msn")
    hioki = get_data(client, cfg, "hioki")

    # {
    #     psn: {
    #        wsn: [bzd1, bzd2]
    #     }
    # }
    ret = {}

    if mdata is not None:
        for d in mdata:
            psn = d["psn"]
            wsn = d["wsn"]
            bzd = d["msn"]

            if psn in ret:
                tmp = ret[psn]
                if wsn in tmp:
                    tmp[wsn].append(bzd)
                else:
                    tmp[wsn] = [bzd]
            else:
                ret[psn] = {wsn: [bzd]}

    if hioki is not None:
        for d in hioki:
            psn = d["psn"]
            wsn = d["wsn"]
            bzd = d["dmcdata"]

            if psn in ret:
                tmp = ret[psn]
                if wsn in tmp:
                    tmp[wsn].append(bzd)
                else:
                    tmp[wsn] = [bzd]
            else:
                ret[psn] = {wsn: [bzd]}

    for p, d in ret.iteritems():
        for w, m in d.iteritems():
            ret = json2xml(client, "msn", {"psn": p, "wsn": w, "bzd": m})
            mq_put("MES.MEB.ASSEMBLE.RESULT", ret)


def put_fin(client, cfg):
    st = None
    if "snfinsh" in cfg:
        st = cfg["snfinsh"]

    if st is None:
        info = json_post(client, host_timedb(), {
            "n": "stnstatus",
            "obj": "*",
            "opt": {
                "limit": 1,
                "and": [{"eq": "wsn", "v": "af450"}]
            }
        })
    else:
        info = json_post(client, host_timedb(), {
            "n": "stnstatus",
            "obj": "*",
            "opt": {
                "limit": 1,
                "and": [
                    {"eq": "wsn", "v": "af450"},
                    {"gt": "time", "v": st}
                ]
            }
        })

    if info is None:
        return

    data = info["stnstatus"]
    cfg["snfinsh"] = data[u'end']
    data = data[u'data'][0]

    ret = json2xml(client, "fin", {"psn": data["psn"], "in": data["in"], "out": data["out"]})

    mq_put("MES.MEB.ASSEMBLE.START", ret)
    time.sleep(5)
    mq_put("MES.MEB.ASSEMBLE.FINISH", ret)


def get_plan(client):
    data = mq_get(client, "MES.MEB.ASSEMBLE.PLAN.SEND")
    if data is None:
        return

    start = datetime.datetime.strptime(data["PT"], "%Y%m%d%H%M%S")
    diff = datetime.timedelta(minutes=15)

    pstart = start.strftime("%Y-%m-%dT%H:%M:%S")
    pend = (start + diff).strftime("%Y-%m-%dT%H:%M:%S")

    sn = data["CID"]

    ret = json_post(client, host_real_task(), {
        "sn": sn,
        "tsn": data["TSN"],
        "pstart": str(pstart),
        "pend": str(pend),
        "pnum": 1,
        "info": [
            {"k": "ig2", "v": data["1G2"]},
            {"k": "288", "v": data["288"]},
            {"k": "gbt", "v": data["GBT"]},
            {"k": "sqr", "v": data["SQR"]},
            {"k": "prn", "v": data["PRN"]},
            {"k": "tsn", "v": data["TSN"]}
        ]
    })

    if ret != "Success":
        return

    ret = json_post(client, host_graphdbget(), {
        "n": "task",
        "obj": "uid,sn",
        "opt": {
            "and": [{"eq": "sn", "v": sn}]
        }
    })

    if ret is None:
        return

    uid = ret[0]["uid"]

    ret = json_post(client, host_graphdb(), {
        "a": [{
            "u": uid,
            "n": "pcode",
            "v": [[{"k": "sn", "v": sn}]]
        }]
    })

    if ret != "Success":
        return

    ret = json2xml(client, "ack", "")

    mq_put("MES.MEB.ASSEMBLE.PLAN.ACK", ret)


def put_print(client, cfg):
    st = None
    if "emergency" in cfg:
        st = cfg["emergency"]

    if st is None:
        ret = json_post(client, host_timedb(), {
            "n": "stnstatus",
            "obj": "*",
            "opt": {
                "desc": True,
                "limit": 1,
                "and": [{"eq": "wsn", "v": "af450"}]
            }
        })
    else:
        ret = json_post(client, host_timedb(), {
            "n": "stnstatus",
            "obj": "*",
            "opt": {
                "desc": True,
                "limit": 1,
                "and": [
                    {"eq": "wsn", "v": "af450"},
                    {"gt": "time", "v": st}]
            }
        })

    if ret is None:
        return

    data = ret["stnstatus"]
    cfg["emergency"] = data[u'end']
    data = data[u'data'][0]

    ret = json2xml(client, "print", {"psn": data["psn"]})
    mq_put("MES.MEB.ASSEMBLE.CERTIFICATE.FAST.REQUEST", ret)


def get_printcode(client):
    qret = mq_get(client, "MES.MEB.ASSEMBLE.CERTIFICATE.SEND")
    if qret is None:
        return

    status = get_item(qret, u"STATUS")
    sn = get_item(qret, u"CID")
    tele = get_item(qret, u"TELE")
    errtele = get_item(qret, u"ERRTELE")

    data = json_post(client, host_timedb(), {
        "n": "task",
        "obj": "*",
        "opt": {
            "desc": True,
            "limit": 1,
            "and": [
                {"eq": "task", "v": sn},
                {"eq": "line", "v": "line-one"}
            ]
        }
    })

    if data is None:
        return

    data = data["task"]["data"][0]
    data.pop("task")
    data.pop("line")

    data["tele"] = tele
    data["errtele"] = errtele
    data["status"] = status

    json_post(client, host_timedbput(), {
        "cmd": "put",
        "data": {
            "tab": "task",
            "tags": {
                "line": "line-one",
                "task": sn
            },
            "fields": data
        }
    })


def do_post_cmd(cmd):
    client = tornado.httpclient.HTTPClient()
    cfg = read_cfg()

    if cfg is None:
        cfg = {}

    if cmd == "putfinsh":
        put_fin(client, cfg)
    elif cmd == "putprint":
        put_print(client, cfg)
    elif cmd == "putmsn":
        put_bzd(client, cfg)
    elif cmd == "getplan":
        get_plan(client)
    elif cmd == "getprintstr":
        get_printcode(client)

    client.close()

    write_cfg(cfg)


def do_task():
    try:
        qmgr.connect_tcp_client("VMFSMESMQTEST1", pymqi.CD(), "CLI.PD.MES.MEB.1", "10.232.129.54(1416)", "mqm", "mqm")
    except pymqi.MQMIError as e:
        if e.comp == pymqi.CMQC.MQCC_WARNING and e.reason == pymqi.CMQC.MQRC_ALREADY_CONNECTED:
            pass
        else:
            print("mq error: %s" % e)
            return

    client = tornado.httpclient.HTTPClient()

    cfg = read_cfg()
    if cfg is None:
        cfg = {}

    get_plan(client)

    put_fin(client, cfg)
    get_printcode(client)

    put_print(client, cfg)
    # put_bzd(client, cfg)

    write_cfg(cfg)
    client.close()
