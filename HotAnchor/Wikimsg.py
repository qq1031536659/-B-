# 生成wiki格式的文本
import sqlite3, time
from datetime import datetime, timedelta
from mako.template import Template
class wiki:
    def wikidata(self):
        a = int(time.time())  # 当前时间
        c = datetime.fromtimestamp(a).strftime('%Y-%m-%d')  # 格式转换
        cx = sqlite3.connect("./Anchor_Data.db")
        cu = cx.cursor()
        cu.execute("select * from AnchorData")  # 获取数据库中的数据
        data = cu.fetchall()
        payload = []
        wikidata = []
        wikiheader = ['日期','uid', '直播ID', '最高热度', '开始时间', '结束时间', '直播时长', '总礼物价值', '付费礼物价值', '免费礼物价值', '付费人数',
                      '新增订阅', '弹幕条数', '弹幕人数', '礼物1', '礼物2', '礼物3', '礼物4', '礼物5', '礼物6']
        if data != []:
            for result in data:
                payload.append(result)
            payload = sorted(payload, key=lambda x: (x[3]), reverse=True)  # 按第三个字段(max_hot)倒序输出
        for arr in payload:
            json = {}
            i = 0
            while i != len(arr):
                if i == 0:
                    json[wikiheader[i]] = str(datetime.fromtimestamp(arr[0]).strftime('%Y-%m-%d'))
                else:
                    json[wikiheader[i]] = str(arr[i])
                i += 1
            wikidata.append(json)
        getjson = wikidata
        gameList = wikiheader
        jsondata = getjson
        jsonline = getjson

        tableTemplate = Template(filename='line.html')
        tableText = tableTemplate.render(gameList=gameList, result=jsonline, datestr=c)

        trTemplate = Template(filename='table.html')
        trText = trTemplate.render(gameList=gameList, result=jsondata, datestr=c)

        tableandtr = tableText + trText
        return tableandtr

if __name__ == '__main__':
    a = wiki()
    print(a.wikidata())