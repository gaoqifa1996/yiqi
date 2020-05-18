import zeep
from zeep.cache import SqliteCache
from zeep.transports import Transport


def get_client():
    wsdl = 'http://24961z084i.zicp.vip/prj-bqzj/ws/routeMesInterfaceService?wsdl'
    transport = Transport(cache=SqliteCache())
    client = zeep.Client(wsdl=wsdl, transport=transport)
    return client


def post_resistance(client):
    ret = client.service.getResistance(
            arg0=[{
                "inRes": "0",
                "materialCode": "7020000147",
                "negToShelllmp": "0",
                "openCircuitVolt": "0",
                "operator": "user1",
                "optime": "2019-03-04 21:12:00",
                "posToShellDCW": "0",
                "posToShelllmp": "0",
                "productSN": "00000660006659199900YHCT001",
                "result": "PASS",
                "stcode": "ST10",
                "stepNo": "61",
                "wonum": "SC20180207001",
                "workcenterCode": "PL71"
                }]
            )
    return ret


def post_dynamiccheck(client):
    ret = client.service.getDynamiccheck(
            arg0=[{
                "hiVoltage": "11",
                "jueYuan": "11",
                "materialCode": "11",
                "maxResistance": "11",
                "maxVoltage": "11",
                "minResistance": "11",
                "minVoltage": "11",
                "operator": "aaa",
                "optime": "2019-03-04 21:12:00",
                "productSN": "00000660006659199900YHCT001",
                "resistance": "11",
                "result": "PASS",
                "stcode": "ST10",
                "stepNo": "1",
                "voltage": "11",
                "wonum": "SC20180207001",
                "workcenterCode": "PL71"
                }]
            )
    return ret


def post_screw(client):
    ret = client.service.getScrew(
            arg0=[{
                "controlID": "11",
                "deviceID": "11",
                "finalAngle": "11",
                "finalTorque": "11",
                "materialCode": "7020000147",
                "maxAngle": "11",
                "maxTorque": "11",
                "minAngle": "11",
                "minTorque": "11",
                "operator": "aaa",
                "optime": "2019-03-04 21:12:00",
                "productSN": "00000660006659199900YHCT001",
                "pset": "11",
                "psetTool": "11",
                "result": "PASS",
                "stcode": "ST10",
                "stepNo": "1",
                "wonum": "SC20180207001",
                "workcenterCode": "PL71"
                }]
            )
    print(ret)
    return ret


def post_leak(client):
    ret = client.service.getWaterCooledLeakTesting(
            arg0=[{
                "keepPresVal": "11",
                "materialCode": "7020000147",
                "operator": "aaa",
                "optime": "2019-06-26 11:41:23",
                "productSN": "00000660006659199900YHCT001",
                "ratetNum": "11",
                "ratetVal": "11",
                "result": "PASS",
                "stcode": "ST10",
                "stepNo": "1",
                "testConut": "11",
                "testDate": "2019-06-26 11:41:23",
                "testPressure": "11",
                "testProID": "11",
                "testRate": "11",
                "testTemp": "11",
                "wonum": "SC20180207001",
                "workcenterCode": "PL71"
                }]
            )
    return ret


def post_order(client):
    ret = client.service.getWorkOrderState(
            arg0=[{
                "inStcode": "2",
                "materialCode": "E00101444",
                "optime": "2019-03-04 21:12:00",
                "outStCode": "0",
                "productSN": "101A0LS000000196M0000008",
                "state": "1",
                "wonum": "HCC0620_01",
                "workcenterCode": "PL71"
                }]
            )
    return ret


def post_cross(client):
    ret = client.service.snCrosspointInformation(
            arg0=[{
                "inoptime": "2019-03-04 20:12:00",
                "materialCode": "7020000147",
                "operator": "aaa",
                "outoptime": "2019-03-04 21:12:00",
                "productSN": "00000660006659199900YHCT001",
                "stcode": "ST10",
                "wonum": "SC20180207001",
                "workcenterCode": "PL71"
                }]
            )
    return ret


def post_bom(client):
    ret = client.service.snAssemblyMaterial(
            arg0=[
                {
                    "materialBarcode": "aaaaa",
                    "materialCode": "7020000147",
                    "operator": "abc",
                    "optime": "2019-06-26 11:41:23",
                    "productSN": "00000660006659199900YHCT001",
                    "result": "PASS",
                    "stcode": "ST10",
                    "stepNo": "1",
                    "wonum": "SC20180207001",
                    "workcenterCode": "PL71"
                    },
                {
                    "materialBarcode": "aaaaa",
                    "materialCode": "8020000147",
                    "operator": "abc",
                    "optime": "2019-06-26 11:41:23",
                    "productSN": "00000660006659199900YHCT001",
                    "result": "PASS",
                    "stcode": "ST10",
                    "stepNo": "1",
                    "wonum": "SC20180207001",
                    "workcenterCode": "PL71"
                    }
                ]
            )
    return ret


def get_plan(client):
    ret = client.service.planOrderSendToRouteMes()
    return ret


def do_post_cmd(cmd, client):
    if cmd == "dynamiccheck":
        ret = post_dynamiccheck(client)
        return {"ret": ret["uploadResult"], "error": ret["reason"]}
    elif cmd == "resistance":
        ret = post_resistance(client)
        return {"ret": ret["uploadResult"], "error": ret["reason"]}
    elif cmd == "screw":
        ret = post_screw(client)
        return {"ret": ret["uploadResult"], "error": ret["reason"]}
    elif cmd == "leak":
        ret = post_leak(client)
        return {"ret": ret["uploadResult"], "error": ret["reason"]}
    elif cmd == "order":
        ret = post_order(client)
        return {"ret": ret["uploadResult"], "error": ret["reason"]}
    elif cmd == "cross":
        ret = post_cross(client)
        return {"ret": ret["uploadResult"], "error": ret["reason"]}
    elif cmd == "bom":
        ret = post_bom(client)
        return {"ret": ret["uploadResult"], "error": ret["reason"]}

    return {"ret": "Success", "error": ""}


def do_get_cmd(cmd, client):
    if cmd == "plan":
        ret = get_plan(client)
        return ret


def do_task():
    print("beiqixxxxx")
