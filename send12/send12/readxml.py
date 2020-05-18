import xmltodict
import json

# xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><env:Envelope xmlns:env="http://pdps.in.audi.vwg/legacy_schema/20.7.3/envelope"><Header><Sender><Location assembly_cycle="" assembly_line="" assembly_line_section="" assembly_subline="" plant="C4" plant_segment="BODY"/><Device name="" hostname="" ipaddress="10.228.202.97" macaddress="" manufacturer="" type="" operating_state="" model=""/><Application name="MES" minorversion="0" majorversion="1" manufacturer=""/></Sender><Telegraminfo minorversion="0" majorversion="1" dataguid="" timestamp="2020-02-07T10:45:45" datatype="MODULES"/><Communicationtype type="SEND"/></Header><Body><VehicleData><BodyIdent plant="C4" id="1128001" productionyear="2019" checkdigit="9"/></VehicleData><Data><Raw><Detail><Key>STA</Key><Value>X000</Value></Detail><Detail><Key>TIM</Key><Value>20191205135529000</Value></Detail></Raw></Data></Body></env:Envelope>'
def xml2dict(xml):
    convertedDict = xmltodict.parse(xml)
    # print(convertedDict)
    #ensure_ascii = False chinese can be used
    jsonStr = json.dumps(convertedDict,ensure_ascii=False)
    print(jsonStr)
    #if isinstance(jsonStr,str):
        #s = jsonStr.replace("\r", "").replace("\n", "")
        #jsonDict = eval(s)
        #return jsonDict
    #elif isinstance(jsonStr,dict):
        #return jsonStr
    jsonDict = eval(jsonStr)
    return jsonDict

def xml2dict2(xml):
    convertedDict = xmltodict.parse(xml)
    # print(convertedDict)
    #ensure_ascii = False chinese can be used
    jsonStr = json.dumps(convertedDict,ensure_ascii=False)
    print(jsonStr)
    if isinstance(jsonStr,str):
        s = jsonStr.replace("\r", "").replace("\n", "")
        jsonDict = json.loads(s)
        return jsonDict
    elif isinstance(jsonStr,dict):
        return jsonStr




def dict2xml(dict):
    #2.Json to Xml
    convertedXml = xmltodict.unparse(dict)
    print ("convertedXml=",convertedXml)
    return convertedXml


def readjson(json):
    print(json)
    env = json["env:Envelope"]
    xmlns = env["@xmlns:env"]
    header = env["Header"]

    body = env["Body"]
    vehicledata = body["VehicleData"]
    data = body["Data"]
    raw = data["Raw"]
    detail = raw["Detail"]
    d = {}
    for a in range(len(detail)):
        # print(detail[a])
        d[detail[a]["Key"]] = detail[a]["Value"]
    print(d)
    del env["Body"]["Data"]["Raw"]
    # print(env)
    return d,env

def readjson2(json):

    env = json["env:Envelope"]
    xmlns = env["@xmlns:env"]
    header = env["Header"]
    body = env["Body"]
    vehicledata = body["VehicleData"]
    data = body["Data"]
    raw = data["Raw"]
    detail = raw["Detail"]
    # return detail
    d = {}
    for a in range(len(detail)):
        # print(detail[a])
        d[detail[a]["Key"]] = detail[a]["Value"]
    # print(d)
    del env["Body"]["Data"]["Raw"]
    # print(env)
    return d,env

# jsonStr = {"env:Envelope": {"@xmlns:env": "http://pdps.in.audi.vwg/legacy_schema/20.7.3/envelope", "Header": {"Sender": {"Location": {"@assembly_cycle": "", "@assembly_line": "", "@assembly_line_section": "", "@assembly_subline": "", "@plant": "C4", "@plant_segment": "BODY"}, "Device": {"@name": "", "@hostname": "", "@ipaddress": "10.228.202.97", "@macaddress": "", "@manufacturer": "", "@type": "", "@operating_state": "", "@model": ""}, "Application": {"@name": "MES", "@minorversion": "0", "@majorversion": "1", "@manufacturer": ""}}, "Telegraminfo": {"@minorversion": "0", "@majorversion": "1", "@dataguid": "", "@timestamp": "2020-02-07T10:45:45", "@datatype": "MODULES"}, "Communicationtype": {"@type": "SEND"}}, "Body": {"VehicleData": {"BodyIdent": {"@plant": "C4", "@id": "1128001", "@productionyear": "2019", "@checkdigit": "9"}}, "Data": {"Raw": {"Detail": [{"Key": "STA", "Value": "X000"}, {"Key": "TIM", "Value": "20191205135529000"}]}}}}}
#
# jsonStr = '<?xml version="1.0" encoding="utf-8"?><env:Envelope xmlns:prc_sst="http://xmldefs.vw-group.com/KAP/station/V2.0/prc_sst" xmlns:env="http://www.audi.de/FIS" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.audi.de/FIS C:\Aktuell\pdps_xml_schema_prebuild_v.6_0_19_Freigabe_11.02.2008\envelope.xsd"><Header><Sender><Location plant_segment="BODY" plant="C4" assembly_subline="N" assembly_line="MLA" assembly_cycle="001" /><Device operating_state="AUTOMATICMODE" type="Leitrechner" name="CA431001" model="ES45" manufacturer="IBM" macaddress="AA-00-04-00-3B-0D" ipaddress="10.201.13.23" hostname="CA431001" /><Application name="MMS" manufacturer="Kon-Cept" uri="" majorversion="1" minorversion="0" /></Sender><Telegraminfo majorversion="1" minorversion="0" dataguid="" timestamp="2019-11-23T13:18:22" datatype="MODULES" /><Communicationtype type="RESPONSE" /></Header><Body><VehicleData><BodyIdent plant="C4" id="1128001" productionyear="2019" checkdigit="9" /><KINIdent plant="C4" componentnumber="20" productionyear="19" id="1128001" checkdigit="9" serial=""/></VehicleData><Data><Raw><Detail><Key>STATUS</Key><Value>IO</Value></Detail><Detail><Key>STATUS</Key><Value>C4201911280019</Value></Detail><Detail><Key>TELE</Key><Value> XXXXXXXXXXXX</Value></Detail></Raw></Data></Body></env:Envelope>'

# json = xml2dict(jsonStr)

# readjson(json)


