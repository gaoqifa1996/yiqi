import pymqi
from tool import read_cfg,write_cfg,json_post,host_timedb,host_graphdb,host_graphdbget
import tornado
from xml.dom.minidom import Document
from readxml import xml2dict,readjson
import time
import datetime

def connect(recv_mq):
    qmgr = pymqi.connect(recv_mq["recv_queue_manager"], recv_mq["recv_channel"], recv_mq["ip"] + "(" + str(recv_mq["port"]) + ")","username","password")
    global queue
    queue = pymqi.Queue(qmgr, recv_mq["recv_queue"])

def get_item(data, key):
    if key in data:
        return data[key]
    return None

def get_plan(client,tab,cfg,rec):
    st = None

    if tab in cfg:
        st = cfg[tab]

    #tsn = rec["tsn"]
    tsn = "11G 915 911"
    sn = rec["CID"]
    pt = rec["PT"]
    ig2 = rec["1G2"]
    b288 = rec["288"]
    gbt = rec["GBT"]

    pstar = datetime.datetime.strptime(pt,"%Y%m%d%H%M%S")
    nedtime = datetime.timedelta(minutes=15)
    pen = (pstar+nedtime).strftime("%Y-%m-%dT%H:%M:%S")
    pstart = str(pstar.strftime("%Y-%m-%dT%H:%M:%S"))
    pend = str(pen)

    if st is None:
        uidinfo = json_post(client,host_graphdbget(),{
            "n":"tech",
            "obj":"uid,sn",
            "opt":{
                "and":[{
                    "eq":"sn",
                    "v":tsn
                }]
            }
        })
	print(uidinfo)
        uid = uidinfo[0]["uid"]

        info = json_post(client, host_graphdb(), {
            "a":[{
            "u":"line-one",
            "n":"task",
            "v":[[
                {"k":"sn","v":sn},
                {"k":"tech","u":uid},
                {"k":"pstart","v":pstart},
                {"k":"pend","v":pend},
                {"k":"pnum","v":"1"},
                {"k":"state","v":"open"},
                {"k": "ig2", "v": ig2},
                {"k": "288", "v": b288},
                {"k": "gbt", "v": gbt}
            ]]
            }]})
        if info == "Success":
            return info


def get_data(client, tab, cfg):
    st = None

    if tab in cfg:
        st = cfg[tab]
	
    if st is None:
        info = json_post(client, host_timedb(), {
            "n":tab,
            "obj":"*",
            "opt":{
                "limit":1
                }
            })

    else:
        info = json_post(client, host_timedb(), {
            "n":tab,
            "obj":"*",
            "opt":{
                "and":[{
                    "ge":"time",
                    "v":st
                }],
                "limit":20
                }
            })

    
    if info is not None:
        data1 = info["stnstatus"]
        if "start" in data1 and "end" in data1 and "data" in data1:
            print(data1["start"])
            print(data1["end"])
            print(data1["data"])

            cfg[tab] = data1["end"]
            for data in data1["data"]:
                return data

    return None

def put_stationdata(client,cfg,recv_mq):
    data = get_data(client,"stnstatus",cfg)
    if data is None:
        # logging.DEBUG("data=None")
        return

    doc = Document()
    env = doc.createElement("env:Envelope")
    doc.appendChild(env)
    env.setAttribute("xmlns:env", "http://pdps.in.audi.vwg/legacy_schema/20.7.3/envelope")

    herder = doc.createElement("Herder")
    doc.appendChild(herder)

    sender = doc.createElement("Sender")
    herder.appendChild(sender)

    location = doc.createElement("Location")
    sender.appendChild(location)
    sender_assembly_cycle = get_item(data,u"assembly_cycle")
    location.setAttribute("assembly_cycle",sender_assembly_cycle)
    location.setAttribute("assembly_line","MES Battery Assembly Line")
    location.setAttribute("assembly_subline", "1")
    location.setAttribute("plant", "C4")
    location.setAttribute("plant_segment", "Battery")

    device = doc.createElement("Device")
    sender.appendChild(device)
    sender_hostname = get_item(data, u"hostname")
    device.setAttribute("hostname",sender_hostname)
    sender_manufacturer = get_item(data, u"manufacturer")
    device.setAttribute("manufacturer", sender_manufacturer)
    sender_type = get_item(data,u"type")
    device.setAttribute("type", sender_type)
    sender_opmode = get_item(data, u"opmode")
    device.setAttribute("opmode", sender_opmode)

    telegraminfo = doc.createElement("Telegraminfo")
    herder.appendChild(telegraminfo)
    sender_timestamp = get_item(data, u"opmode")
    telegraminfo.setAttribute("timestamp",sender_timestamp)
    sender_datatype = get_item(data, u"opmode")
    telegraminfo.setAttribute("datatype", sender_datatype)

    body = doc.createElement("Body")
    doc.appendChild(body)

    batterdata = doc.createElement("BatteryData")
    doc.appendChild(batterdata)
    cid = get_item(data, u"cid")
    batterdata.setAttribute("cid",cid)
    prt = get_item(data, u"teilnr.")
    batterdata.setAttribute("prt",prt)
    pt1 = get_item(data, u"gbt")
    batterdata.setAttribute("pt1",pt1)

    prc_sst = doc.createElement("PRC_SST")
    doc.appendChild(prc_sst)

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
    Gbt_info = doc.createTextNode("dddd")
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


    xml = open("reserve.xml","w")
    doc.writexml(xml, indent='\t', newl='\n', addindent='\t', encoding='gbk')
    xml.close()

    with open("reserve.xml", "rt") as xml:
        line = xml.read()
        print(line)

    connect(recv_mq)
    queue.put(line)
    # logging.info(line)
    queue.close()	
    print("3")

def get_getplan(client,cfg,recv_mq):
    connect(recv_mq)
    
    rec = queue.get()
    queue.close()
    json = xml2dict(rec)
    #print(json)
    a = readjson(json)

    x = a[0]
    y = a[1]

    result = get_plan(client,"sn",cfg,x)
    
    if result=="Success":
        print("writer success")
        put_getplan(x,y)


def put_getplan(x,y):
    recv_mq = {
        "ip": "10.232.129.54",
        "port": 1416,
        "username": "mqm",
        "password": "mqm",

        "recv_queue_manager": "VMFSMESMQTEST1",
        "recv_channel": "CLI.PD.MES.MEB.1",
        "recv_queue": "MES.MEB.BODY.PLAN.ACK",
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
    #connect(recv_mq)
    x = str(y)
    queue.put(x)
    print(x)
    queue.close()




def do_post_cmd(cmd,n):
    client = tornado.httpclient.HTTPClient()
    cfg = read_cfg()

    if cfg is None:
        cfg = {}

    if cmd == "stnstatus":
        recv_mq = {
            "ip": "10.232.129.54",
            "port": 1416,
            "username": "mqm",
            "password": "mqm",

            "recv_queue_manager": "VMFSMESMQTEST1",
            "recv_channel": "CLI.PD.MES.MEB.1",
            "recv_queue": "MES.MEB.TEST.SENSOR",
        }
        put_stationdata(client,cfg,recv_mq)
    client.close()

    write_cfg(cfg)

def do_get_cmd(cmd,n):
    client = tornado.httpclient.HTTPClient()
    cfg = read_cfg()

    if cfg is None:
        cfg = {}

    if cmd == "getplan":
        recv_mq = {
            "ip": "10.232.129.54",
            "port": 1416,
            "username": "mqm",
            "password": "mqm",

            "recv_queue_manager": "VMFSMESMQTEST1",
            "recv_channel": "CLI.PD.MES.MEB.1",
            "recv_queue": "MES.MEB.ASSEMBLE.PLAN.SEND",
        }
        get_getplan(client,cfg,recv_mq)

def puttest():
    recv_mq = {
            "ip": "10.232.129.54",
            "port": 1416,
            "username": "mqm",
            "password": "mqm",

            "recv_queue_manager": "VMFSMESMQTEST1",
            "recv_channel": "CLI.PD.MES.MEB.1",
            "recv_queue": "MES.MEB.ASSEMBLE.PLAN.SEND",
        }
    connect(recv_mq)
    line = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><env:Envelope xmlns:env="http://pdps.in.audi.vwg/legacy_schema/20.7.3/envelope" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:com="http://pdps.in.audi.vwg/legacy_schema/20.7.3-2018.01/common" xsi:schemaLocation="http://pdps.in.audi.vwg/legacy_schema/20.7.3-2018.01/envelope envelope.xsd"><Header><Sender><Location assembly_cycle="" assembly_line="" assembly_line_section="" assembly_subline="" plant="79" plant_segment="BODY"/><Device name="" hostname="" ipaddress="10.228.202.97" macaddress="" manufacturer="" type="" operating_state="" model=""/><Application majorversion="1" minorversion="0" name="MES" manufacturer=""/></Sender><Telegraminfo minorversion="0" majorversion="1" dataguid="" timestamp="2020-03-21T11:35:39" datatype="MODULES"/><Communicationtype type="SEND"/></Header><Body><VehicleData><BodyIdent plant="79" id="1412019" productionyear="0000" checkdigit="2"/></VehicleData><Data><Raw><Detail><Key>STA</Key><Value>1</Value></Detail><Detail><Key>288</Key><Value>288 5FAFA33019+</Value></Detail><Detail><Key>PT</Key><Value>20200321113539</Value></Detail><Detail><Key>SQR</Key><Value>0001</Value></Detail><Detail><Key>GBT</Key><Value>08OPEA00LFV0ABA330000019</Value></Detail><Detail><Key>TYP</Key><Value>0</Value></Detail><Detail><Key>1G2</Key><Value>1G2 5FAFA390252</Value></Detail><Detail><Key>PRN</Key><Value>+KB3+M2R</Value></Detail><Detail><Key>TSN</Key><Value>11G 915 910 E</Value></Detail><Detail><Key>CID</Key><Value>79000014120193</Value></Detail></Raw></Data></Body></env:Envelope>'
    queue.put(line)
    queue.close()	
    print("put up success")
    

def do_task():
    do_post_cmd("stnstatus",None)
    #do_get_cmd("getplan",None)
puttest()
#do_task()
