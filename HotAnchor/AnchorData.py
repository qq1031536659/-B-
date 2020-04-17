# coding:UTF-8
import requests, os, json, time
import sqlite3
import pandas as pd
import smtplib# 发送邮件模块
from email.mime.text import MIMEText# 定义邮件内容
from email.mime.multipart import MIMEMultipart# 用于传送附件
import time
import datetime
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
yesterday_start_time = int(time.mktime(time.strptime(str(yesterday), '%Y-%m-%d')))
yesterday_end_time = int(time.mktime(time.strptime(str(today), '%Y-%m-%d'))) - 1
today_start_time = yesterday_end_time + 1
today_end_time = int(time.mktime(time.strptime(str(tomorrow), '%Y-%m-%d'))) - 1
morningEight = today_start_time + 28800
tomorrowEight = today_end_time + 28800
yesterdaystart = yesterday_start_time + 28800
nowtime = int(time.time())
#娱乐分区热门直播
url = "https://api.live.bilibili.com/room/v3/area/getRoomList?platform=web&parent_area_id=1&cate_id=0&area_id=199&sort_type=sort_type_55&page=1&page_size=30&tag_version=1"
r = requests.get(url)
a = r.content  # .content直接获取字节流数据，解决windows-1254编码
html = json.loads(a)['data']['list']
payload = []
payload_copy = []
onload = []
# 此处做时间判断是否是七点59
from datetime import datetime
a = int(time.time())  # 当前时间
c = datetime.fromtimestamp(a).strftime('%H:%M')  # 格式转换
error = ''
file_handle=open('AnchorData_start.txt',mode='w+')
file_handle.write('endtime:' + str(datetime.fromtimestamp(int(time.time()))))

# if False:
if str(c) != '07:59':
    cx = sqlite3.connect("./Anchor_Data.db")
    cu = cx.cursor()
    try:
        cu.execute(
            "create table AnchorData (timesetup integer,uid integer(20),uname varchar(20),max_hot integer,live_start_time varchar(20),live_end_time varchar(20),airtime varchar(10),sum_gift_price integer,charge_gift_price integer,free_gift_price integer,charge_gift_sender integer,focus_grouth integer,msg_count integer,msg_sender integer,gift1 varchar(50),gift2 varchar(50),gift3 varchar(50),gift4 varchar(50),gift5 varchar(50),gift6 varchar(50))")
    except Exception:
        error = '表存在'
    for result in html:
        if result['online'] >= 10000:
            roomid = str(result['roomid'])
            xhl_url = "https://www.xiaohulu.com/apis/bd/index/anchor/anchorLiveRecord?platId=15&roomId=" + roomid + "&type=1&dateId=&page=1"
            r = requests.get(xhl_url)
            a = r.text
            if len(json.loads(a)['data']['data']) != 0:
                xhl_html = json.loads(a)['data']['data'][0]
                gift_url = "https://www.xiaohulu.com/apis/bd/index/anchor/analysisAnchorLiveFansData?platId=15&roomId=" + roomid + "&taskId=" + \
                           xhl_html['task_id']
                r = requests.get(gift_url)
                a = r.text
                gift_html = json.loads(a)['data']['gift']['gift_rank']
                if xhl_html['live_end_time'] == None:
                    live_end_time = '未下播'
                else:
                    live_end_time = xhl_html['live_end_time']
                if nowtime < morningEight:
                    realtime = yesterdaystart
                else:
                    realtime = morningEight
                content = {
                    'timesetup': realtime,
                    'uid': result['uid'],
                    'uname': result['uname'],
                    'max_hot': result['online'],
                    'live_start_time': xhl_html['live_start_time'],
                    'live_end_time': live_end_time,
                    'airtime': xhl_html['airtime'],
                    'sum_gift_price': xhl_html['sum_gift_price'],
                    'charge_gift_price': xhl_html['charge_gift_price'],
                    'free_gift_price': xhl_html['free_gift_price'],
                    'charge_gift_sender': xhl_html['charge_gift_sender'],
                    'focus_grouth': xhl_html['focus_grouth'],
                    'msg_count': xhl_html['msg_count'],
                    'msg_sender': xhl_html['msg_sender'],

                }
                for gift_value in gift_html:
                    if len(gift_html) == 6:
                        try:
                            content[gift_value['name']] = gift_value['name'] + ':' + str(
                                gift_value['gift_id_value'])
                        except Exception:
                            content['礼物'] = '小葫芦还未记录'
                    else:
                        try:
                            content[gift_html[gift_value]['name']] = gift_value['name'] + ':' + str(
                                gift_value['gift_id_value'])
                        except Exception:
                            content['礼物'] = '小葫芦还未记录'
            else:
                if nowtime < morningEight:
                    realtime = yesterdaystart
                else:
                    realtime = morningEight
                content = {
                    'timesetup': realtime,
                    'uid': result['uid'],
                    'uname': result['uname'],
                    'max_hot': result['online'],
                    'live_start_time': '刚开播不到一个小时',
                    'live_end_time': '小葫芦还未记录',
                    'airtime': '小葫芦还未记录',
                    'sum_gift_price': '小葫芦还未记录',
                    'charge_gift_price': '小葫芦还未记录',
                    'free_gift_price': '小葫芦还未记录',
                    'charge_gift_sender': '小葫芦还未记录',
                    'focus_grouth': '小葫芦还未记录',
                    'msg_count': '小葫芦还未记录',
                    'msg_sender': '小葫芦还未记录',
                }
            payload.append(content)

    cu.execute("select * from AnchorData")  # 获取数据库中的数据
    data = cu.fetchall()
    if data != []:
        for result in data:  # 获取现有数据库中的数据
            payload_copy.append(result)
        payload_real = []
        for paydata in payload_copy:
            arr = []
            for p in paydata:
                arr.append(p)
            payload_real.append(arr)
        for new_msg in payload:  # payload为新的数据
            same = True
            for result in payload_real:  # payload_real为原始数据
                if result[0] != new_msg['timesetup']:# 先判断时间戳，判断是不是当天的
                    break
                else:
                    if result[1] == new_msg['uid']:
                        if result[3] < new_msg['max_hot']:
                            arr = []
                            for data in new_msg:
                                arr.append(new_msg[data])
                            result = arr
                            # payload_real.append(result)
                        else:
                            arr = []
                            for data in new_msg:
                                arr.append(new_msg[data])
                            arr[3] = result[3]
                            result = arr
                            # payload_real.append(result)
                        same = False
                        break
            if same == True:
                arr = []
                for a in new_msg:
                    arr.append(new_msg[a])
                payload_real.append(arr)
        cu.execute("delete from AnchorData")  # 删除所有数据
        cx.commit()

        for d in payload_real:
            arr = []
            for da in d:
                arr.append(da)
            if len(arr) < 20:
                i = 20 - len(arr)
                while i:
                    arr.append('0')
                    i = i - 1
            cx.execute("insert into AnchorData('timesetup','uid','uname','max_hot','live_start_time','live_end_time','airtime','sum_gift_price','charge_gift_sender','free_gift_price','charge_gift_sender','focus_grouth','msg_count','msg_sender','gift1','gift2','gift3','gift4','gift5','gift6') values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",arr)
            cx.commit()
    else:
        for d in payload:
            arr = []
            for da in d:
                arr.append(d[da])
            if len(arr) < 20:
                i = 20 - len(arr)
                while i:
                    arr.append('0')
                    i = i - 1
            cx.execute("insert into AnchorData('timesetup','uid','uname','max_hot','live_start_time','live_end_time','airtime','sum_gift_price','charge_gift_sender','free_gift_price','charge_gift_sender','focus_grouth','msg_count','msg_sender','gift1','gift2','gift3','gift4','gift5','gift6') values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",arr)
            cx.commit()
else:
    cx = sqlite3.connect("./Anchor_Data.db")
    cu = cx.cursor()
    try:
        cu.execute("create table AnchorData (timesetup integer,uid integer,uname varchar(20),max_hot integer,live_start_time varchar(20),live_end_time varchar(20),airtime varchar(10),sum_gift_price integer,charge_gift_price integer,free_gift_price integer,charge_gift_sender integer,focus_grouth integer,msg_count integer,msg_sender integer,gift1 varchar(50),gift2 varchar(50),gift3 varchar(50),gift4 varchar(50),gift5 varchar(50),gift6 varchar(50))")
    except Exception:
        error = '表存在'
    cu.execute("select * from AnchorData")  # 获取数据库中的数据
    data = cu.fetchall()
    if data != []:
        for result in data:
            payload.append(result)
        payload = sorted(payload, key=lambda x: (x[3]), reverse=True)  # 按第三个字段(max_hot)倒序输出
        # 生成excel表
        df = pd.DataFrame()  # 最后转换得到的结果
        df0 = []
        arr_header = []
        for line in payload:
            arr = []
            for value in line:
                arr.append(value)
            if len(line) < 20:
                i = 20 - len(line)
                while i:
                    arr.append('0')
                    i = i - 1
            arr[0] = datetime.fromtimestamp(arr[0]).strftime('%Y-%m-%d')
            df0.append(arr)
        df1 = pd.DataFrame(df0)
        df = df.append(df1)
        a = int(time.time())  # 当前时间
        c = datetime.fromtimestamp(a).strftime('%Y-%m-%d')  # 格式转换
        # # 在excel表格的第1列写入, 不写入index
        df.to_excel('./' + c + '热门主播信息.xlsx',
                    header=['日期','uid', '直播ID', '最高热度', '开始时间', '结束时间', '直播时长', '总礼物价值', '付费礼物价值', '免费礼物价值', '付费人数',
                            '新增订阅', '弹幕条数', '弹幕人数', '礼物1', '礼物2', '礼物3', '礼物4', '礼物5', '礼物6'],
                    sheet_name='Data',
                    startcol=0, index=True)
        # 发附件邮件
        smtpserver = 'smtp.exmail.qq.com'  # 该邮箱服务器(此处为腾讯企业邮箱)
        user = 'zhangyilong@smile-tech.com'  # 用于登录邮箱的账号
        password = 'jL6oxVXZwedtDJ8g'  # 用户登录邮箱的授权码
        sender = 'zhangyilong@smile-tech.com'  # 发送人邮箱
        receives = ['dwj@smile-tech.com', 'zl@smilebeta.com', '1031536659@qq.com']  # 接收人邮箱
        subject = c + '热门主播信息'
        content = ' '

        send_file = open('./' + c + '热门主播信息.xlsx', 'rb').read()

        att = MIMEText(send_file, 'base64', 'utf-8')
        att["Content-Type"] = 'application/octet-stream'
        # att["Content-Disposition"] = 'attachment;filename="' + c + '热门主播.xlsx"'# 英文文件名用
        att.add_header("Content-Disposition", "attachment", filename=("gbk", "", c + "热门主播信息.xlsx"))  # 中文文件名用

        msgRoot = MIMEMultipart()
        msgRoot.attach(MIMEText(content, 'html', 'utf-8'))
        msgRoot['subject'] = subject
        msgRoot['From'] = sender
        msgRoot['To'] = ','.join(receives)
        msgRoot.attach(att)

        smtp = smtplib.SMTP_SSL(smtpserver, 465)

        smtp.helo(smtpserver)
        smtp.ehlo(smtpserver)
        smtp.login(user, password)


        smtp.sendmail(sender, receives, msgRoot.as_string())

        smtp.quit()


        # 删除"./"目录下后缀名为xlsx的文件
        path = './'
        for root, dirs, files in os.walk(path):
            for name in files:
                if name.endswith(".xlsx"):  # 填写规则
                    os.remove(os.path.join(root, name))