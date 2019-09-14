#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:俊坚
# datetime:2019/9/5 21:15
# software: PyCharm

import re
import requests
import json
from database.dblink import MySQLClient
from config.configdata import team_data,schedule_data,player_matchdata,team_matchdata
class WorldCupParser(object):
    def __init__(self):
        self.mysqlclent = MySQLClient()
        self.team = team_data
        self.schedule_data = schedule_data
        self.player_matchdata =player_matchdata
        self.team_matchdata = team_matchdata


    def download(self,url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
        }
        if url.startswith('http://events.sports.sina.com.cn/bkwc/'):
            response = requests.get(url, headers=headers)
            text = response.text.encode('utf-8').decode('unicode_escape')

        else:
            response = requests.get(url, headers=headers)
            text = str(response.content, 'utf-8')
        return text



    def parser_schedule(self,schedule):
        condition = 'match_id = \'{}\''.format(schedule['match_id'])
        query = self.mysqlclent.select_where('schedule',condition)
        if schedule['status']  == '3' and  not query:
            for key, value in schedule.items():
                if key in self.schedule_data.keys()  and value:
                    self.schedule_data[key] = value
            self.mysqlclent.insert('schedule', self.schedule_data)


    def parser_team(self,schedule):
        if schedule['date'] == '2019-08-31' or schedule['date'] == '2019-09-01':
            self.team['id']  = schedule['beitai_team1_tid']
            self.team['tid'] = schedule['team1_tid']
            self.team['tname'] = schedule['team1_name']
            self.team['tlogo'] = schedule['team1_logo']
            self.mysqlclent.insert('team',self.team)
            self.team['id']  = schedule['beitai_team2_tid']
            self.team['tid'] = schedule['team2_tid']
            self.team['tname'] = schedule['team2_name']
            self.team['tlogo'] = schedule['team2_logo']
            self.mysqlclent.insert('team',self.team)

    def parser_playerdata(self,matchdata):
        condition = 'ScheduleID=\'{}\' and TeamID=\'{}\' and  PlayerID=\'{}\''.format(matchdata['ScheduleID'],matchdata['TeamID'],matchdata['PlayerID'])
        query = self.mysqlclent.select_where('player_matchdata', condition)
        if not query:
            for key, value in matchdata.items():
                if key in self.player_matchdata.keys():
                    self.player_matchdata[key] = value
            self.mysqlclent.insert('player_matchdata', self.player_matchdata)

    def parser_teamdata(self,matchdata):
        condition = 'ScheduleID=\'{}\' and TeamID=\'{}\' '.format(matchdata['ScheduleID'],matchdata['TeamID'])
        query = self.mysqlclent.select_where('team_matchdata', condition)
        if not query:
            for key, value in matchdata.items():
                if key in self.team_matchdata.keys():
                    self.team_matchdata[key] = value
            self.mysqlclent.insert('team_matchdata', self.team_matchdata)

    def main(self):
        url = 'http://events.sports.sina.com.cn/bkwc/api/beitai/dateschedule?callback=cb_get_date_schedule_c58aa18b_8ed7_48a6_a589_72c488239604&dpc=1'
        schedule_text = self.download(url)
        schedule_data = re.findall(r'"data":(.*?)\}\}\);\}catch\(e\)\{\};',schedule_text)
        schedule_dicts = json.loads(schedule_data[0])
        for key, value in schedule_dicts.items():
            for schedule in value:
                self.parser_team(schedule)
                self.parser_schedule(schedule)
        matchid_lists = self.mysqlclent.select('schedule','match_id')
        for match_id in matchid_lists:
            matchdata_url = 'http://events.sports.sina.com.cn/bps/peony/mersh/beitai/fiba/live/livejs?leagueid=433&scheduleid={}&dpc=1 '.format(match_id)
            print(matchdata_url)
            matchdata_text = self.download(matchdata_url)
            matchdata_dicts = json.loads(matchdata_text)
            for key, values in matchdata_dicts.items():
                if key == 'homeplayerdata' or key == 'visplayerdata':
                    for value in values:
                        self.parser_playerdata(value)
                if key == 'hometeamdata' or key == 'visteamdata':
                    self.parser_teamdata(values)



if __name__ == '__main__':
    worldcup = WorldCupParser()
    worldcup.main()