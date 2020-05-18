from base import xml_msn, xml_fin, xml_print, xml_node, xml_ack
from xmap import get_assemble, get_hostname, get_bodyident, get_kinident
import datetime


def get_item(data, key):
    if key in data:
        return data[key]
    return ""


def w_msn(data):
    psn = data["psn"]
    wsn = data["wsn"]
    bzd = data["bzd"]

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

    for d in bzd:
        mod = doc.createElement("Module")
        data.appendChild(mod)

        mod.setAttribute("status", "AV")
        mod.setAttribute("code", "KGG")
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

    return None
