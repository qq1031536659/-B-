import sqlite3
import time
import datetime
today = datetime.date.today()
yesterday_end_time = int(time.mktime(time.strptime(str(today), '%Y-%m-%d'))) - 1
today_start_time = yesterday_end_time + 1
morningEight = today_start_time + 28800
time1 = int(morningEight) - 86400*7# 时间戳减七天（一天的时间戳为86400）

cx = sqlite3.connect("./Anchor_Data.db")
cu = cx.cursor()
# # 删除现有库中七天前的数据
cu.execute("delete from AnchorData where timesetup < " + str(time1))
cx.commit()

