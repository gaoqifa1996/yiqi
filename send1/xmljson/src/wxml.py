from base import xml_msn, xml_fin, xml_print, xml_node, xml_ack, xml_eol
from xmap import get_assemble, get_hostname, get_bodyident, get_kinident,get_map_type
import datetime
from tornado.escape import json_encode

def get_item(data, key):
    if key in data:
        return data[key]
    return ""


def w_msn(data):
    psn = data["psn"]
    wsn = data["wsn"]
    bzd = data["bzd"]
    point = data["point"]
    code = data["code"]
    ret = xml_msn()

    location = ret["location"]
    device = ret["device"]
    bodyident = ret["bodyident"]
    doc = ret["doc"]
    data = ret["data"]

    location.setAttribute("assembly_cycle", get_assemble(wsn))
    device.setAttribute("hostname", get_hostname(wsn))

    bid = get_bodyident(psn)

    bodyident.setAttribute("plant", get_item(bid, "plant"))
    bodyident.setAttribute("checkdigit", get_item(bid, "checkdigit"))
    bodyident.setAttribute("productionyear", get_item(bid, "productionyear"))
    bodyident.setAttribute("id", get_item(bid, "bodyidentid"))

    map_type = get_map_type(point)
    mod_type = doc.createElement(map_type)
    data.appendChild(mod_type)

    for d in bzd:
        code_num = bzd.index(d)
        mod = doc.createElement("Module")
        mod_type.appendChild(mod)

        mod.setAttribute("status", "AV")
        mod.setAttribute("code", code[code_num])
        mod.setAttribute("serialnumber", d)

    return doc.toxml(encoding='gbk')


def w_fin(data):
    ret = xml_fin()

    psn = data["psn"]
    bzd = get_bodyident(psn)

    bodyident = ret["bodyident"]
    kident = ret["kident"]
    raw = ret["raw"]
    doc = ret["doc"]

    bodyident.setAttribute("plant", get_item(bzd, "plant"))
    bodyident.setAttribute("checkdigit", get_item(bzd, "checkdigit"))
    bodyident.setAttribute("productionyear", get_item(bzd, "productionyear"))
    bodyident.setAttribute("id", get_item(bzd, "bodyidentid"))

    kid = get_kinident(psn)

    kident.setAttribute("plant", get_item(kid, "plant"))
    kident.setAttribute("componentnumber", get_item(kid, "componentnumber"))
    kident.setAttribute("productionyear", get_item(kid, "productionyear"))
    kident.setAttribute("id", get_item(kid, "bodyidentid"))
    kident.setAttribute("serial", " ")
    kident.setAttribute("checkdigit", get_item(kid, "checkdigit"))

    tin = get_item(data, u"in")
    tin = datetime.datetime.strptime(tin, "%Y-%m-%d %H:%M:%S").strftime("%Y%m%d%H%M%S")

    tout = get_item(data, u"out")
    tout = datetime.datetime.strptime(tout, "%Y-%m-%d %H:%M:%S").strftime("%Y%m%d%H%M%S")

    result = {
        "CID": psn,
        "IN": tin,
        "OUT": tout
    }

    for k, v in result.iteritems():
        detail = doc.createElement("Detail")
        raw.appendChild(detail)

        xml_node(doc, detail, "Key", k)
        xml_node(doc, detail, "Value", v)

    return doc.toxml(encoding='gbk')


def w_print(data):
    ret = xml_print()

    raw = ret["raw"]
    doc = ret["doc"]

    psn = data["psn"]

    detail = doc.createElement("Detail")
    raw.appendChild(detail)

    xml_node(doc, detail, "Key", "CID")
    xml_node(doc, detail, "Value", psn)

    return doc.toxml(encoding='gbk')


def w_ack():
    ret = xml_ack()

    raw = ret["raw"]
    doc = ret["doc"]

    now = datetime.datetime.now()
    tim = datetime.datetime.strftime(now, '%Y%m%d%H%M%S')

    detail = doc.createElement("Detail")
    raw.appendChild(detail)

    xml_node(doc, detail, "STA", "X000")
    xml_node(doc, detail, "TIM", str(tim))

    return doc.toxml(encoding='gbk')


def w_eol(data):
    psn = data["psn"]
    wsn = data["wsn"]
    eol_data = data["data"]
    status = data["status"]
    ret = xml_eol()

    location = ret["location"]
    device = ret["device"]
    bodyident = ret["bodyident"]
    doc = ret["doc"]
    prc_sst_world = ret["prc_sst_world"]

    location.setAttribute("assembly_cycle", get_assemble(wsn))
    device.setAttribute("hostname", get_hostname(wsn))

    bid = get_bodyident(psn)

    bodyident.setAttribute("plant", get_item(bid, "plant"))
    bodyident.setAttribute("checkdigit", get_item(bid, "checkdigit"))
    bodyident.setAttribute("productionyear", get_item(bid, "productionyear"))
    bodyident.setAttribute("id", get_item(bid, "bodyidentid"))

    abz = doc.createElement("ABZ")
    prc_sst_world.appendChild(abz)
    wrk = doc.createElement("WRK")
    prc_sst_world.appendChild(wrk)
    fsg = doc.createElement("FSG")
    prc_sst_world.appendChild(fsg)
    fab = doc.createElement("FAB")
    prc_sst_world.appendChild(fab)
    fbr = doc.createElement("FBR")
    prc_sst_world.appendChild(fbr)
    ort = doc.createElement("ORT")
    prc_sst_world.appendChild(ort)
    abs = doc.createElement("ABS")
    prc_sst_world.appendChild(abs)
    pnr = doc.createElement("PNR")
    prc_sst_world.appendChild(pnr)
    par = doc.createElement("PAR")
    prc_sst_world.appendChild(par)

    prt = doc.createElement("PRT")
    par.appendChild(prt)
    xml_node(doc,par,"PI1",psn)
    pi2 = doc.createElement("PI2")
    par.appendChild(pi2)
    stc = doc.createElement("STC")
    par.appendChild(stc)
    result = get_item(status,"result")
    if result == "pass":
        xml_node(doc,par,"PSC","IO")
    else:
        xml_node(doc,par,"PSC","NIO")
    xml_node(doc,par,"TotalTestTime",status["totaltesttime"])
    xml_node(doc,par,"Operator",status["Operator"])
    xml_node(doc,par,"Tp-Name",status["Tp-Name"])
    xml_node(doc,par,"gbcode",status["gbcode"])
    xml_node(doc,par,"bustype",status["bustype"])
    xml_node(doc,par,"bzdno",status["bzdno"])
    for i in eol_data:
        fas = doc.createElement("FAS")
        par.appendChild(fas)

        xml_node(doc, fas, "FAP",get_item(i,"itemname"))
        xml_node(doc, fas, "FNR", get_item(i, "stepno"))
        wid = doc.createElement("WID")
        fas.appendChild(wid)
        s = get_item(i, "result")
        if s == "pass":
            xml_node(doc, fas, "FSC", "IO")
        else:
            xml_node(doc, fas, "FSC", "NIO")
        sio = doc.createElement("SIO")
        fas.appendChild(sio)
        iio = doc.createElement("IIO")
        fas.appendChild(iio)
        ino = doc.createElement("INO")
        fas.appendChild(ino)

        grp = doc.createElement("GRP")
        fas.appendChild(grp)

        PNR = doc.createElement("PNR")
        grp.appendChild(PNR)
        GNR = doc.createElement("GNR")
        grp.appendChild(GNR)
        PRG = doc.createElement("PRG")
        grp.appendChild(PRG)
        DAT = doc.createElement("DAT")
        grp.appendChild(DAT)
        TIM = doc.createElement("TIM")
        grp.appendChild(TIM)
        TAC = doc.createElement("TAC")
        grp.appendChild(TAC)
        objl = doc.createElement("OBJL")
        grp.appendChild(objl)

        i.pop("esn")
        i.pop("stepno")
        i.pop("line")
        i.pop("psn")
        i.pop("result")
        i.pop("time")
        i.pop("wsn")
        i.pop("extname")
        i.pop("itemname")

        for aaa in i:
            obj = doc.createElement("OBJ")
            objl.appendChild(obj)
            xml_node(doc, obj, "NAME", aaa)
            ist = doc.createElement("IST")
            obj.appendChild(ist)
            unt = doc.createElement("UNT")
            ist.appendChild(unt)
            val = doc.createElement("VAL")
            ist.appendChild(val)
            xml_node(doc, val, "VAD", get_item(i,aaa))
            sta = doc.createElement("STA")
            ist.appendChild(sta)

    return doc.toxml(encoding='gbk')


def json_xml(data):
    key = data["k"]
    val = data["v"]

    if key == "ack":
        return w_ack()
    elif key == "print":
        return w_print(val)
    elif key == "fin":
        return w_fin(val)
    elif key == "msn":
        return w_msn(val)
    elif key == "eol":
        return w_eol(val)
    return None

d = {"status": {"totaltesttime":"5m","Operator":"root","result":"pass","Tp-Name":"c4202004010023","gbcode":"dfjsidjfisjfi","bustype":"11g 910 915 f","bzdno":"288 hudsfhsdfs"}, "data": [
            {
         "elapsedtime": "4'976",
         "esn": "il03",
         "extname": "null",
         "itemname": "ac connector contact check",
         "line": "line-one",
         "psn": "c4202003040022",
         "r-rac+-ohm": "0.978251",
         "r-rac+-ohm-max": "2.00000",
         "r-rac+-ohm-min": "0.000000",
         "r-rac--ohm": "1.03533",
         "r-rac--ohm-max": "2.00000",
         "r-rac--ohm-min": "0.000000",
         "result": "pass",
         "stepno": "1",
         "time": "2020-03-05T04:21:05.711473592Z",
         "wsn": "af220"
      },
            {
         "elapsedtime": "26'395",
         "esn": "il03",
         "extname": "null",
         "itemname": "meb system setup",
         "line": "line-one",
         "psn": "c4202003040022",
         "r-exbat-hvtns-setting": "348.000",
         "r-hvsrc": "347.975",
         "r-inbat-hvtns": "345.000",
         "r-isb": "0.643685",
         "r-processmsg": "0",
         "result": "pass",
         "stepno": "2",
         "time": "2020-03-05T04:21:05.711473592Z",
         "wsn": "af220"
      },
            {
         "elapsedtime": "16'224",
         "esn": "il03",
         "extname": "null",
         "itemname": "dc connector contact check",
         "line": "line-one",
         "psn": "c4202003040022",
         "r-message": "0",
         "r-rdc+-ohm": "1.02264",
         "r-rdc+-ohm-max": "2.00000",
         "r-rdc+-ohm-min": "0.000000",
         "r-rdc--ohm": "1.05230",
         "r-rdc--ohm-max": "2.00000",
         "r-rdc--ohm-min": "0.000000",
         "result": "pass",
         "stepno": "3",
         "time": "2020-03-05T04:21:05.711473592Z",
         "wsn": "af220"
      },
            {
         "elapsedtime": "3'619",
         "esn": "il03",
         "extname": "null",
         "itemname": "meb bmce flash process",
         "line": "line-one",
         "psn": "c4202003040022",
         "r-bmce-result": "1",
         "r-bmce-result-max": "1",
         "r-bmce-result-min": "1",
         "r-bootloader-af": "null",
         "r-bootloader-bf": "5018",
         "r-bootloader-check": "5018",
         "r-flash-status": "0",
         "r-hwnr-af": "null",
         "r-hwnr-bf": "5ke915184ab",
         "r-hwver-af": "null",
         "r-hwver-bf": "002",
         "r-processmsg": "杞欢鐗堟湰宸叉渶鏂帮紝鏃犻渶鍒峰啓!",
         "r-swver-af": "null",
         "r-swver-bf": "0815",
         "r-swver-check": "0815",
         "r-swver-limit": "a760",
         "result": "pass",
         "stepno": "4",
         "time": "2020-03-05T04:21:05.711473592Z",
         "wsn": "af220"
      },
            {
         "elapsedtime": "6'271",
         "esn": "il03",
         "extname": "null",
         "itemname": "meb addressing cell controllers",
         "line": "line-one",
         "psn": "c4202003040022",
         "r-processmsg": "0",
         "r-responsedata": "24",
         "r-timer": "4.02500",
         "r-timer-max": "5.00000",
         "result": "pass",
         "stepno": "5",
         "time": "2020-03-05T04:21:05.711473592Z",
         "wsn": "af220"
      },
            {
         "elapsedtime": "4:30'038",
         "esn": "il03",
         "extname": "null",
         "itemname": "meb cmce flash process",
         "line": "line-one",
         "psn": "c4202003040022",
         "r-cmceflashstatus-array": "001,001,001",
         "r-cmcenum": "3",
         "r-cmceresult-array": "001,001,001",
         "r-cmceresult-array-max": "001,001,001",
         "r-cmceresult-array-min": "001,001,001",
         "r-hwnr-af-cmc1": "5ke915140  ",
         "r-hwnr-af-cmc5": "5ke915140  ",
         "r-hwnr-af-cmc9": "5ke915140  ",
         "r-hwnr-bf-cmc1": "5ke915140  ",
         "r-hwnr-bf-cmc5": "5ke915140  ",
         "r-hwnr-bf-cmc9": "5ke915140  ",
         "r-hwver-af-cmc1": "001",
         "r-hwver-af-cmc5": "001",
         "r-hwver-af-cmc9": "001",
         "r-hwver-bf-cmc1": "001",
         "r-hwver-bf-cmc5": "001",
         "r-hwver-bf-cmc9": "001",
         "r-pnnr-af-cmc1": "5ke915140  ",
         "r-pnnr-af-cmc5": "5ke915140  ",
         "r-pnnr-af-cmc9": "5ke915140  ",
         "r-pnnr-bf-cmc1": "5ke915140  ",
         "r-pnnr-bf-cmc5": "5ke915140  ",
         "r-pnnr-bf-cmc9": "5ke915140  ",
         "r-processmsg-cmc1": "0",
         "r-processmsg-cmc5": "0",
         "r-processmsg-cmc9": "0",
         "r-swver-af-cmc1": "0800",
         "r-swver-af-cmc5": "0800",
         "r-swver-af-cmc9": "0800",
         "r-swver-bf-cmc1": "0750",
         "r-swver-bf-cmc5": "0750",
         "r-swver-bf-cmc9": "0750",
         "r-swver-check": "0800",
         "r-swver-limit": "0750",
         "r-swver-limit-2": "0760",
         "r-swver-limit-3": "c178",
         "result": "pass",
         "stepno": "6",
         "time": "2020-03-05T04:21:05.711473592Z",
         "wsn": "af220"
      }],
    "psn":"CS202004010023","wsn": "af220"}

ret = w_eol(d)
print(ret)
json_encode(ret)