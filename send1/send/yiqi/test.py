import json
import urllib2
import unittest


def put_json(url, v):
    value = json.dumps(v)
    req = urllib2.Request(url, value, {'Content-Type': 'application/json'})
    response = urllib2.urlopen(req)

    return response.read()


class Test(unittest.TestCase):
    def do_put(self, cmd):
        # url = "http://127.0.0.1/send/put"
        url = "http://localhost:9900/send/put"
        respone = put_json(url, {
            "cmd": cmd
            })
        ret = json.loads(respone)
        print(ret["ret"])
        print(ret["error"])

    def test_put(self):
        self.do_put("stationpass")
        # self.do_put("packtighten")
        # self.do_put("packleaktest")
        # self.do_put("packweight")


if __name__ == '__main__':
    unittest.main()
