import json
import urllib2
import unittest


def put_json(url, v):
    value = json.dumps(v)
    req = urllib2.Request(url, value, {'Content-Type': 'application/json'})
    response = urllib2.urlopen(req)

    return response.read()


class Test(unittest.TestCase):
    def jsonxml(self):
        # url = "http://127.0.0.1/xmljosn/put"
        url = "http://localhost:9903/xmljson/put"

        respone = put_json(url, {
            "cmd": "jsonxml",
            "data": {
                "k": "ack",
                "v": ""
                }
            })
        ret = json.loads(respone)
        print(ret)

        respone = put_json(url, {
            "cmd": "jsonxml",
            "data": {
                "k": "print",
                "v": {
                    "psn": "printaab"
                    }
                }
            })
        ret = json.loads(respone)
        print(ret)

        respone = put_json(url, {
            "cmd": "jsonxml",
            "data": {
                "k": "fin",
                "v": {
                    "psn": "1234567890abcd",
                    "in": "2020-10-20 20:32:22",
                    "out": "2020-10-20 20:34:22"
                    }
                }
            })
        ret = json.loads(respone)
        print(ret)

        respone = put_json(url, {
            "cmd": "jsonxml",
            "data": {
                "k": "msn",
                "v": {
                    "psn": "printaab",
                    "wsn": "af10",
                    "bzd": ["bzd-1", "bzd-2"]
                    }
                }
            })
        ret = json.loads(respone)
        print(ret)

    def xmljson(self):
        # url = "http://127.0.0.1/xmljosn/put"
        url = "http://localhost:9903/xmljson/put"
        respone = put_json(url, {
            "cmd": "xmljson",
            "data": '<env:Envelope>\
                    <Body name="a">\
                        <Data>\
                            <Raw>\
                                <Detail>\
                                    <Key>k1</Key>\
                                    <Value>v1</Value>\
                                </Detail>\
                                <Detail>\
                                    <Key>k2</Key>\
                                    <Value>v2</Value>\
                                </Detail>\
                            </Raw>\
                        </Data>\
                    </Body>\
                </env:Envelope>',
            })
        ret = json.loads(respone)
        print(ret)
        print(ret["env:Envelope"])

    def test_put(self):
        # self.xmljson()
        self.jsonxml()


if __name__ == '__main__':
    unittest.main()
