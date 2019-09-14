#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:俊坚
# datetime:2019/9/4 22:16
# software: PyCharm


import requests
import re
import json
url = 'http://events.sports.sina.com.cn/bps/peony/mersh/beitai/fiba/live/livejs?leagueid=433&scheduleid=100023567&dpc=1'
headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
        }

response = requests.get(url, headers = headers)
# print(response.encoding)
# response.encoding = 'utf-8'
# print(response.text.decode('utf-8'))
print(response.text)
# print(str(response.content,'utf-8'))
# matchdata_text = str(response.content,'utf-8')
# matchdata_dicts = json.loads(matchdata_text)
# for key,values in  matchdata_dicts.items():
#     if key == 'homeplayerdata' :
#         for value in values:
#             # self.parser_playerdata(value)
#             print(value)
    # if key == 'hometeamdata' or key == 'visteamdata':
        # print(values)
        # for value in values:
        #     print(value)


# schedule_data = re.findall(r'"data":(.*?)\}\}\);\}catch\(e\)\{\};', text)
# schedule_dicts = json.loads(schedule_data[0])
# for key,value in  schedule_dicts.items():
#     for schedule in value:
#         print(schedule)
# # print(schedule_dict)