import pymqi


def connect(recv_mq):
    qmgr = pymqi.connect(recv_mq["recv_queue_manager"], recv_mq["recv_channel"], recv_mq["ip"] + "(" + str(recv_mq["port"]) + ")","username","password")
    global queue
    queue = pymqi.Queue(qmgr, recv_mq["recv_queue"])

def puttest():
    recv_mq = {
            "ip": "10.232.129.54",
            "port": 1416,
            "username": "mqm",
            "password": "mqm",

            "recv_queue_manager": "VMFSMESMQTEST1",
            "recv_channel": "CLI.PD.MES.MEB.1",
            "recv_queue": "MES.MEB.BODY.PLAN.SEND",
        }
    connect(recv_mq)
    line = '<?xml version="1.0" encoding="utf-8"?><env:Envelope xmlns:env="http://pdps.in.audi.vwg/legacy_schema/20.7.3/envelope"><Header><Sender><Location assembly_cycle="" assembly_line="" assembly_line_section="" assembly_subline="" plant="C4" plant_segment="BODY"/><Device name="" hostname="" ipaddress="10.228.202.97" macaddress="" manufacturer="" type="" operating_state="" model=""/><Application name="MES" minorversion="0" majorversion="1" manufacturer=""/></Sender><Telegraminfo minorversion="0" majorversion="1" dataguid="" timestamp="2020-02-07T10:45:45" datatype="MODULES"/><Communicationtype type="SEND"/></Header><Body><VehicleData><BodyIdent plant="C4" id="1128001" productionyear="2019" checkdigit="9"/></VehicleData><Data><Raw><Detail><Key>288</Key><Value>288 5FVL11999C=</Value></Detail><Detail><Key>PT</Key><Value>20200101120530</Value></Detail><Detail><Key>SQR</Key><Value>0001</Value></Detail><Detail><Key>GBT</Key><Value>08OFEA01LFV0AL110000999</Value></Detail><Detail><Key>1G2</Key><Value>1G2 5FV1234567C</Value></Detail><Detail><Key>PRN</Key><Value>#M2R</Value></Detail><Detail><Key>CID</Key><Value>C4201911280029</Value></Detail></Raw></Data></Body></env:Envelope>'
    queue.put(line)
    queue.close()	
    print("put up")

puttest()
