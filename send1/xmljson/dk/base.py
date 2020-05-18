import xml
import xml.dom
import xml.dom.minidom
import datetime


def xml_node(doc, parent, name, val):
    nd = doc.createElement(name)
    nd_v = doc.createTextNode(val)
    nd.appendChild(nd_v)
    parent.appendChild(nd)


def xml_head():
    doc = xml.dom.minidom.Document()
    env = doc.createElement("env:Envelope")
    doc.appendChild(env)

    header = doc.createElement("Header")
    env.appendChild(header)

    sender = doc.createElement("Sender")
    header.appendChild(sender)

    location = doc.createElement("Location")
    sender.appendChild(location)

    device = doc.createElement("Device")
    sender.appendChild(device)

    application = doc.createElement("Application")
    sender.appendChild(application)

    telegraminfo = doc.createElement("Telegraminfo")
    header.appendChild(telegraminfo)

    communicationtype = doc.createElement("Communicationtype")
    header.appendChild(communicationtype)

    body = doc.createElement("Body")
    env.appendChild(body)

    vechicledata = doc.createElement("VehicleData")
    body.appendChild(vechicledata)

    bodyident = doc.createElement("BodyIdent")
    vechicledata.appendChild(bodyident)

    kident = doc.createElement("KINIdent")
    vechicledata.appendChild(kident)

    data = doc.createElement("Data")
    body.appendChild(data)

    raw = doc.createElement("Raw")
    data.appendChild(raw)

    env.setAttribute("xmlns:env", "http://pdps.in.audi.vwg/legacy_schema/20.7.3/envelope")
    env.setAttribute("xmlns:com", "http://pdps.in.audi.vwg/legacy_schema/20.7.3-2018.01/common")
    env.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    env.setAttribute("xsi:schemaLocation", "http://pdps.in.audi.vwg/legacy_schema/20.7.3-2018.01/envelope envelope.xsd")

    location.setAttribute("plant_segment", "BODY")
    location.setAttribute("plant", "C4")
    location.setAttribute("assembly_subline", "N")
    location.setAttribute("assembly_line", "MLA")

    device.setAttribute("operating_state", "AUTOMATICMODE")
    device.setAttribute("type", "Leitrechner")

    now = datetime.datetime.now()
    tim = datetime.datetime.strftime(now, '%Y-%m-%dT%H:%M:%S')
    year = datetime.datetime.strftime(now, '%Y')

    telegraminfo.setAttribute("timestamp", str(tim))
    telegraminfo.setAttribute("datatype", "MODULES")
    telegraminfo.setAttribute("majorversion", "1")
    telegraminfo.setAttribute("minorversion", "0")
    telegraminfo.setAttribute("dataguid", "")

    communicationtype.setAttribute("type", "SEND")

    bodyident.setAttribute("plant", "C4")
    bodyident.setAttribute("productionyear", str(year))
    bodyident.setAttribute("id", "1128001")
    bodyident.setAttribute("checkdigit", "9")

    kident.setAttribute("plant", "C4")
    kident.setAttribute("componentnumber", "20")
    kident.setAttribute("id", "1128001")
    kident.setAttribute("serial", "")
    kident.setAttribute("checkdigit", "9")

    return {
        "doc": doc,
        "location": location,
        "device": device,
        "application": application,
        "telegraminfo": telegraminfo,
        "communicationtype": communicationtype,
        "vechicledata": vechicledata,
        "bodyident": bodyident,
        "kident": kident,
        "raw": raw,
        "data": data
    }


def xml_ack():
    ret = xml_head()

    location = ret["location"]
    device = ret["device"]
    application = ret["application"]
    bodyident = ret["bodyident"]
    kident = ret["kident"]

    location.setAttribute("assembly_cycle", "001")

    device.setAttribute("name", "CA431001")
    device.setAttribute("model", "ES45")
    device.setAttribute("manufacturer", "IBM")
    device.setAttribute("macaddress", "AA-00-04-00-3B-0D")
    device.setAttribute("ipaddress", "10.201.13.23")
    device.setAttribute("hostname", "CA431001")

    application.setAttribute("name", "MMS")
    application.setAttribute("manufacturer", "Kon-Cept")
    application.setAttribute("uri", "")
    application.setAttribute("majorversion", "1")
    application.setAttribute("minorversion", "0")

    bodyident.setAttribute("id", "1128001")
    bodyident.setAttribute("checkdigit", "9")

    kident.setAttribute("componentnumber", "20")
    kident.setAttribute("id", "1128001")
    kident.setAttribute("checkdigit", "9")
    kident.setAttribute("serial", "")

    return ret


def xml_msn():
    ret = xml_head()

    device = ret["device"]

    device.setAttribute("manufacturer", "")
    device.setAttribute("type", "")
    device.setAttribute("opmode", "")

    return ret


def xml_fin():
    ret = xml_head()

    location = ret["location"]
    device = ret["device"]
    application = ret["application"]

    location.setAttribute("assembly_cycle", "501")

    device.setAttribute("name", "CA431001")
    device.setAttribute("model", "ES45")
    device.setAttribute("manufacturer", "IBM")
    device.setAttribute("macaddress", "AA-00-04-00-3B-0D")
    device.setAttribute("ipaddress", "10.212.120.14")
    device.setAttribute("hostname", "MESAF450")

    application.setAttribute("name", "MMS")
    application.setAttribute("manufacturer", "Kon-Cept")
    application.setAttribute("uri", "")
    application.setAttribute("majorversion", "1")
    application.setAttribute("minorversion", "0")

    return ret


def xml_print():
    ret = xml_head()

    location = ret["location"]
    device = ret["device"]
    application = ret["application"]
    communicationtype = ret["communicationtype"]

    location.setAttribute("assembly_cycle", "4501")

    device.setAttribute("name", "CA431001")
    device.setAttribute("model", "ES45")
    device.setAttribute("manufacturer", "IBM")
    device.setAttribute("macaddress", "AA-00-04-00-3B-0D")
    device.setAttribute("ipaddress", "10.212.120.14")
    device.setAttribute("hostname", "MESAF450")

    application.setAttribute("name", "MMS")
    application.setAttribute("manufacturer", "Kon-Cept")
    application.setAttribute("uri", "")
    application.setAttribute("majorversion", "1")
    application.setAttribute("minorversion", "0")

    communicationtype.setAttribute("type", "REQUEST")

    return ret
