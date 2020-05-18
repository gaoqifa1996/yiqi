import unittest
import pymqi
import time
import tornado
import tornado.httpclient
from tool import write_cfg, read_cfg
from yiqi import qmgr, put_fin, put_print, get_plan, get_printcode,put_eol


class Test(unittest.TestCase):
    def test_put(self):
        try:
            qmgr.connect_tcp_client("VMFSMESMQTEST1", pymqi.CD(), "CLI.PD.MES.MEB.1", "10.232.129.54(1416)", "mqm", "mqm")
        except pymqi.MQMIError as e:
            if e.comp == pymqi.CMQC.MQCC_WARNING and e.reason == pymqi.CMQC.MQRC_ALREADY_CONNECTED:
                pass
            else:
                print("mq error: %s" % e)
                return

        client = tornado.httpclient.HTTPClient()

        cfg = read_cfg()
        if cfg is None:
            cfg = {}
        put_eol(client,cfg)
        #put_fin(client, cfg)
	time.sleep(5)
        #put_print(client, cfg)
        #put_msndata(client, cfg)

        #get_plan(client)
        #get_printcode(client)

        write_cfg(cfg)
        client.close()


if __name__ == '__main__':
    unittest.main()
