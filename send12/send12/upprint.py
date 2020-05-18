import pymqi


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

def puttest():
    recv_mq = {
            "ip": "10.232.129.54",
            "port": "1416",
            "username": "mqm",
            "password": "mqm",
            "recv_queue_manager": "VMFSMESMQTEST1",
            "recv_channel": "CLI.PD.MES.MEB.1",
            "recv_queue": "MES.MEB.ASSEMBLE.RESULT",
        }
    with open("test.xml", "rt") as xml:
        line = xml.read()
        print(line)
    connectmq_put(recv_mq,line)
    # line = '<?xml version="1.0" encoding="utf-8"?><env:Envelope xmlns:env="http://pdps.in.audi.vwg/legacy_schema/20.7.3/envelope"><Header><Sender><Location assembly_cycle="" assembly_line="" assembly_line_section="" assembly_subline="" plant="C4" plant_segment="BODY"/><Device name="" hostname="" ipaddress="10.228.202.97" macaddress="" manufacturer="" type="" operating_state="" model=""/><Application name="MES" minorversion="0" majorversion="1" manufacturer=""/></Sender><Telegraminfo minorversion="0" majorversion="1" dataguid="" timestamp="2020-02-07T10:45:45" datatype="MODULES"/><Communicationtype type="SEND"/></Header><Body><VehicleData><BodyIdent plant="C4" id="1128001" productionyear="2019" checkdigit="9"/></VehicleData><Data><Raw><Detail><Key>288</Key><Value>288 5FVL11999C=</Value></Detail><Detail><Key>PT</Key><Value>20200101120530</Value></Detail><Detail><Key>SQR</Key><Value>0001</Value></Detail><Detail><Key>GBT</Key><Value>08OFEA01LFV0AL110000999</Value></Detail><Detail><Key>1G2</Key><Value>1G2 5FV1234567C</Value></Detail><Detail><Key>PRN</Key><Value>#M2R</Value></Detail><Detail><Key>CID</Key><Value>C4201911280029</Value></Detail></Raw></Data></Body></env:Envelope>'
    print("put up printxml")

puttest()


