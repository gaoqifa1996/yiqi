# from suds.client import Client
#
# user_url = "http://192.168.124.4:2020/?singleWsdl"
# client = Client(user_url, autoblend = True,faults=False,timeout=15)
# print('last sent:\n', client.last_sent())
# print('last recv:\n', client.last_received())
# print(client)



# print(client.service.GetMode())
# t = {'ns0':'{"eid": "op1010","uid": "op20190902","cmd": "WriteToPLC","data": {"y":"54644"},"sign": " "}'}
# t = '{"eid": "op1010","uid": "op20190902","cmd": "WriteToPLC","data": {"y":"54644"},"sign": " "}'
# print(type(t))
# t=getattr("data", 'GetMode')('{/"eid": "op1010","uid": "op20190902","cmd": "WriteToPLC","data": {"y":"54644"},"sign": " "}')
# result=client.service.GetMode(data = t)

# print(result)


# import suds

# 检查手机号归属地
# url = 'http://webservice.webxml.com.cn/WebServices/MobileCodeWS.asmx?wsdl'
# clientPH = suds.client.Client(url)
# print(clientPH)
# result = clientPH.service.getMobileCodeInfo(18955909753)  # 这个号码是办证的，拿来测试，哈哈
# print(result)  # 返回  18611217787：北京 北京 北京联通GSM卡
# print(clientPH.last_received())

# 检查QQ是否在线
# url2 = 'http://www.webxml.com.cn/webservices/qqOnlineWebService.asmx?wsdl'
# clientQQ = suds.client.Client(url2)
# print(clientQQ)
# res2 = clientQQ.service.qqCheckOnline(3458955191)
# print(res2) # 返回：Y
#
# if __name__ == '__main__':
#   pass



import json
a= '{"k":"ddddddd"}'
b = json.loads(a)
print(b)


s = '{"k":"ddd\\"dddd"}'
x = json.loads(s)
print(x)
print(x)