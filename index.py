# coding:UTF-8
import requests, os, redis, json, time
import pandas as pd
from datetime import datetime
import smtplib# 发送邮件模块
from email.mime.text import MIMEText# 定义邮件内容
from email.mime.multipart import MIMEMultipart# 用于传送附件
#娱乐分区热门直播
url = "https://api.live.bilibili.com/room/v3/area/getRoomList?platform=web&parent_area_id=1&cate_id=0&area_id=199&sort_type=sort_type_55&page=1&page_size=30&tag_version=1"
r = requests.get(url)
a = r.content# .content直接获取字节流数据，解决windows-1254编码
html = json.loads(a)['data']['list']
payload = []
payload_copy = []
onload = []
# 连接Redis
re = redis.Redis(host='127.0.0.1', password='', port=6379)

# 此处做时间判断是否是七点59
a = int(time.time())    #当前时间
c = datetime.fromtimestamp(a).strftime('%H:%M')    #格式转换
if str(c) != '07:59':
    for result in html:
        if result['online'] >= 10000:
            roomid = str(result['roomid'])
            xhl_url = "https://www.xiaohulu.com/apis/bd/index/anchor/anchorLiveRecord?platId=15&roomId=" + roomid + "&type=1&dateId=&page=1"
            r = requests.get(xhl_url)
            a = r.text
            if len(json.loads(a)['data']['data']) != 0:
                xhl_html = json.loads(a)['data']['data'][0]
                gift_url = "https://www.xiaohulu.com/apis/bd/index/anchor/analysisAnchorLiveFansData?platId=15&roomId=" + roomid + "&taskId=" + xhl_html['task_id']
                r = requests.get(gift_url)
                a = r.text
                gift_html = json.loads(a)['data']['gift']['gift_rank']
                if xhl_html['live_end_time'] == None:
                    live_end_time = '未下播'
                else:
                    live_end_time = xhl_html['live_end_time']
                content = {
                    'uid': result['uid'],
                    'uname': result['uname'],
                    'max_hot': xhl_html['max_hot'],
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
                            content[gift_value['name']] = gift_value['name'] + ':' + str(gift_value['gift_id_value'])
                        except Exception:
                            content['礼物'] = '小葫芦未记录'
                    else:
                        try:
                            content[gift_html[gift_value]['name']] = gift_value['name'] + ':' + str(gift_value['gift_id_value'])
                        except Exception:
                            content['礼物'] = '小葫芦未记录'
            else:
                content = {
                    'uid': result['uid'],
                    'uname': result['uname'],
                    'max_hot': 0,
                    'live_start_time': '刚开播不到一个小时',
                    'live_end_time': '小葫芦未记录',
                    'airtime': '小葫芦未记录',
                    'sum_gift_price': '小葫芦未记录',
                    'charge_gift_price': '小葫芦未记录',
                    'free_gift_price': '小葫芦未记录',
                    'charge_gift_sender': '小葫芦未记录',
                    'focus_grouth': '小葫芦未记录',
                    'msg_count': '小葫芦未记录',
                    'msg_sender': '小葫芦未记录',
                }
            payload.append(content)
            # r.hexists('zhibo', result['uid'])# 判断存在与否
            # r.lpush('zhibo', content)# 将爬取到的数据存到redis里

    if len(re.lrange('虚拟偶像热门主播', 0, -1)) != 0:
        for result in re.lrange('虚拟偶像热门主播', 0, -1):# 获取现有数据库中的数据
            payload_copy.append(json.loads(result))
        for new_msg in payload:# payload为刚运行时所爬到的数据
            same = True
            for result in payload_copy:# 做双重循环覆盖重复的保留原有的，添加现有的
                if result['uid'] == new_msg['uid']:
                    result = new_msg
                    same = False
                    break
            if same == True:
                payload_copy.append(new_msg)
        while len(re.lrange('虚拟偶像热门主播', 0, -1)):# 删除现有的库
            re.lpop("虚拟偶像热门主播")
        for data in payload_copy:# 将两者的结合存在数据库中
            re.lpush('虚拟偶像热门主播', json.dumps(data))
    else:
        for data in payload:
            re.lpush('虚拟偶像热门主播', json.dumps(data))
else:
    if len(re.lrange('虚拟偶像热门主播', 0, -1)) != 0:
        for result in re.lrange('虚拟偶像热门主播', 0, -1):
            payload.append(json.loads(result))
        payload = sorted(payload, key=lambda x: (x['max_hot']), reverse=True)# 按max_hot字段倒序输出
        # 生成excel表
        df = pd.DataFrame()  # 最后转换得到的结果
        df0 = []
        arr_header = []
        for line in payload:
            arr = []
            for value in line:
                arr.append(line[value])
            if len(line) < 13:
                i = 13 - len(line)
                while i:
                    arr.append(0)
                    i = i - 1
            df0.append(arr)
        df1 = pd.DataFrame(df0)
        df = df.append(df1)
        a = int(time.time())  # 当前时间
        c = datetime.fromtimestamp(a).strftime('%Y-%m-%d')  # 格式转换
        # 在excel表格的第1列写入, 不写入index
        df.to_excel('./' + c + '热门主播信息.xlsx', header=['uid', '直播ID', '最高热度', '开始时间', '结束时间', '直播时长', '总礼物价值', '付费礼物价值', '免费礼物价值', '付费人数', '新增订阅', '弹幕条数', '弹幕人数', '礼物1', '礼物2', '礼物3', '礼物4', '礼物5', '礼物6'], sheet_name='Data',
                    startcol=0, index=True)

        #发附件邮件
        smtpserver = 'smtp.qq.com'
        user = '1031536659@qq.com'
        password = 'eoreqlhyzsyabahf'

        sender = '1031536659@qq.com'
        receives = ['1031536659@qq.com']
        subject = c + '热门主播信息'
        content = ' '

        send_file = open('./' + c + '热门主播信息.xlsx', 'rb').read()

        att = MIMEText(send_file, 'base64', 'utf-8')
        att["Content-Type"] = 'application/octet-stream'
        # att["Content-Disposition"] = 'attachment;filename="' + c + '热门主播.xlsx"'
        att.add_header("Content-Disposition", "attachment", filename=("gbk", "", c + "热门主播信息.xlsx"))

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

        print("Start send email...")

        smtp.sendmail(sender, receives, msgRoot.as_string())

        smtp.quit()
        print("Send End!")

        # 删除现有库中的数据
        while len(re.lrange('虚拟偶像热门主播', 0, -1)):
            re.lpop("虚拟偶像热门主播")

        # 删除"./"目录下后缀名为xlsx的文件
        path = './'
        for root, dirs, files in os.walk(path):
            for name in files:
                if name.endswith(".xlsx"):             #  填写规则
                    os.remove(os.path.join(root, name))