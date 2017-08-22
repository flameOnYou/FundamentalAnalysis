# -*- coding: utf-8 -*-
"""
当日爬虫
"""
from config import Conf

Economic_Calendar_Address = Conf.Economic_Calendar_Address
CSV_FILE_NAME = Conf.CSV_FILE_NAME
result_filename = Conf.result_filename
# 所需包体
from pyquery import PyQuery as pq
import csv
import time
import requests as rq
import json
import datetime
import sys
import os
# 统一网络层和系统编码格式

reload(sys)
sys.setdefaultencoding('utf8')

"""
初始化文件环境，如果 CSV_FILE_NAME 不存在就创建一个
"""
def initFile():
    if not os.path.exists(CSV_FILE_NAME):
        open(CSV_FILE_NAME,"w+").close()


"""
将EconomicCalendar列表转换成csv文件
@eclist  EconomicCalendar对象列表
@filename 文件名
@model 写入模式
"""
def writeToCsv(eclist,filename):
#     判断文件是否存在，存在则追加写入否则创建
    data = []
    lastTimeStamp = 0
    with open(filename,'rb') as csvfile:
        reader = list(csv.reader(csvfile))
        print "len:",len(reader)
        if len(reader) != 0:# 文件不为空
            lastDate = reader[-1][0]# 最后一个时间 2017-7-3 23:30
            lastTimeStamp = time.mktime(time.strptime(lastDate,'%Y-%m-%d %H:%M'))
        # 组装数据
    for e in eclist:
        # 如果现在时间小于存储的最后一个时间则跳过，说明是重复数据,
        # 如果包含什么实验性就不录入
        if '\u8bd5\u9a8c\u6027' in str(e.time) or '试验性' in str(e.name):
            continue
        print "str:",str(e.time)
        try:
             nowTimeStamp = time.mktime(time.strptime(e.time,'%Y-%m-%d %H:%M'))
        except Exception as e:
            continue


        if nowTimeStamp <= lastTimeStamp:
            continue
        e_data = (e.time,e.country, e.name ,e.actual, e.forecast, e.previous);
        data.append(e_data)
        csvfile = file(filename,'ab')
        writer = csv.writer(csvfile)
        writer.writerows(data)
        csvfile.close()

# 财经日历类
class EconomicCalendar(object):
    def __init__(self, time,country,name, actual, forecast, previous):
        self.time = time # 新闻发布时间
        self.country = country # 国家
        self.name = name # 新闻名字
        self.actual = actual # 实际值
        self.forecast = forecast # 预测值
        self.previous = previous # 前值

# 从定义地址爬取数据返回 EconomicCalendar 列表
def getEconomicCalendar_List(html_str):
    # 财经时间链表
    ecal_list = []
    # doc = pq(Economic_Calendar_Address)
    doc = pq(html_str)
    x = doc("tr").map(lambda i,e:pq(e)) # 遍历解析每个<tr>节点

    timestamp = ""
    for index,val in enumerate(x):
        # class=theDay的是日期
        tr = pq(val)
        td_ = tr("td").map(lambda i,e:pq(e)) # 遍历解析每个<td>节点
        td = tr("td").map(lambda i,e:pq(e).text())
        if td_.attr("class") == "theDay":
             timestamp = pq(val).text().split(u"\xa0")[0].replace(u"\u5e74", "-").replace(u"\u6708", "-").replace(u"\u65e5", "")
             print timestamp
             continue

         # 跳过节假日
        if(td[2] == "假日"):
            continue
        # 解析单元格内容
        time = timestamp+" "+td[0]
        country = td[1]
        eventNam = td[3]
        nowVal = td[4]
        forecastVal = td[5]
        priorValue = td[6]

        ec = EconomicCalendar(time,country,eventNam,nowVal,forecastVal,priorValue)
        ecal_list.append(ec)
    return ecal_list

"""
"设置爬虫模拟浏览器策略，防止反爬虫策略,他的数据回传一次只会传输5天的参数，所以要分批次获取
"dateFrom":"2017-07-01",
"dateTo":"2017-07-15",
"""
def getHTML(dateFrom,dateTo):

    url = "https://cn.investing.com/economic-calendar/Service/getCalendarFilteredData"

    headers = {
        "Host": "cn.investing.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
        "Accept": "*/*",
        "Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://cn.investing.com/economic-calendar/",
        "Connection": "keep-alive"

    }
    country = [37,6,110,14,48,46,32,17,10,36,43,35,72,22,41,25,12,5,4,26,11,39,42]
    data={
        "country" : country,
        "dateFrom":dateFrom,
        "dateTo":dateTo,
        "limit_from":"0",
        "timeFilter":"timeRemain",
        "timeZone":"28"

    }
    r = rq.post(url,data,headers=headers)
    content = r.text.encode("utf8")
    txt =  json.loads(content)['data']
    return txt

"""
删除重复字段
"""
def removeRepeart():
    l = []
    files =open(CSV_FILE_NAME,'rb')
    for line in files:
        l.append(line)

        # 去除重复,顺序不变
    l = sorted(set(l),key=l.index)
    csvfile = file(result_filename,'wb')
    csvfile.writelines(l)
    csvfile.close()


# 开始时间
DATA_FROM="2017-1-3"
# 截止到今天之后多少天
DATA_DELAY =7
# 爬虫爬取周期(/天)
REPTILE_CYCLE = 5

if __name__ == '__main__':
#     初始化环境
    initFile()
#     开始时间
    dataFrom = datetime.datetime.strptime(DATA_FROM,'%Y-%m-%d')
    dataNow  =datetime.datetime.now()
#     未来N天
    delta = datetime.timedelta(days = DATA_DELAY)
    dataTo = dataNow + delta

    allsecond = REPTILE_CYCLE*86400
#     按照五天为一个爬取周期  五天一共432000秒
    for i in xrange(int(time.mktime(dataFrom.timetuple())), int(time.mktime(dataTo.timetuple())), allsecond):
        try:
            dataStart =  datetime.date.fromtimestamp(i)
            dataEnd = datetime.date.fromtimestamp(i+allsecond)
            dataStart_str = str(dataStart)
            dataEnd_str = str(dataEnd)
            # print "正在获取",dataStart_str,"--",dataEnd_str
            html_str = getHTML(dataStart_str,dataEnd_str)
            l = getEconomicCalendar_List(html_str)
            if len(l) == 0:
                print "can't get data ,list size = 0"
                continue
            writeToCsv(l,CSV_FILE_NAME)

            #去除重复字段
            removeRepeart()
        except Exception as err:
            continue
