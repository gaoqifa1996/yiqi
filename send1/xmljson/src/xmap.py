hostname = {
    'af10': 'MESAF10',
    'af20': 'MESAF20',
    'af30': 'MESAF30',
    'af40': 'MESAF40',
    'af50': 'MESAF50',
    'af51': 'MESAF10',
    'af52': 'MESAF10',
    'af60': 'MESAF10',
    'af70': 'MESAF10',
    'af80': 'MESAF10',
    'af90': 'MESAF10',
    'af100': 'MESAF10',
    'af120': 'MESAF10',
    'af130': 'MESAF10',
    'af140': 'MESAF10',
    'af150': 'MESAF10',
    'af170': 'MESAF10',
    'af180': 'MESAF10',
    'af190': 'MESAF10',
    'af200': 'MESAF10',
    'af210': 'MESAF10',
    'af220': 'MESAF10',
    'af230': 'MESAF10',
    'af240': 'MESAF10',
    'af250': 'MESAF10',
    'af260': 'MESAF10',
    'af270': 'MESAF10',
    'af280': 'MESAF10',
    'af281': 'MESAF10',
    'af290': 'MESAF10',
    'af300': 'MESAF10',
    'af310': 'MESAF10',
    'af330': 'MESAF10',
    'af340': 'MESAF10',
    'af350': 'MESAF10',
    'af360': 'MESAF10',
    'af370': 'MESAF10',
    'af380': 'MESAF10',
    'af390': 'MESAF10',
    'af400': 'MESAF10',
    'af410': 'MESAF10',
    'af440': 'MESAF10',
    'af450': 'MESAF10',
    'af470': 'MESAF10',
    'af480': 'MESAF10',
    'af490': 'MESAF10',
    'af500': 'MESAF10',
    'af510': 'MESAF10',
    'af520': 'MESAF10',
    'af610': 'MESAF10',
    'af620': 'MESAF10',
    'af630': 'MESAF10',
    'af640': 'MESAF10',
}

assmble_cycle = {
    'af10': '101',
    'af20': '201',
    'af50': '501',
    'af60': '601',
    'af70': '701',
    'af80': '801',
    'af90': '901',
    'af100': '1001',
    'af120': '1201',
    'af130': '1301',
    'af140': '1401',
    'af150': '1501',
    'af170': '1701',
    'af180': '1801',
    'af190': '1901',
    'af200': '2001',
    'af210': '2101',
    'af220': '2201',
    'af230': '2301',
    'af240': '2401',
    'af250': '2501',
    'af260': '2601',
    'af270': '2701',
    'af280': '2801',
    'af281': '2802',
    'af290': '2901',
    'af300': '3001',
    'af310': '3101',
    'af330': '3301',
    'af340': '3401',
    'af350': '3501',
    'af360': '3601',
    'af370': '3701',
    'af380': '3801',
    'af390': '3901',
    'af400': '4001',
    'af410': '4101',
    'af440': '4401',
    'af450': '4501',
    'af470': '4701',
    'af480': '4801',
    'af490': '4901',
    'af500': '5001',
    'af510': '5101',
    'af520': '5201',
    'af610': '6101',
    'af620': '6201',
    'af630': '6301',
    'af640': '6401',
}

map_type = {
"121":"ZSB.Housing",
"111":"ZSB.Housing",
"141":"ZSB.Housing",
"523":"Cellmodule",
"513":"Cellmodule",
"812":"HVconnector",
"813":"HVconnector",
"912":"CMCE",
"922":"CMCE",
"1111":"BMC6E",
"1122":"Minusbox",
"1112":"Minusbox",
"1123":"Plusbox",
"1113":"Plusbox",
"1221":"Vehicleconnector",
"1211":"Vehicleconnector",
"1622":"CMC-Modulwire",
"1612":"CMC-Modulwire",
"1623":"CMC-Modulwire",
"1613":"CMC-Modulwire",
"1634":"NVwiringharness",
"1624":"NVwiringharness",
"1614":"NVwiringharness",
"1821":"HVwiringharness",
"1811":"HVwiringharness",
"1911":"Druckausgleichselement(DAE)",
"2013":"HVconnector",
"":"HVconnector",
"2012":"HVconnector",
"2032":"HVconnector",
"2022":"HVconnector",
"2721":"ZSB.Uppershell(incl.seal)",
"2711":"ZSB.Uppershell(incl.seal)",
"2741":"ZSB.Uppershell(incl.seal)",
"3421":"ZSBUnderrideprotection",
"3411":"ZSBUnderrideprotection",
}

def get_hostname(wsn):
    if wsn in hostname:
        return hostname[wsn]
    else:
        return ""


def get_assemble(wsn):
    if wsn in assmble_cycle:
        return assmble_cycle[wsn]
    else:
        return ""


def get_bodyident(cid):
    result = {}
    if len(cid) == 14:
        result["plant"] = cid[0:2]
        result["productionyear"] = cid[2:6]
        result["bodyidentid"] = cid[6:-1]
        result["checkdigit"] = cid[-1]

        return result
    else:
        return ""


def get_kinident(cid):
    result = {}
    if len(cid) == 14:
        result["plant"] = cid[0:2]
        result["componentnumber"] = cid[2:4]
        result["productionyear"] = cid[4:6]
        result["bodyidentid"] = cid[6:-1]
        result["checkdigit"] = cid[-1]

        return result
    else:
        return None

def get_map_type(scan_porint):
    if scan_porint in map_type:
        return map_type[scan_porint]
    else:
        return "ModuleData"