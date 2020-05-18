from tool import json_get, json_post, read_cfg, write_cfg, host_timedb
import tornado.httpclient
import dateutil.parser
import datetime


def time_iso(d, utc=False):
    try:
        v = dateutil.parser.parse(d)
        if utc:
            v += datetime.timedelta(hours=8)
        return v.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(e)
        return d


def get_host(m, n):
    host = "http://172.17.50.36:8088/mes-edi/packPackageService/%s?%s=" % (m, n)
    return host


def get_client():
    return None


def get_item(data, key):
    if key in data:
        return data[key]
    return None


def get_val(data, i):
    if data is not None and i < len(data):
        return str(data[i])
    return "none"


def get_line(d):
    if d == u'line-one':
        return u'PL1'

    return d


def get_data(client, tab, cfg):
    st = None
    if tab in cfg:
        st = cfg[tab]

    if st is None:
        data = json_post(client, host_timedb(), {
            "cmd": "get/first",
            "data": {
                "tab": tab,
                "orig": "true",
                "obj": "*"
                }
            })
    else:
        data = json_post(client, host_timedb(), {
            "cmd": "get/start",
            "data": {
                "tab": tab,
                "limit": 20,
                "start": st,
                "orig": "true",
                "nostart": "true",
                "obj": "*"
                }
            })

    if data is not None:
        if "start" in data and "end" in data and "data" in data:
            print(data["start"])
            print(data["end"])
            print(data["data"])

            cfg[tab] = data["end"]

            return data["data"]

    return None


def packscanner(client, cfg, dev, tab):
    data = get_data(client, tab, cfg)
    if data is None:
        return

    line = get_item(data, u'line')
    psn = get_item(data, u'psn')
    esn = get_item(data, u'esn')
    usn = get_item(data, u'usn')
    msn = get_item(data, u'msn')

    time = get_item(data, u'time')
    workstepno = get_item(data, u'step')
    stepwisestate = get_item(data, u'state')
    steprhythm = get_item(data, u'sbeat')
    intime = get_item(data, u'in')
    outtime = get_item(data, u'out')

    for i in range(len(time)):
        json_get(client, get_host("packscanner", "packscanner"), {
            "cmd": "put",
            "data": {
                "tags": {
                    "opcode": dev,
                    "line": get_line(get_val(line, i)),
                    "psn": get_val(psn, i),
                    "esn": get_val(esn, i),
                    "usn": get_val(usn, i),
                    "msn": get_val(msn, i)
                    },
                "fields": {
                    "workstepno": get_val(workstepno, i),
                    "stepwisestate": get_val(stepwisestate, i),
                    "steprhythm": get_val(steprhythm, i),
                    "intime": time_iso(get_val(intime, i)),
                    "outtime": time_iso(get_val(outtime, i)),
                    "uploadtime": time_iso(get_val(time, i), True)
                    }
                }
            })


def packtighten(client, cfg, dev, tab):
    data = get_data(client, tab, cfg)
    if data is None:
        return

    line = get_item(data, u'line')
    psn = get_item(data, u'psn')
    esn = get_item(data, u'esn')
    usn = get_item(data, u'usn')

    time = get_item(data, u'time')
    tightencode = get_item(data, u'gnum')
    tightprocedurecode = get_item(data, u'gset')
    sleevenumber = get_item(data, u'gsleeve')
    lasttorsion = get_item(data, u'gforce')
    lastangle = get_item(data, u'gangle')
    minangle = get_item(data, u'gamin')
    workstepno = get_item(data, u'step')
    stepwisestate = get_item(data, u'state')
    steprhythm = get_item(data, u'sbeat')
    stepstarttime = get_item(data, u'in')
    stependtime = get_item(data, u'out')
    maxtorsion = get_item(data, u'gfmax')
    maxangle = get_item(data, u'gamax')

    for i in range(len(time)):
        json_get(client, get_host("packtighten", "packtighten"), {
            "cmd": "put",
            "data": {
                "tags": {
                    "opcode": dev,
                    "line": get_line(get_val(line, i)),
                    "station": "A",
                    "psn": get_val(psn, i),
                    "esn": get_val(esn, i),
                    "usn": get_val(usn, i),
                    "msn": "none"
                    },
                "fields": {
                    "uploadtime": time_iso(get_val(time, i), True),
                    "tightencode": get_val(tightencode, i),
                    "tightprocedurecode": get_val(tightprocedurecode, i),
                    "sleevenumber": get_val(sleevenumber, i),
                    "lasttorsion": get_val(lasttorsion, i),
                    "lastangle": get_val(lastangle, i),
                    "minangle": get_val(minangle, i),
                    "workstepno": get_val(workstepno, i),
                    "stepwisestate": get_val(stepwisestate, i),
                    "steprhythm": get_val(steprhythm, i),
                    "stepstarttime": time_iso(get_val(stepstarttime, i)),
                    "stependtime": time_iso(get_val(stependtime, i)),
                    "maxtorsion": get_val(maxtorsion, i),
                    "maxangle": get_val(maxangle, i)
                    }
                }
            })


def post_packscanner(client, cfg):
    packscanner(client, cfg, "IPC_OP020_A", "IPC_OP020_A")
    packscanner(client, cfg, "IPC_OP030_A", "IPC_OP030_A")
    packscanner(client, cfg, "IPC_OP060_A", "IPC_OP060_A")
    packscanner(client, cfg, "IPC_OP070_A", "IPC_OP070_A")
    packscanner(client, cfg, "IPC_OP080_A", "IPC_OP080_A")
    packscanner(client, cfg, "IPC_OP090_A", "IPC_OP090_A")
    packscanner(client, cfg, "IPC_OP100_A", "IPC_OP100_A")
    packscanner(client, cfg, "IPC_OP110_A", "IPC_OP110_A")
    packscanner(client, cfg, "IPC_OP130_A", "IPC_OP130_A")
    packscanner(client, cfg, "IPC_OP150_A", "IPC_OP150_A")
    packscanner(client, cfg, "IPC_OP160_A", "IPC_OP160_A")
    packscanner(client, cfg, "IPC_OP220_A", "IPC_OP220_A")


def post_packtighten(client, cfg):
    packtighten(client, cfg, "IPC_OP020_B", "IPC_OP020_B")
    packtighten(client, cfg, "IPC_OP020_C", "IPC_OP020_C")
    packtighten(client, cfg, "IPC_OP030_B", "IPC_OP030_B")
    packtighten(client, cfg, "IPC_OP070_B", "IPC_OP070_B")
    packtighten(client, cfg, "IPC_OP070_C", "IPC_OP070_C")
    packtighten(client, cfg, "IPC_OP090_B", "IPC_OP090_B")
    packtighten(client, cfg, "IPC_OP100_B", "IPC_OP100_B")
    packtighten(client, cfg, "IPC_OP110_B", "IPC_OP110_B")
    packtighten(client, cfg, "IPC_OP110_C", "IPC_OP110_C")
    packtighten(client, cfg, "IPC_OP130_B", "IPC_OP130_B")
    packtighten(client, cfg, "IPC_OP150_B", "IPC_OP150_B")
    packtighten(client, cfg, "IPC_OP160_B", "IPC_OP160_B")
    packtighten(client, cfg, "IPC_OP160_C", "IPC_OP160_C")


def packleaktest(client, cfg, device):
    data = get_data(client, device, cfg)
    if data is None:
        return

    line = get_item(data, u'line')
    psn = get_item(data, u'psn')
    esn = get_item(data, u'esn')
    usn = get_item(data, u'usn')

    time = get_item(data, u'time')
    productmodel = get_item(data, u'Productmodel')
    testPressure = get_item(data, u'TestPressure')
    decayvalue = get_item(data, u'Decayvalue')
    testresult = get_item(data, u'Testresult')
    filltime = get_item(data, u'Fill')
    stabilizetime = get_item(data, u'Stabilize')
    testtime = get_item(data, u'Test')
    minpressure = get_item(data, u'MinimumPressure')
    targetpressure = get_item(data, u'TargetPressure')
    maxpressure = get_item(data, u'MaximumPressure')
    lowlimitrate = get_item(data, u'LowLimitRate')
    highlimitrate = get_item(data, u'HighLimitRate')
    intime = get_item(data, u'in')
    outtime = get_item(data, u'out')
    sbeat = get_item(data, u'sbeat')

    for i in range(len(time)):
        json_get(client, get_host("packleaktest", "packleaktest"), {
            "cmd": "put",
            "data": {
                "tags": {
                    "opcode": device,
                    "line": get_line(get_val(line, i)),
                    "psn": get_val(psn, i),
                    "esn": get_val(esn, i),
                    "usn": get_val(usn, i),
                    "msn": "none"
                    },
                "fields": {
                    "uploadtime": time_iso(get_val(time, i), True),
                    "productmodel": get_val(productmodel, i),
                    "testPressure": get_val(testPressure, i),
                    "decayvalue": get_val(decayvalue, i),
                    "testresult": get_val(testresult, i),
                    "filltime": get_val(filltime, i),
                    "stabilizetime": get_val(stabilizetime, i),
                    "testtime": get_val(testtime, i),
                    "minpressure": get_val(minpressure, i),
                    "targetpressure": get_val(targetpressure, i),
                    "maxpressure": get_val(maxpressure, i),
                    "lowlimitrate": get_val(lowlimitrate, i),
                    "highlimitrate": get_val(highlimitrate, i),
                    "intime": time_iso(get_val(intime, i)),
                    "outtime": time_iso(get_val(outtime, i)),
                    "sbeat": get_val(sbeat, i)
                    }
                }
            })


def post_packleaktest(client, cfg):
    packleaktest(client, cfg, "IPC_OP170")
    packleaktest(client, cfg, "IPC_OP180")


def post_packweight(client, cfg):
    data = get_data(client, "IPC_OP220_H", cfg)
    if data is None:
        return

    line = get_item(data, u'line')
    psn = get_item(data, u'psn')
    esn = get_item(data, u'esn')
    usn = get_item(data, u'usn')

    time = get_item(data, u'time')
    productweigh = get_item(data, u'weigh')
    lowweighset = get_item(data, u'weighdown')
    upweighset = get_item(data, u'weighup')
    testresult = get_item(data, u'state')
    intime = get_item(data, u'in')
    outtime = get_item(data, u'out')
    producerhythm = get_item(data, u'sbeat')

    for i in range(len(time)):
        json_get(client, get_host("packweight", "packweight"), {
            "cmd": "put",
            "data": {
                "tags": {
                    "line": get_line(get_val(line, i)),
                    "opcode": "IPC_OP220_H",
                    "psn": get_val(psn, i),
                    "esn": get_val(esn, i),
                    "usn": get_val(usn, i),
                    "msn": "none"
                    },
                "fields": {
                    "uploadtime": time_iso(get_val(time, i), True),
                    "productweigh": get_val(productweigh, i),
                    "lowweighset": get_val(lowweighset, i),
                    "upweighset": get_val(upweighset, i),
                    "testresult": get_val(testresult, i),
                    "intime": time_iso(get_val(intime, i)),
                    "outtime": time_iso(get_val(outtime, i)),
                    "producerhythm": get_val(producerhythm, i)
                    }
                }
            })


def do_post_cmd(cmd, n):
    client = tornado.httpclient.HTTPClient()

    cfg = read_cfg()
    if cfg is None:
        cfg = {}

    if cmd == "packscanner":
        post_packscanner(client, cfg)
    elif cmd == "packtighten":
        post_packtighten(client, cfg)
    elif cmd == "packleaktest":
        post_packleaktest(client, cfg)
    elif cmd == "packweight":
        post_packweight(client, cfg)

    client.close()

    write_cfg(cfg)


def do_get_cmd(cmd, client):
    None


def do_task():
    do_post_cmd("packscanner", None)
    do_post_cmd("packtighten", None)
    do_post_cmd("packleaktest", None)
    do_post_cmd("packweight", None)
