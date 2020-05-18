#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymqi
from tool import read_cfg, write_cfg, json_post, host_timedb, host_graphdb, host_graphdbget, host_real_task, \
    host_timedbput
import tornado
import tornado.httpclient
from xml.dom.minidom import Document
from readxml import xml2dict, readjson, xml2dict2
import time
import datetime
from map import get_kinident, get_bodyident


def connectmq_put(recv_mq, str1):
    host = recv_mq["ip"] + "(" + recv_mq["port"] + ")"

    qmgr = pymqi.QueueManager(None)
    qmgr.connect_tcp_client(recv_mq["recv_queue_manager"], pymqi.CD(), recv_mq["recv_channel"], host,
                            recv_mq["username"], recv_mq["password"])

    try:
        qmgr.connect_tcp_client(recv_mq["recv_queue_manager"], pymqi.CD(), recv_mq["recv_channel"], host,
                                recv_mq["username"], recv_mq["password"])


    except pymqi.MQMIError as e:
        if e.comp == pymqi.CMQC.MQCC_WARNING and e.reason == pymqi.CMQC.MQRC_ALREADY_CONNECTED:
            pass

    queue = pymqi.Queue(qmgr, recv_mq["recv_queue"])
    queue.put(str1)
    queue.close()
    qmgr.disconnect()


def connectmq_get(recv_mq):
    host = recv_mq["ip"] + "(" + recv_mq["port"] + ")"

    qmgr = pymqi.QueueManager(None)
    qmgr.connect_tcp_client(recv_mq["recv_queue_manager"], pymqi.CD(), recv_mq["recv_channel"], host,
                            recv_mq["username"], recv_mq["password"])

    try:
        qmgr.connect_tcp_client(recv_mq["recv_queue_manager"], pymqi.CD(), recv_mq["recv_channel"], host,
                                recv_mq["username"], recv_mq["password"])


    except pymqi.MQMIError as e:
        if e.comp == pymqi.CMQC.MQCC_WARNING and e.reason == pymqi.CMQC.MQRC_ALREADY_CONNECTED:
            pass

    queue = pymqi.Queue(qmgr, recv_mq["recv_queue"])
    str1 = queue.get()
    queue.close()
    qmgr.disconnect()
    return str1


def get_item(data, key):
    if key in data:
        return data[key]
    return None


def get_plan(client, tab, cfg, rec):
    st = None
    if tab in cfg:
        st = cfg[tab]
    tsn = rec["TSN"]
    sn = rec["CID"]
    pt = rec["PT"]
    big2 = rec["1G2"]
    b288 = rec["288"]
    gbt = rec["GBT"]
    sqr = rec["SQR"]
    prn = rec["PRN"]
    pstar = datetime.datetime.strptime(pt, "%Y%m%d%H%M%S")
    nedtime = datetime.timedelta(minutes=15)
    pen = (pstar + nedtime).strftime("%Y-%m-%dT%H:%M:%S")
    pstart = str(pstar.strftime("%Y-%m-%dT%H:%M:%S"))
    pend = str(pen)

    if st is None:
        info = json_post(client, host_real_task(), {
            "sn": sn,
            "tsn": tsn,
            "pstart": pstart,
            "pend": pstart,
            "pnum": 1,
            "info": [
                {"k": "ig2", "v": big2},
                {"k": "288", "v": b288},
                {"k": "gbt", "v": gbt},
                {"k": "sqr", "v": sqr},
                {"k": "prn", "v": prn},
                {"k": "tsn", "v": tsn},

            ]
        })
        if info == "Success":
            result = put_psn(client, sn)
            if result == "Success":
                return info


def get_taskinfo(client, tab, cfg, x):
    status = get_item(x, u"STATUS")
    sn = get_item(x, u"CID")
    tele = get_item(x, u"TELE")
    errtele = get_item(x, u"ERRTELE")

    info = json_post(client, host_timedb(), {
        "n": "task",
        "obj": "*",
        "opt": {
            "and": [
                {
                    "eq": "task",
                    "v": sn
                },
                {
                    "eq": "line",
                    "v": "line-one"
                }
            ]
        }
    })

    data = info["task"]["data"][0]
    if data["task"]:
        if sn == data["task"]:
            data.pop("task")
        else:
            print("ERROR: no such CID")
            return

    if data["line"]:
        data.pop("line")

    data["tele"] = tele
    data["errtele"] = errtele
    data["status"] = status

    result = json_post(client, host_timedbput(), {
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
    return result


def get_data(client, tab, cfg):
    st = None

    if tab in cfg:
        st = cfg[tab]

    if st is None:
        info = json_post(client, host_timedb(), {
            "n": tab,
            "obj": "*",
            "opt": {
                "limit": 1
            }
        })
    else:
        info = json_post(client, host_timedb(), {
            "n": tab,
            "obj": "*",
            "opt": {
                "and": [{
                    "ge": "time",
                    "v": st
                }],
                "limit": 20
            }
        })

    if info is not None:
        data1 = info[tab]
        if "start" in data1 and "end" in data1 and "data" in data1:
            print(data1["start"])
            print(data1["end"])
            print(data1["data"])

            cfg[tab] = data1["end"]
            # for data in data1["data"]:
            #     return data
            return data1["data"]
    return None


def get_bzd(client, tab, cfg, x, y):
    st = None
    if y in cfg:
        st = cfg[y]
    if st is None:
        info = json_post(client, host_timedb(), {
            "n": tab,
            "obj": "*",
            "opt": {
                "limit": 1
            }
        })

    else:
        info = json_post(client, host_timedb(), {
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


def put_stationdata(client, cfg, recv_mq):
    data = get_data(client, "stnstatus", cfg)
    if data is None:
        # logging.DEBUG("data=None")
        return

    doc = Document()
    env = doc.createElement("env:Envelope")
    doc.appendChild(env)
    env.setAttribute("xmlns:env", "http://pdps.in.audi.vwg/legacy_schema/20.7.3/envelope")

    herder = doc.createElement("Herder")
    env.appendChild(herder)

    sender = doc.createElement("Sender")
    herder.appendChild(sender)

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
    herder.appendChild(telegraminfo)
    sender_timestamp = get_item(data, u"opmode")
    telegraminfo.setAttribute("timestamp", sender_timestamp)
    sender_datatype = get_item(data, u"opmode")
    telegraminfo.setAttribute("datatype", sender_datatype)

    body = doc.createElement("Body")
    env.appendChild(body)

    batterdata = doc.createElement("BatteryData")
    body.appendChild(batterdata)
    cid = get_item(data, u"cid")
    batterdata.setAttribute("cid", cid)
    prt = get_item(data, u"teilnr.")
    batterdata.setAttribute("prt", prt)
    pt1 = get_item(data, u"gbt")
    batterdata.setAttribute("pt1", pt1)

    prc_sst = doc.createElement("PRC_SST")
    body.appendChild(prc_sst)

    In = doc.createElement("Entry")
    jobnumber = get_item(data, u"in")
    In_info = doc.createTextNode(jobnumber)
    In.appendChild(In_info)
    prc_sst.appendChild(In)

    Out = doc.createElement("Leave")
    textdescription = get_item(data, u"out")
    Out_info = doc.createTextNode(textdescription)
    Out.appendChild(Out_info)
    prc_sst.appendChild(Out)

    Palletnumber = doc.createElement("palletnumber")
    palletnumber = get_item(data, u"palletnumber")
    Palletnumber_info = doc.createTextNode(palletnumber)
    Palletnumber.appendChild(Palletnumber_info)
    prc_sst.appendChild(Palletnumber)

    Palletcycletimescount = doc.createElement("palletcycletimescount")
    palletcycletimescount = get_item(data, u"palletcycletimesCount")
    Palletcycletimescount_info = doc.createTextNode(palletcycletimescount)
    Palletcycletimescount.appendChild(Palletcycletimescount_info)
    prc_sst.appendChild(Palletcycletimescount)

    Pallettype = doc.createElement("pallettype")
    pallettype = get_item(data, u"pallettype_m_or_n")
    Pallettype_info = doc.createTextNode(pallettype)
    Pallettype.appendChild(Pallettype_info)
    prc_sst.appendChild(Pallettype)

    Lastworkstation = doc.createElement("lastworkstation")
    lastworkstation = get_item(data, u"lastworkstation")
    Lastworkstation_info = doc.createTextNode(lastworkstation)
    Lastworkstation.appendChild(Lastworkstation_info)
    prc_sst.appendChild(Lastworkstation)

    Palletloaded = doc.createElement("palletloaded")
    palletloaded = get_item(data, u"palletloaded")
    Palletloaded_info = doc.createTextNode(palletloaded)
    Palletloaded.appendChild(Palletloaded_info)
    prc_sst.appendChild(Palletloaded)

    Palletworkok = doc.createElement("palletworkok")
    palletworkok = get_item(data, u"palletworkok")
    Palletworkok_info = doc.createTextNode(palletworkok)
    Palletworkok.appendChild(Palletworkok_info)
    prc_sst.appendChild(Palletworkok)

    Palletworknok = doc.createElement("palletworknok")
    palletworknok = get_item(data, u"palletworknok")
    Palletworknok_info = doc.createTextNode(palletworknok)
    Palletworknok.appendChild(Palletworknok_info)
    prc_sst.appendChild(Palletworknok)

    Palletscrapped = doc.createElement("palletscrapped")
    palletscrapped = get_item(data, u"palletscrapped")
    Palletscrapped_info = doc.createTextNode(palletscrapped)
    Palletscrapped.appendChild(Palletscrapped_info)
    prc_sst.appendChild(Palletscrapped)

    Palletworkposition = doc.createElement("palletworkposition")
    palletworkposition = get_item(data, u"palletworkposition")
    Palletworkposition_info = doc.createTextNode(palletworkposition)
    Palletworkposition.appendChild(Palletworkposition_info)
    prc_sst.appendChild(Palletworkposition)

    Repairstatus = doc.createElement("repairstatus")
    repairstatus = get_item(data, u"repairstatus")
    Repairstatus_info = doc.createTextNode(repairstatus)
    Repairstatus.appendChild(Repairstatus_info)
    prc_sst.appendChild(Repairstatus)

    Repairtimescount = doc.createElement("repairtimescount")
    repairtimescount = get_item(data, u"repairtimescount")
    Repairtimescount_info = doc.createTextNode(repairtimescount)
    Repairtimescount.appendChild(Repairtimescount_info)
    prc_sst.appendChild(Repairtimescount)

    Ilchecktimescount = doc.createElement("ilchecktimescount")
    ilchecktimescount = get_item(data, u"ilchecktimescount")
    Ilchecktimescount_info = doc.createTextNode(ilchecktimescount)
    Ilchecktimescount.appendChild(Ilchecktimescount_info)
    prc_sst.appendChild(Ilchecktimescount)

    Eolchecktimescount = doc.createElement("eolchecktimescount")
    eolchecktimescount = get_item(data, u"eolchecktimescount")
    Eolchecktimescount_info = doc.createTextNode(eolchecktimescount)
    Eolchecktimescount.appendChild(Eolchecktimescount_info)
    prc_sst.appendChild(Eolchecktimescount)

    Dateandtimeid = doc.createElement("dateandtimeid")
    dateandtimeid = get_item(data, u"dateandtimeid")
    Dateandtimeid_info = doc.createTextNode(dateandtimeid)
    Dateandtimeid.appendChild(Dateandtimeid_info)
    prc_sst.appendChild(Dateandtimeid)

    Batteryid = doc.createElement("batteryid")
    batteryid = get_item(data, u"opmode")
    Batteryid_info = doc.createTextNode(batteryid)
    Batteryid.appendChild(Batteryid_info)
    prc_sst.appendChild(Batteryid)

    Bzd_batterycase = doc.createElement("bzd_batterycase")
    bzd_batterycase = get_item(data, u"bzdBatteryCase")
    Bzd_batterycase_info = doc.createTextNode(bzd_batterycase)
    Bzd_batterycase.appendChild(Bzd_batterycase_info)
    prc_sst.appendChild(Bzd_batterycase)

    Bzd_batterypack = doc.createElement("bzd_batterypack")
    bzd_batterypack = get_item(data, u"bzdBatteryPack")
    Bzd_batterypack_info = doc.createTextNode(bzd_batterypack)
    Bzd_batterypack.appendChild(Bzd_batterypack_info)
    prc_sst.appendChild(Bzd_batterypack)

    Teilnr = doc.createElement("teilnr.")
    teilnr = get_item(data, u"teilnr.")
    Teilnr_info = doc.createTextNode(teilnr)
    Teilnr.appendChild(Teilnr_info)
    prc_sst.appendChild(Teilnr)

    Cid = doc.createElement("cid")
    cid = get_item(data, u"cid")
    Cid_info = doc.createTextNode(cid)
    Cid.appendChild(Cid_info)
    prc_sst.appendChild(Cid)

    Gbt = doc.createElement("gbt")
    gbt = get_item(data, u"gbt")
    Gbt_info = doc.createTextNode(gbt)
    Cid.appendChild(Gbt_info)
    prc_sst.appendChild(Cid)

    Gapfillermodule1 = doc.createElement("gapfillermodule1")
    gapfillermodule1 = get_item(data, u"gapfillermodule1")
    Gapfillermodule1_info = doc.createTextNode(gapfillermodule1)
    Gapfillermodule1.appendChild(Gapfillermodule1_info)
    prc_sst.appendChild(Gapfillermodule1)

    Gapfillermodule2 = doc.createElement("gapfillermodule2")
    gapfillermodule2 = get_item(data, u"gapfillermodule2")
    Gapfillermodule2_info = doc.createTextNode(gapfillermodule2)
    Gapfillermodule2.appendChild(Gapfillermodule2_info)
    prc_sst.appendChild(Gapfillermodule2)

    Gapfillermodule3 = doc.createElement("gapfillermodule3")
    gapfillermodule3 = get_item(data, u"gapfillermodule3")
    Gapfillermodule3_info = doc.createTextNode(gapfillermodule3)
    Gapfillermodule3.appendChild(Gapfillermodule3_info)
    prc_sst.appendChild(Gapfillermodule3)

    Gapfillermodule4 = doc.createElement("gapfillermodule4")
    gapfillermodule4 = get_item(data, u"gapfillermodule4")
    Gapfillermodule4_info = doc.createTextNode(gapfillermodule4)
    Gapfillermodule4.appendChild(Gapfillermodule4_info)
    prc_sst.appendChild(Gapfillermodule4)

    Gapfillermodule5 = doc.createElement("gapfillermodule5")
    gapfillermodule5 = get_item(data, u"gapfillermodule5")
    Gapfillermodule5_info = doc.createTextNode(gapfillermodule5)
    Gapfillermodule5.appendChild(Gapfillermodule5_info)
    prc_sst.appendChild(Gapfillermodule5)

    Gapfillermodule6 = doc.createElement("gapfillermodule6")
    gapfillermodule6 = get_item(data, u"gapfillermodule6")
    Gapfillermodule6_info = doc.createTextNode(gapfillermodule6)
    Gapfillermodule6.appendChild(Gapfillermodule6_info)
    prc_sst.appendChild(Gapfillermodule6)

    Gapfillermodule7 = doc.createElement("gapfillermodule7")
    gapfillermodule7 = get_item(data, u"gapfillermodule7")
    Gapfillermodule7_info = doc.createTextNode(gapfillermodule7)
    Gapfillermodule7.appendChild(Gapfillermodule7_info)
    prc_sst.appendChild(Gapfillermodule7)

    Gapfillermodule8 = doc.createElement("gapfillermodule8")
    gapfillermodule8 = get_item(data, u"gapfillermodule8")
    Gapfillermodule8_info = doc.createTextNode(gapfillermodule8)
    Gapfillermodule8.appendChild(Gapfillermodule8_info)
    prc_sst.appendChild(Gapfillermodule8)

    Gapfillermodule9 = doc.createElement("gapfillermodule9")
    gapfillermodule9 = get_item(data, u"gapfillermodule9")
    Gapfillermodule9_info = doc.createTextNode(gapfillermodule9)
    Gapfillermodule9.appendChild(Gapfillermodule9_info)
    prc_sst.appendChild(Gapfillermodule9)

    Gapfillermodule10 = doc.createElement("gapfillermodule10")
    gapfillermodule10 = get_item(data, u"gapfillermodule10")
    Gapfillermodule10_info = doc.createTextNode(gapfillermodule10)
    Gapfillermodule10.appendChild(Gapfillermodule10_info)
    prc_sst.appendChild(Gapfillermodule10)

    Gapfillermodule11 = doc.createElement("gapfillermodule11")
    gapfillermodule11 = get_item(data, u"gapfillermodule11")
    Gapfillermodule11_info = doc.createTextNode(gapfillermodule11)
    Gapfillermodule11.appendChild(Gapfillermodule11_info)
    prc_sst.appendChild(Gapfillermodule11)

    Gapfillermodule12 = doc.createElement("gapfillermodule12")
    gapfillermodule12 = get_item(data, u"gapfillermodule12")
    Gapfillermodule12_info = doc.createTextNode(gapfillermodule12)
    Gapfillermodule12.appendChild(Gapfillermodule12_info)
    prc_sst.appendChild(Gapfillermodule12)

    Gapfillermodule13 = doc.createElement("gapfillermodule13")
    gapfillermodule13 = get_item(data, u"gapfillermodule13")
    Gapfillermodule13_info = doc.createTextNode(gapfillermodule13)
    Gapfillermodule13.appendChild(Gapfillermodule13_info)
    prc_sst.appendChild(Gapfillermodule13)

    Gapfillermodule14 = doc.createElement("gapfillermodule14")
    gapfillermodule14 = get_item(data, u"gapfillermodule14")
    Gapfillermodule14_info = doc.createTextNode(gapfillermodule14)
    Gapfillermodule14.appendChild(Gapfillermodule14_info)
    prc_sst.appendChild(Gapfillermodule14)

    Gapfillermodule15 = doc.createElement("gapfillermodule15")
    gapfillermodule15 = get_item(data, u"gapfillermodule15")
    Gapfillermodule15_info = doc.createTextNode(gapfillermodule15)
    Gapfillermodule15.appendChild(Gapfillermodule15_info)
    prc_sst.appendChild(Gapfillermodule15)

    Recipeversion = doc.createElement("recipeversion")
    recipeversion = get_item(data, u"recipeversion")
    Recipeversion_info = doc.createTextNode(recipeversion)
    Recipeversion.appendChild(Recipeversion_info)
    prc_sst.appendChild(Recipeversion)

    Bomversion = doc.createElement("bomversion")
    bomversion = get_item(data, u"bomversion")
    Bomversion_info = doc.createTextNode(bomversion)
    Bomversion.appendChild(Bomversion_info)
    prc_sst.appendChild(Bomversion)

    Work_ok = doc.createElement("work_ok")
    work_ok = get_item(data, u"work_ok")
    Work_ok_info = doc.createTextNode(work_ok)
    Work_ok.appendChild(Work_ok_info)
    prc_sst.appendChild(Work_ok)

    Work_nok = doc.createElement("work_nok")
    work_nok = get_item(data, u"work_nok")
    Work_nok_info = doc.createTextNode(work_nok)
    Work_nok.appendChild(Work_nok_info)
    prc_sst.appendChild(Work_nok)

    Workerdecisionok = doc.createElement("workerdecisionok")
    workerdecisionok = get_item(data, u"workerdecisionok")
    Workerdecisionok_info = doc.createTextNode(workerdecisionok)
    Workerdecisionok.appendChild(Workerdecisionok_info)
    prc_sst.appendChild(Workerdecisionok)

    Workerdecisionnok = doc.createElement("workerdecisionnok")
    workerdecisionnok = get_item(data, u"workerdecisionnok")
    Workerdecisionnok_info = doc.createTextNode(workerdecisionnok)
    Workerdecisionnok.appendChild(Workerdecisionnok_info)
    prc_sst.appendChild(Workerdecisionnok)

    xml = open("stnstatus.xml", "w")
    doc.writexml(xml, indent='\t', newl='\n', addindent='\t', encoding='gbk')
    xml.close()

    with open("stnstatus.xml", "rt") as xml:
        line = xml.read()
        print(line)

    connectmq_put(recv_mq, line)


def put_msndata(client, cfg, recv_mq):
    data = get_bzd(client, "msn", cfg, 1, "putbzd")
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

    bodyident = doc.createElement("BodyIdent")
    vechicledata.appendChild(bodyident)

    bodyident.setAttribute("plant", get_item(sss, "plant"))
    bodyident.setAttribute("checkdigit", get_item(sss, "checkdigit"))
    bodyident.setAttribute("productionyear", get_item(sss, "productionyear"))
    bodyident.setAttribute("id", get_item(sss, "bodyidentid"))

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
            msn = get_item(data, "msn")
            if msn is None:
                print("msn is None! msn:", msn)
                cfg["putbzd"] = get_item(data, u"time")
                return
            if len(msn) > 10:
                modul.setAttribute("serialnumber", msn)
            else:
                print("msn is empty! msn:", msn)
                cfg["putbzd"] = get_item(data, u"time")
                return
        else:
            result = get_bzd(client, "msn", cfg, 0, "putbzd")
            if result is None:
                return
            stat = get_item(result, u"esn")
            if sta == stat:
                msn = get_item(data, "msn")
                if len(msn) < 10:
                    break
                modul = doc.createElement("Module")
                moduledata.appendChild(modul)
                modul.setAttribute("status", "AV")
                modul.setAttribute("code", "KGG")
                if len(msn) > 10:
                    modul.setAttribute("serialnumber", msn)
                    cfg["putbzd"] = get_item(result, u"time")
                else:
                    print("msn is empty! msn:", msn)
                    break
            else:
                break

    xml = open("msn.xml", "w")
    doc.writexml(xml, indent='\t', newl='\n', addindent='\t', encoding='gbk')
    xml.close()

    with open("msn.xml", "rt") as xml:
        line = xml.read()
        print(line)
    connectmq_put(recv_mq, line)


def put_msndata2(client, cfg, recv_mq):
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

    bodyident.setAttribute("plant", get_item(sss, "plant"))
    bodyident.setAttribute("checkdigit", get_item(sss, "checkdigit"))
    bodyident.setAttribute("productionyear", get_item(sss, "productionyear"))
    bodyident.setAttribute("id", get_item(sss, "bodyidentid"))

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
            msn = get_item(data, "dmcdata")
            if msn is None:
                print("msn is None! msn:", msn)
                cfg["putbzd2"] = get_item(data, u"time")
                return
            if len(msn) > 10:
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
                msn = get_item(data, "dmcdata")
                if len(msn) < 10:
                    break
                modul = doc.createElement("Module")
                moduledata.appendChild(modul)
                modul.setAttribute("status", "AV")
                modul.setAttribute("code", "KGG")
                if len(msn) > 10:
                    modul.setAttribute("serialnumber", msn)
                    cfg["putbzd2"] = get_item(result, u"time")
                else:
                    print("msn is empty! msn:", msn)
                    cfg["putbzd2"] = get_item(result, u"time")
                    break
            else:
                break

    xml = open("msn.xml", "w")
    doc.writexml(xml, indent='\t', newl='\n', addindent='\t', encoding='gbk')
    xml.close()

    with open("msn.xml", "rt") as xml:
        line = xml.read()
        print(line)
    connectmq_put(recv_mq, line)


def get_snfinsh(client, cfg):
    st = None
    if "snfinsh" in cfg:
        st = cfg["snfinsh"]
    if st is None:
        info = json_post(client, host_timedb(), {
            "n": "stnstatus",
            "obj": "*",
            "opt": {
                "limit": 1,
                "and": [
                    {"eq": "wsn",
                     "v": "af450"
                     }]
            }
        })
    else:
        info = json_post(client, host_timedb(), {
            "n": "stnstatus",
            "obj": "*",
            "opt": {
                "limit": 1,
                "and": [
                    {"eq": "wsn",
                     "v": "af450"
                     },
                    {"gt": "time",
                     "v": st
                     }]
            }
        })
    print(info)
    if info is not None:
        data1 = info["stnstatus"]
        if "start" in data1 and "end" in data1 and "data" in data1:
            cfg["snfinsh"] = data1["end"]
            return data1["data"][0]
    return None

def put_snfinsh(client, cfg, recv_mq):
    data = get_snfinsh(client, cfg)
    if data is None:
        return
    doc = Document()
    env = doc.createElement("env:Envelope")
    doc.appendChild(env)
    env.setAttribute("xmlns:prc_sst", "http://xmldefs.vw-group.com/KAP/station/V2.0/prc_sst")
    env.setAttribute("xmlns:env", "http://www.audi.de/FIS")
    env.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    env.setAttribute("xsi:schemaLocation",
                     "http://www.audi.de/FIS C:\Aktuell\pdps_xml_schema_prebuild_v.6_0_19_Freigabe_11.02.2008\envelope.xsd")

    herder = doc.createElement("Header")
    env.appendChild(herder)

    sender = doc.createElement("Sender")
    herder.appendChild(sender)

    location = doc.createElement("Location")
    sender.appendChild(location)
    location.setAttribute("assembly_cycle", "501")
    location.setAttribute("assembly_line", "MLA")
    location.setAttribute("assembly_subline", "N")
    location.setAttribute("plant", "C4")
    location.setAttribute("plant_segment", "ASSEMBLY")

    device = doc.createElement("Device")
    sender.appendChild(device)
    device.setAttribute("operating_state", "AUTOMATICMODE")
    device.setAttribute("type", "Leitrechner")
    device.setAttribute("name", "CA431001")
    device.setAttribute("model", "ES45")
    device.setAttribute("manufacturer", "IBM")
    device.setAttribute("macaddress", "AA-00-04-00-3B-0D")
    device.setAttribute("ipaddress", "10.212.120.14")
    device.setAttribute("hostname", "MESAF450")

    application = doc.createElement("Application")
    sender.appendChild(application)
    application.setAttribute("name", "MMS")
    application.setAttribute("manufacturer", "Kon-Cept")
    application.setAttribute("uri", " ")
    application.setAttribute("majorversion", "1")
    application.setAttribute("minorversion", "0")

    telegraminfo = doc.createElement("Telegraminfo")
    herder.appendChild(telegraminfo)
    telegraminfo.setAttribute("majorversion", "1")
    telegraminfo.setAttribute("minorversion", "0")
    telegraminfo.setAttribute("dataguid", " ")
    now_time = datetime.datetime.now()
    Tim = datetime.datetime.strftime(now_time, '%Y-%m-%dT%H:%M:%S')
    tim = str(Tim)
    telegraminfo.setAttribute("timestamp", tim)
    telegraminfo.setAttribute("datatype", "MODULES")

    communicationtype = doc.createElement("Communicationtype")
    herder.appendChild(communicationtype)
    communicationtype.setAttribute("type", "SEND")

    body = doc.createElement("Body")
    env.appendChild(body)

    VehicleData = doc.createElement("VehicleData")
    body.appendChild(VehicleData)

    cid = get_item(data, u"psn")
    sss = get_bodyident(cid)

    BodyIdent = doc.createElement("BodyIdent")
    VehicleData.appendChild(BodyIdent)
    BodyIdent.setAttribute("plant", get_item(sss, "plant"))
    BodyIdent.setAttribute("checkdigit", get_item(sss, "checkdigit"))
    BodyIdent.setAttribute("productionyear", get_item(sss, "productionyear"))
    BodyIdent.setAttribute("id", get_item(sss, "bodyidentid"))

    xxx = get_kinident(cid)

    KINIdent = doc.createElement("KINIdent")
    VehicleData.appendChild(KINIdent)
    KINIdent.setAttribute("plant", get_item(xxx, "plant"))
    KINIdent.setAttribute("componentnumber", get_item(xxx, "componentnumber"))
    KINIdent.setAttribute("productionyear", get_item(xxx, "productionyear"))
    KINIdent.setAttribute("id", get_item(xxx, "bodyidentid"))
    KINIdent.setAttribute("serial", " ")
    KINIdent.setAttribute("checkdigit", get_item(xxx, "checkdigit"))

    Data = doc.createElement("Data")
    body.appendChild(Data)

    Raw = doc.createElement("Raw")
    Data.appendChild(Raw)
    CID = get_item(data, u"psn")
    intim = get_item(data, u"in")
    outtim = get_item(data, u"out")
    IN = datetime.datetime.strptime(intim, "%Y-%m-%d %H:%M:%S").strftime("%Y%m%d%H%M%S")
    OUT = datetime.datetime.strptime(outtim, "%Y-%m-%d %H:%M:%S").strftime("%Y%m%d%H%M%S")
    result = {}
    result["CID"] = CID
    result["IN"] = IN
    result["OUT"] = OUT
    for ss in result:
        Detail = doc.createElement("Detail")
        Raw.appendChild(Detail)
        Key = doc.createElement("Key")
        key_info = doc.createTextNode(str(ss))
        Key.appendChild(key_info)
        Detail.appendChild(Key)
        Value = doc.createElement("Value")
        value = get_item(result, str(ss))
        value_info = doc.createTextNode(str(value))
        Value.appendChild(value_info)
        Detail.appendChild(Value)

    xml = open("snfinsh.xml", "w")
    doc.writexml(xml, indent='\t', newl='\n', addindent='\t', encoding='gbk')
    xml.close()

    with open("snfinsh.xml", "rt") as xml:
        line = xml.read()
        print(line)
    connectmq_put({
            "ip": "10.232.129.54",
            "port": "1416",
            "username": "mqm",
            "password": "mqm",

            "recv_queue_manager": "VMFSMESMQTEST1",
            "recv_channel": "CLI.PD.MES.MEB.1",
            "recv_queue": "MES.MEB.ASSEMBLE.START",
        },line)
    connectmq_put(recv_mq, line)


def get_getplan(client, cfg, recv_mq):
    rec = connectmq_get(recv_mq)
    print(rec)
    json = xml2dict(rec)
    a = readjson(json)

    x = a[0]
    y = a[1]

    result = get_plan(client, "sn", cfg, x)

    if result == "Success":
        print("writer success")
        put_getplan(x, y)


def put_emergency_print(client, cfg):
    recv_mq = {
        "ip": "10.232.129.54",
        "port": "1416",
        "username": "mqm",
        "password": "mqm",

        "recv_queue_manager": "VMFSMESMQTEST1",
        "recv_channel": "CLI.PD.MES.MEB.1",
        "recv_queue": "MES.MEB.ASSEMBLE.CERTIFICATE.FAST.REQUEST",
    }

    data = get_snfinsh(client, cfg)
    if data is None:
        return
    doc = Document()
    env = doc.createElement("env:Envelope")
    doc.appendChild(env)
    env.setAttribute("xmlns:prc_sst", "http://xmldefs.vw-group.com/KAP/station/V2.0/prc_sst")
    env.setAttribute("xmlns:env", "http://www.audi.de/FIS")
    env.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    env.setAttribute("xsi:schemaLocation",
                     "http://www.audi.de/FIS C:\Aktuell\pdps_xml_schema_prebuild_v.6_0_19_Freigabe_11.02.2008\envelope.xsd")

    herder = doc.createElement("Header")
    env.appendChild(herder)

    sender = doc.createElement("Sender")
    herder.appendChild(sender)

    location = doc.createElement("Location")
    sender.appendChild(location)
    location.setAttribute("assembly_cycle", "4501")
    location.setAttribute("assembly_line", "MLA")
    location.setAttribute("assembly_subline", "N")
    location.setAttribute("plant", "C4")
    location.setAttribute("plant_segment", "ASSEMBLY")

    device = doc.createElement("Device")
    sender.appendChild(device)
    device.setAttribute("operating_state", "AUTOMATICMODE")
    device.setAttribute("type", "Leitrechner")
    device.setAttribute("name", "CA431001")
    device.setAttribute("model", "ES45")
    device.setAttribute("manufacturer", "IBM")
    device.setAttribute("macaddress", "AA-00-04-00-3B-0D")
    device.setAttribute("ipaddress", "10.212.120.14")
    device.setAttribute("hostname", "MESAF450")

    application = doc.createElement("Application")
    sender.appendChild(application)
    application.setAttribute("name", "MMS")
    application.setAttribute("manufacturer", "Kon-Cept")
    application.setAttribute("uri", " ")
    application.setAttribute("majorversion", "1")
    application.setAttribute("minorversion", "0")

    telegraminfo = doc.createElement("Telegraminfo")
    herder.appendChild(telegraminfo)
    telegraminfo.setAttribute("majorversion", "1")
    telegraminfo.setAttribute("minorversion", "0")
    telegraminfo.setAttribute("dataguid", " ")
    now_time = datetime.datetime.now()
    Tim = datetime.datetime.strftime(now_time, '%Y-%m-%dT%H:%M:%S')
    tim = str(Tim)
    telegraminfo.setAttribute("timestamp", tim)
    telegraminfo.setAttribute("datatype", "MODULES")

    communicationtype = doc.createElement("Communicationtype")
    herder.appendChild(communicationtype)
    communicationtype.setAttribute("type", "REQUEST")

    body = doc.createElement("Body")
    env.appendChild(body)

    VehicleData = doc.createElement("VehicleData")
    body.appendChild(VehicleData)

    BodyIdent = doc.createElement("BodyIdent")
    VehicleData.appendChild(BodyIdent)
    BodyIdent.setAttribute("plant", "C4")
    BodyIdent.setAttribute("id", "1128001")
    Tim = datetime.datetime.strftime(now_time, '%Y')
    year = str(Tim)
    BodyIdent.setAttribute("productionyear", year)
    BodyIdent.setAttribute("checkdigit", "9")

    KINIdent = doc.createElement("KINIdent")
    VehicleData.appendChild(KINIdent)
    KINIdent.setAttribute("plant", "C4")
    KINIdent.setAttribute("componentnumber", "20")
    KINIdent.setAttribute("productionyear", "19")
    KINIdent.setAttribute("id", "1128001")
    KINIdent.setAttribute("serial", " ")
    KINIdent.setAttribute("checkdigit", "9")

    Data = doc.createElement("Data")
    body.appendChild(Data)

    Raw = doc.createElement("Raw")
    Data.appendChild(Raw)
    CID = get_item(data, u"psn")

    Detail = doc.createElement("Detail")
    Raw.appendChild(Detail)
    Key = doc.createElement("Key")
    key_info = doc.createTextNode("CID")
    Key.appendChild(key_info)
    Detail.appendChild(Key)
    Value = doc.createElement("Value")
    value_info = doc.createTextNode(str(CID))
    Value.appendChild(value_info)
    Detail.appendChild(Value)

    xml = open("eme_print.xml", "w")
    doc.writexml(xml, indent='\t', newl='\n', addindent='\t', encoding='gbk')
    xml.close()

    with open("eme_print.xml", "rt") as xml:
        line = xml.read()
        print(line)
    connectmq_put(recv_mq, line)
    print("emergency put success!")


def get_getprintstr(client, cfg, recv_mq):
    rec = connectmq_get(recv_mq)
    print(rec)
    json = xml2dict(rec)
    # print(json)
    a = readjson(json)

    x = a[0]
    y = a[1]
    result = get_taskinfo(client, "task", cfg, x)
    if result == "Success":
        print("writer print success")


def put_psn(client, sn):
    info = json_post(client, host_graphdbget(), {
        "n": "task",
        "obj": "uid,sn",
        "opt": {
            "and": [{
                "eq": "sn",
                "v": sn
            }]
        }
    })
    uid = info[0]["uid"]
    result = json_post(client, host_graphdb(), {
        "a": [{
            "v": [[{
                "k": "sn",
                "v": sn
            }]],
            "u": uid,
            "n": "pcode"
        }]
    })
    if result == "Success":
        return result
    else:
        return "Error"


def put_getplan(x, y):
    recv_mq = {
        "ip": "10.232.129.54",
        "port": "1416",
        "username": "mqm",
        "password": "mqm",
        "recv_queue_manager": "VMFSMESMQTEST1",
        "recv_channel": "CLI.PD.MES.MEB.1",
        "recv_queue": "MES.MEB.ASSEMBLE.PLAN.ACK",
    }

    now_time = datetime.datetime.now()
    Tim = datetime.datetime.strftime(now_time, '%Y%m%d%H%M%S')
    tim = str(Tim)
    a = [{
        "Key": "STA",
        "Value": "X000"
    },
        {
            "Key": "TIM",
            "Value": tim
        }]
    y["Body"]["Data"]["Raw"] = a
    x = str(y)
    connectmq_put(recv_mq, x)
    print(x)


def do_post_cmd(cmd, n):
    client = tornado.httpclient.HTTPClient()
    cfg = read_cfg()

    if cfg is None:
        cfg = {}

    if cmd == "putfinsh":
        recv_mq = {
            "ip": "10.232.129.54",
            "port": "1416",
            "username": "mqm",
            "password": "mqm",

            "recv_queue_manager": "VMFSMESMQTEST1",
            "recv_channel": "CLI.PD.MES.MEB.1",
            "recv_queue": "MES.MEB.ASSEMBLE.FINISH",
        }
        put_snfinsh(client, cfg, recv_mq)

    if cmd == "emergency":
        ### emergency user ###
        put_emergency_print(client, cfg)

    if cmd == "stnstatus":
        recv_mq = {
            "ip": "10.232.129.54",
            "port": "1416",
            "username": "mqm",
            "password": "mqm",

            "recv_queue_manager": "VMFSMESMQTEST1",
            "recv_channel": "CLI.PD.MES.MEB.1",
            "recv_queue": "MES.MEB.TEST.SENSOR",
        }
        put_stationdata(client, cfg, recv_mq)

    if cmd == "putmsn":
        recv_mq = {
            "ip": "10.232.129.54",
            "port": "1416",
            "username": "mqm",
            "password": "mqm",

            "recv_queue_manager": "VMFSMESMQTEST1",
            "recv_channel": "CLI.PD.MES.MEB.1",
            "recv_queue": "MES.MEB.ASSEMBLE.RESULT",
        }
        put_msndata(client, cfg, recv_mq)

    if cmd == "putmsn2":
        recv_mq = {
            "ip": "10.232.129.54",
            "port": "1416",
            "username": "mqm",
            "password": "mqm",

            "recv_queue_manager": "VMFSMESMQTEST1",
            "recv_channel": "CLI.PD.MES.MEB.1",
            "recv_queue": "MES.MEB.ASSEMBLE.RESULT",
        }
        put_msndata2(client, cfg, recv_mq)

    client.close()

    write_cfg(cfg)


def do_get_cmd(cmd, n):
    client = tornado.httpclient.HTTPClient()
    cfg = read_cfg()

    if cfg is None:
        cfg = {}

    if cmd == "getplan":
        recv_mq = {
            "ip": "10.232.129.54",
            "port": "1416",
            "username": "mqm",
            "password": "mqm",

            "recv_queue_manager": "VMFSMESMQTEST1",
            "recv_channel": "CLI.PD.MES.MEB.1",
            "recv_queue": "MES.MEB.ASSEMBLE.PLAN.SEND",
        }
        get_getplan(client, cfg, recv_mq)

    if cmd == "getprintstr":
        recv_mq = {
            "ip": "10.232.129.54",
            "port": "1416",
            "username": "mqm",
            "password": "mqm",

            "recv_queue_manager": "VMFSMESMQTEST1",
            "recv_channel": "CLI.PD.MES.MEB.1",
            "recv_queue": "MES.MEB.ASSEMBLE.CERTIFICATE.FAST.RESPONSE",
        }
        get_getprintstr(client, cfg, recv_mq)


def do_task():
    now_time = datetime.datetime.now()
    Tim = datetime.datetime.strftime(now_time, '%Y-%m-%d %H:%M:%S')
    print(Tim)

    # do_post_cmd("putfinsh", None)

    do_get_cmd("getprintstr", None)
    # do_post_cmd("stnstatus",None)
    #try:
    #   do_post_cmd("putfinsh", None)
    #except Exception as e:
    #   print("putfinsh error:", e)
    #   pass
    # do_post_cmd("emergency",None)
    # do_post_cmd("putmsn2", None)
    #try:
    #    do_post_cmd("putmsn2", None)
    #except Exception as e:
    #    print("putmsn2 error:", e)
    #    pass

    # try:
    #     do_get_cmd("getplan", None)
    # except Exception as e:
    #     print("getplan error:",e)
    #     pass
    #
    #     #do_post_cmd("putmsn", None)
    #
    # try:
    #     do_get_cmd("getprintstr", None)
    # except Exception as e:
    #     print("getprintstr error:",e)
    #     pass


do_task()

