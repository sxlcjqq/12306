#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from urllib import request, parse
from datetime import datetime
from pprint import pprint
import sys
import json, re, time
import logging;logging.basicConfig(level=logging.DEBUG)
from login import My12306
import myInfo

def getStationName():
    stationVersion = 1.9044
    url = "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js"
    reqData = parse.urlencode([("station_version", stationVersion)])
    url = url + "?" + reqData
    logging.debug(url)
    req = request.Request(url)
    with request.urlopen(req) as f:
        names = f.read()
        with open("stationInfo.txt", "wb") as fw:
            fw.write(names)
        
        itemsTMP = names.decode('utf-8').split("'")
        formatStr = "{:<16} {:<16} {:<16} {:<16} {:<16} {:<16}"
        if len(itemsTMP) == 3:
            with open("stationTable.txt", "wt") as fw:
                items = itemsTMP[1].split('@')
                logging.debug(formatStr.format("代号","中文名","车站代码","中文拼音","拼音首字母","序号"))
                fw.write(formatStr.format("代号","中文名","车站代码","中文拼音","拼音首字母","序号"))
                for item in items:
                    if item == "": continue
                    info = item.split("|")
                    logging.debug(formatStr.format(*info))
                    fw.write(formatStr.format(*info))
                    fw.write("\n")

# getStationName()


"""
[0] tf%2B3IVkDJ7uFD4smUZpouHqCUnYHQroOGXrhxEaCG9ALaJ1BDRKHiPDEM8Mn%2F4dKC0R3i52ReHd8%0AFRhAkoB7np86Y8P4WbTa1GovFeB5f
ViSVDkFp7RpQCcQ0OXDsDFa5f8v4gYpXNJsj12%2B0hSplzpA%0A3vOzbJtUkFRQRSxFEjIVMDl1t6vGGEL5y%2BJ3ex%2Fe0yZRGa21MlZz1MAOI9U3
HtVZYKtwhvV0g7vZ%0AsiUvF%2Fvcj6aATm3geFxj2d7hfSTy9R2%2FbSFK3L0%3D
[1] 预订
[2] 6c000G11400F
[3] G1140
[4] IZQ
[5] WHN
[6] IZQ
[7] WHN
[8] 18:43
[9] 23:01
[10] 04:18
[11] Y
[12] BfwS4mAMpcQ4E8qbPZCZ8nSKPYw%2BhRsIfsjw%2FdXg%2F74o2MTB1XgTwcuOSt0%3D
[13] 20180129
[14] 3
[15] Q9
[16] 01
[17] 08
[18] 1
[19] 0
[20]
[21]
[22]
[23]
[24]
[25]
[26] 无
[27]
[28]
[29]
[30] 有
[31] 16
[32] 3
[33]
[34] O090M0O0
[35] O9MO
[36] 0
"""
"""
{'data': {'flag': '1',
          'map': {'GGQ': '广州东',
                  'GZQ': '广州',
                  'HKN': '汉口',
                  'IZQ': '广州南',
                  'WCN': '武昌',
                  'WHN': '武汉'},
          'result': ['|预订|6c0000G29600|G296|IZQ|TXP|IZQ|WHN|06:28|1
0:54|04:26|Y|YjVHflqJg3%2FAcYSaWZPAZqNcasBODd2Ba2mIiRCUE9eXKtnG|20180129|3|Q9|01|09|1|0|||||||||||无|有|19||O0M090|OM9|0',
                     ]},
 'httpstatus': 200,
 'messages': '',
 'status': True}
"""
def getTrainInfo2():
    "GET"
    destDat = "2018-01-25"
    baseURL = "https://kyfw.12306.cn/otn/leftTicket/queryZ"
    reqData = parse.urlencode([
        ("leftTicketDTO.train_date",   destDat),
        ("leftTicketDTO.from_station", "GZQ"),
        ("leftTicketDTO.to_station",   "WHN"),
        ("purpose_codes",              "ADULT")
    ])
    destURL = baseURL + "?" + reqData

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.3",
        "Referer":    "https://kyfw.12306.cn/otn/leftTicket/init",
        "Host":       "kyfw.12306.cn",
        "X-Requested-With": "XMLHttpRequest",
    }
    req = request.Request(destURL, headers=headers)

    with request.urlopen(req) as f:
        logging.debug("Status:{} {}".format(f.status, f.reason))
        for k, v in f.getheaders():
            logging.debug("{}: {}".format(k, v))
        try:
            data = json.loads(f.read().decode("utf-8"))
        except:
            sys.exit("something wrong")
        
        pprint(data)
        # 车次 3  发车时间 8 到达 9 历时 10 发车日期 13 是否可预订 11
        # 商务 32 一等 31 二等 30
        # 无座 26 软卧 23 硬卧 28 硬座 29
        if data["httpstatus"] == 200:
            for item in data["data"]["result"]:
                for i, v in enumerate(item.split("|")):
                    logging.debug("[{}] {}".format(i, v))
                    # print(v, end=" ")

def getTrainInfo(browser):
    destDat = "2018-01-29"
    ticketData = parse.urlencode([
        ("leftTicketDTO.train_date",   destDat),
        ("leftTicketDTO.from_station", "GZQ"),
        ("leftTicketDTO.to_station",   "WHN"),
        ("purpose_codes",              "ADULT")
    ])
    logging.debug("ticketData: {}".format(ticketData))
    
    ok = False
    while not ok:
        retCode, retData = browser.doGET("https://kyfw.12306.cn/otn/leftTicket/queryZ", ticketData)
        logging.info("retCode:[{}]".format(retCode))
        try:
            trainData = json.loads(retData.decode("utf-8"))
            ok = True
            return trainData
        except:
            time.sleep(5)

"""
POST 验证用户是否登陆: https://kyfw.12306.cn/otn/login/checkUser
参数列表:
_json_att:

POST 车票信息是否过期: https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest
参数列表:
secretStr:j/1PMOf74E0WmppV1A8k/vHAZYpxpgkaGq5AATeQE4eMEW09JSABTTN6SxpsMASmXWqC1ju2OAyf
8rSPiES/clHkQiWwta8XxUMylLOUmIq0LTcPQdxXkOamUvOox9qiEFDP1EcyrCiQPn4fu0MGrV6O
0egB0wtILTJngdf/qRTZmw20BtyeL40yjdZzm+csW8miS0LqYl/zU0U+IbhpoxOfDaNb7sA0QZtn
ljM2UMrgo6VZU3cE9HyaeOQ/yTc3EYgQBFjmjks=
train_date:2018-01-16
back_train_date:2018-01-13
tour_flag:dc
purpose_codes:ADULT
query_from_station_name:广州
query_to_station_name:武汉
undefined:
"""
def checkUser(browser):
    data = {"_json_att": ""}
    retCode, retData = browser.doPOST("https://kyfw.12306.cn/otn/login/checkUser", parse.urlencode(data))
    logging.info("retCode:[{}]".format(retCode))

def submitOrderRequest(browser, train):
    back_date = datetime.strftime(datetime.now(), "%Y-%m-%d")
    wantTrainInfo = train["data"]["result"][0].split("|")
    data = {
        "secretStr": wantTrainInfo[0],
        "train_date": "",
        "back_train_date": back_date,
        "tour_flag": "dc",
        "purpose_codes": "ADULT",
        "query_from_station_name": "广州",
        "query_to_station_name": "武汉",
        "undefined": "",
    }
    retCode, retData = browser.doPOST("https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest",
        parse.urlencode(data))
    logging.info("retCode:[{}]".format(retCode))
"""
POST initDc https://kyfw.12306.cn/otn/confirmPassenger/initDc
_json_att:
响应信息里提取:  var globalRepeatSubmitToken = '41ccc1848d24018ea59ea2534dcb6ef6';
"""
def getSubmitToken(browser):
    # browser.doGET("https://kyfw.12306.cn/otn/index/initMy12306")
    browser.headers["Referer"] = "https://kyfw.12306.cn/otn/leftTicket/init"
    data = {"_json_att": ""}
    retCode, retData = browser.doPOST("https://kyfw.12306.cn/otn/confirmPassenger/initDc", parse.urlencode(data))
    if retCode == 200:
        html = retData.decode("utf-8")
        logging.debug(html)
        matchs = re.findall(r"globalRepeatSubmitToken\s+=\s+'(\w+)'", html)
        logging.debug(matchs)
        browser.token = matchs[0] if matchs else ""

"""
POST 获取乘车人信息: https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs
参数列表:
_json_att:
REPEAT_SUBMIT_TOKEN:41ccc1848d24018ea59ea2534dcb6ef6
返回:
{"validateMessagesShowId":"_validatorMessage","status":true,
"httpstatus":200,"data":{"isExist":true,"exMsg":"","two_isOpenClick":["93","95","97","99"],
"other_isOpenClick":["91","93","98","99","95","97"],
"normal_passengers":[
{"code":"4","passenger_name":"张三","sex_code":"M","sex_name":"男","born_date":"2000-01-01 00:00:00",
"country_code":"CN","passenger_id_type_code":"1","passenger_id_type_name":"二代身份证","passenger_id_no":"二代身份证",
"passenger_type":"1","passenger_flag":"0","passenger_type_name":"成人","mobile_no":"电话","phone_no":"","email":"zhangsan@qq.com",
"address":"","postalcode":"","first_letter":"ZS","recordCount":"12","total_times":"99","index_id":"0"},
{"code":"3","passenger_name":"李四","sex_code":"F","sex_name":"女","born_date":"2000-01-01 00:00:00",
"country_code":"CN","passenger_id_type_code":"1","passenger_id_type_name":"二代身份证","passenger_id_no":"二代身份证",
"passenger_type":"1","passenger_flag":"0","passenger_type_name":"成人","mobile_no":"电话","phone_no":"","email":"",
"address":"","postalcode":"","first_letter":"LS","recordCount":"12","total_times":"99","index_id":"1"}
],"dj_passengers":[]},"messages":[],"validateMessages":{}}
"""
def getPassengerInfo(browser):
    postData = {
        "_json_att": "",
        "REPEAT_SUBMIT_TOKEN": browser.token,
    }
    ok = False
    while not ok:
        retCode, retData = browser.doGET("https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs", 
            parse.urlencode(postData))
        logging.info("retCode:[{}]".format(retCode))
        try:
            passengerData = json.loads(retData.decode("utf-8"))
            ok = True
            return passengerData
        except:
            raise "获取车票信息失败"

"""
POST 订单信息: https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo
参数列表:
cancel_flag:2
bed_level_order_num:000000000000000000000000000000
passengerTicketStr:O,0,1,张三,1,身份证号码,电话号码,N
oldPassengerStr:张三,1,身份证号码,1_
tour_flag:dc
randCode:
whatsSelect:1
_json_att:
REPEAT_SUBMIT_TOKEN:41ccc1848d24018ea59ea2534dcb6ef6
返回:
{"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,"data":
{"ifShowPassCode":"N","canChooseBeds":"N","canChooseSeats":"Y","choose_Seats":"O9M",
"isCanChooseMid":"N","ifShowPassCodeTime":"1","submitStatus":true,"smokeStr":""},
"messages":[],"validateMessages":{}}
"""
def checkOrderInfo(browser, passengerInfo):
    myself = passengerInfo["normal_passengers"][0]
    # "passengerTicketStr": "O,0,1,张三,1,身份证号码,电话号码,N",
    passengerAttrList = []
    passengerAttrList.append["O"]
    passengerAttrList.append[myself["passenger_flag"]]
    passengerAttrList.append[myself["passenger_type"]]
    passengerAttrList.append[myself["passenger_name"]]
    passengerAttrList.append[myself["passenger_id_type_code"]]
    passengerAttrList.append[myself["passenger_id_no"]]
    passengerAttrList.append[myself["mobile_no"]]
    passengerAttrList.append["N"]

    # "oldPassengerStr": "张三,1,身份证号码,1_",
    oldPassengerAttrList = []
    oldPassengerAttrList.append[myself["passenger_name"]]
    oldPassengerAttrList.append[myself["passenger_id_type_code"]]
    oldPassengerAttrList.append[myself["passenger_id_no"]]
    oldPassengerAttrList.append[myself["1_"]]
     
    postData = {
        "cancel_flag": "2",
        "bed_level_order_num": "000000000000000000000000000000",
        "passengerTicketStr": ",".join(passengerAttrList),
        "oldPassengerStr": ",".join(oldPassengerAttrList),
        "tour_flag": "dc",
        "randCode": "",
        "whatsSelect": "1",
        "_json_att": "",
        "REPEAT_SUBMIT_TOKEN": browser.token,
    }
    retCode, retData = browser.doPOST("https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo", 
            parse.urlencode(postData))
    logging.info("retCode:[{}]".format(retCode))

"""
POST 抢票队列: https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount
参数列表:
train_date:Tue Jan 16 2018 00:00:00 GMT+0800 (中国标准时间)
train_no:6c000G11100C
stationTrainCode:G1110
seatType:O
fromStationTelecode:IZQ
toStationTelecode:WHN
leftTicket:OZR1tpi%2BCS0QS8hPbEkbAETALtfyHEorcZtzKm2GfmJfMqKMr78Z3Na4iWQ%3D
purpose_codes:00
train_location:Q9
_json_att:
REPEAT_SUBMIT_TOKEN:41ccc1848d24018ea59ea2534dcb6ef6
"""
def getQueueCount(browser, train):
    wantTrainInfo = train["data"]["result"][0].split("|")
    
    postData = {
        "train_no": wantTrainInfo[2],
        "stationTrainCode": wantTrainInfo[3],
        "seatType": "O",
        "fromStationTelecode": wantTrainInfo[6],
        "toStationTelecode": wantTrainInfo[7],
        "leftTicket": wantTrainInfo[12],
        "purpose_codes": "00",
        "train_location": "Q9",
        "_json_att": "",
        "REPEAT_SUBMIT_TOKEN": browser.token,
    }
    retCode, retData = browser.doPOST("https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount", 
            parse.urlencode(postData))
    logging.info("retCode:[{}]".format(retCode))



"""
POST 验证队列: https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue
passengerTicketStr:O,0,1,张三,1,身份证号码,电话号码,N
oldPassengerStr:张三,1,身份证号码,1_
randCode:
purpose_codes:00
key_check_isChange:7819EDE21F4BC814E2D8A055CB8B42AAA841B68CAB88AAC06455045B
leftTicketStr:OZR1tpi%2BCS0QS8hPbEkbAETALtfyHEorcZtzKm2GfmJfMqKMr78Z3Na4iWQ%3D
train_location:Q9
choose_seats:1A [or""]
seatDetailType:000
whatsSelect:1
roomType:00
dwAll:N
_json_att:
REPEAT_SUBMIT_TOKEN:41ccc1848d24018ea59ea2534dcb6ef6
"""
def confirmSingleForQueue(browser, passengerInfo, train):
    wantTrainInfo = train["data"]["result"][0].split("|")
    myself = passengerInfo["normal_passengers"][0]
    # "passengerTicketStr": "O,0,1,张三,1,身份证号码,电话号码,N",
    passengerAttrList = []
    passengerAttrList.append["O"]
    passengerAttrList.append[myself["passenger_flag"]]
    passengerAttrList.append[myself["passenger_type"]]
    passengerAttrList.append[myself["passenger_name"]]
    passengerAttrList.append[myself["passenger_id_type_code"]]
    passengerAttrList.append[myself["passenger_id_no"]]
    passengerAttrList.append[myself["mobile_no"]]
    passengerAttrList.append["N"]

    # "oldPassengerStr": "张三,1,身份证号码,1_",
    oldPassengerAttrList = []
    oldPassengerAttrList.append[myself["passenger_name"]]
    oldPassengerAttrList.append[myself["passenger_id_type_code"]]
    oldPassengerAttrList.append[myself["passenger_id_no"]]
    oldPassengerAttrList.append[myself["1_"]]

    postData = {
        "passengerTicketStr": ",".join(passengerAttrList),
        "oldPassengerStr": ",".join(oldPassengerAttrList),
        "randCode": "",
        "purpose_codes": "00",
        "whatsSelect": "1",
        "key_check_isChange": "",
        "leftTicketStr": wantTrainInfo[12],
        "train_location": "Q9",
        "choose_seats": "",
        "seatDetailType": "000",
        "whatsSelect": "1",
        "roomType": "00",
        "dwAll": "N",
        "_json_att": "",
        "REPEAT_SUBMIT_TOKEN": browser.token,
    }
    retCode, retData = browser.doPOST("https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue", 
            parse.urlencode(postData))
    logging.info("retCode:[{}]".format(retCode))

"""
GET https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime
random:1515829299528
tourFlag:dc
_json_att:
REPEAT_SUBMIT_TOKEN:41ccc1848d24018ea59ea2534dcb6ef6

GET https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime
random:1515829302546
tourFlag:dc
_json_att:
REPEAT_SUBMIT_TOKEN:41ccc1848d24018ea59ea2534dcb6ef6

POST https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue
orderSequence_no:EG02217919
_json_att:
REPEAT_SUBMIT_TOKEN:41ccc1848d24018ea59ea2534dcb6ef6
"""
def getMillSeconds():
    millSec = time.time() * 1000
    return str(millSec).split(".")[0]

def queryOrderWaitTime(browser):
    millSec = getMillSeconds()
    data = {
        "random": millSec,
        "tourFlag": "dc",
        "_json_att": "",
        "REPEAT_SUBMIT_TOKEN": browser.token,
    }
    retCode, retData = browser.doGET("https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime", 
            parse.urlencode(data))
    logging.info("retCode:[{}]".format(retCode))

def resultOrderForDcQueue(browser):
    pass


my12306 = My12306()
my12306.checkCaptcha()
my12306.doLogin(myInfo.user, myInfo.passwd)

trainInfo = getTrainInfo(my12306)
logging.debug(trainInfo)
checkUser(my12306)
submitOrderRequest(my12306, trainInfo)
getSubmitToken(my12306)
passengerInfo = getPassengerInfo(my12306)
logging.debug(passengerInfo)
checkOrderInfo(my12306, passengerInfo)
getQueueCount(my12306, trainInfo)
confirmSingleForQueue(my12306, passengerInfo, trainInfo)
queryOrderWaitTime(my12306)
queryOrderWaitTime(my12306)