# -*- coding: utf-8 -*-

import datetime
import pandas as pd
import time
import json
from pymongo import MongoClient

"""
导入csv到mongodb
"""

# mongoDB IP地址
mongo_ip = "127.0.0.1"
# mongoDB 端口
mongo_port = 27017
# mongoDB 数据库名
mongo_db = "ec"
# mongoDB 集合名
mongo_collection = "all_ecs"
# csv文件地址
csv_path = "EURUSD_UTC_1 Min_Bid_2016.01.01_2017.07.24.csv"


conn = MongoClient(mongo_ip, 27017)
db = conn[mongo_db]  #连接mydb数据库，没有则自动创建


def get_timestamp(datestr):
    # print datestr
    d = datetime.datetime.strptime(datestr, '%Y.%m.%d %H:%M:%S')
    return int(time.mktime(d.timetuple()))

df = pd.read_csv(csv_path,skiprows =1,names=["datetime","open","high","low","close","vol"])
# df['timestamp'] = df.apply(lambda x:get_timestamp(x[0]),axis=1)
jarr = json.loads(df.to_json(orient='records'))
table = db[mongo_collection]
# json_arry = []
# for val in jarr:
#     timestamps = val['timestamp']
#     if table.find({"timestamp":timestamps}).count() <= 0:
#         json_arry.append(val)
if len(jarr) > 0:
    table.insert_many(jarr)