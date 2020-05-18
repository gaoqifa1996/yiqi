from xml.dom.minidom import Document
import time
import datetime
from map import get_kinident, get_bodyident
from tool import read_cfg, write_cfg, json_post, host_timedb, host_graphdb, host_graphdbget, host_real_task, \
    host_timedbput
import tornado
import tornado.httpclient

def get_item(data, key):
    if key in data:
        return data[key]
    return None

def get_bzd(client, tab, cfg, x, y):
    st = None
    if y in cfg:
        st = cfg[y]
    if st is None:
        info = json_post(client, "http://47.96.151.120/timedb/get", {
            "n": tab,
            "obj": "*",
            "opt": {
                "limit": 1
            }
        })

    else:
        info = json_post(client, "http://47.96.151.120/timedb/get", {
            "n": tab,
            "obj": "*",
            "opt": {
                "and": [{
                    "gt": "time",
                    "v": st
                }],
                "limit": 1
            }
        })
    if info is not None:
        data1 = info[tab]
        if "start" in data1 and "end" in data1 and "data" in data1:
            print(data1["start"])
            print(data1["end"])
            print(data1["data"])
            if x == 1:
                cfg[y] = data1["end"]
            return data1["data"][0]
    return None

def put_msndata2(client, cfg):
    data = get_bzd(client, "hioki", cfg, 1, "putbzd2")
    if data is None:
        return

    doc = Document()
    env = doc.createElement("env:Envelope")
    doc.appendChild(env)
    env.setAttribute("xmlns:env", "http://pdps.in.audi.vwg/legacy_schema/20.7.3/envelope")
    env.setAttribute("xmlns:com", "http://pdps.in.audi.vwg/legacy_schema/20.7.3-2018.01/common")
    env.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    env.setAttribute("xsi:schemaLocation", "http://pdps.in.audi.vwg/legacy_schema/20.7.3-2018.01/envelope envelope.xsd")

    header = doc.createElement("Header")
    env.appendChild(header)

    sender = doc.createElement("Sender")
    header.appendChild(sender)

    location = doc.createElement("Location")
    sender.appendChild(location)

    sender_assembly_cycle = get_item(data, u"assembly_cycle")
    location.setAttribute("assembly_cycle", sender_assembly_cycle)
    location.setAttribute("assembly_line", "MES Battery Assembly Line")
    location.setAttribute("assembly_subline", "1")
    location.setAttribute("plant", "C4")
    location.setAttribute("plant_segment", "Battery")

    device = doc.createElement("Device")
    sender.appendChild(device)
    sender_hostname = get_item(data, u"hostname")
    device.setAttribute("hostname", sender_hostname)
    sender_manufacturer = get_item(data, u"manufacturer")
    device.setAttribute("manufacturer", sender_manufacturer)
    sender_type = get_item(data, u"type")
    device.setAttribute("type", sender_type)
    sender_opmode = get_item(data, u"opmode")
    device.setAttribute("opmode", sender_opmode)

    telegraminfo = doc.createElement("Telegraminfo")
    header.appendChild(telegraminfo)
    sender_timestamp = get_item(data, u"opmode")
    telegraminfo.setAttribute("timestamp", sender_timestamp)
    sender_datatype = get_item(data, u"opmode")
    telegraminfo.setAttribute("datatype", sender_datatype)

    communicationtype = doc.createElement("Communicationtype")
    header.appendChild(communicationtype)
    communicationtype.setAttribute("type", "SEND_DATA")

    body = doc.createElement("Body")
    env.appendChild(body)

    vechicledata = doc.createElement("VehicleData")
    body.appendChild(vechicledata)

    cid = get_item(data, u"psn")
    sss = get_bodyident(cid)
    print(sss)
    bodyident = doc.createElement("BodyIdent")
    vechicledata.appendChild(bodyident)

    bodyident.setAttribute("plant", get_item(data, "plant"))
    bodyident.setAttribute("checkdigit", get_item(data, "checkdigit"))
    bodyident.setAttribute("productionyear", get_item(data, "productionyear"))
    bodyident.setAttribute("id", get_item(data, "bodyidentid"))

    datadata = doc.createElement("Data")
    body.appendChild(datadata)

    moduledata = doc.createElement("ModuleData")
    datadata.appendChild(moduledata)
    sta = get_item(data, u"esn")
    for i in range(20):
        if i == 0:
            modul = doc.createElement("Module")
            moduledata.appendChild(modul)
            modul.setAttribute("status", "AV")
            modul.setAttribute("code", "KGG")
            msn = get_item(data, "psn")
            if msn is None:
                print("msn is None! msn:", msn)
                cfg["putbzd2"] = get_item(data, u"time")
                return
            if len(msn) > 1:
                modul.setAttribute("serialnumber", msn)
            else:
                print("msn is empty! msn:", msn)
                cfg["putbzd2"] = get_item(data, u"time")
                return
        else:
            result = get_bzd(client, "hioki", cfg, 0, "putbzd2")
            if result is None:
                return
            stat = get_item(result, u"esn")
            if sta == stat:
                msn = get_item(data, "psn")
                if len(msn) < 1:
                    break
                modul = doc.createElement("Module")
                moduledata.appendChild(modul)
                modul.setAttribute("status", "AV")
                modul.setAttribute("code", "KGG")
                if len(msn) > 1:
                    modul.setAttribute("serialnumber", msn)
                    cfg["putbzd2"] = get_item(result, u"time")
                else:
                    print("msn is empty! msn:", msn)
                    cfg["putbzd2"] = get_item(result, u"time")
                    break
            else:
                break

    xml = open("msn2.xml", "w")
    doc.writexml(xml, indent='\t', newl='\n', addindent='\t', encoding='gbk')
    xml.close()
    with open("msn2.xml", "rt") as xml:
        line = xml.read()
        print(line)


client = tornado.httpclient.HTTPClient()
cfg ={}
put_msndata2(client,cfg)