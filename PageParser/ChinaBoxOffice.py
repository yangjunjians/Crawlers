#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:俊坚
# datetime:2019/8/29 22:35
# software: PyCharm

import requests
import  json
from  lxml import etree
from database.dblink import MySQLClient
import collections

def downloadpage(url):
    #页面内容获取
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
    }
    response = requests.get(url,headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return None

def parser_page(url):
    #解析电影详细页内容，获取导演以及演员
    text  = downloadpage(url)
    html = etree.HTML(text)
    actor_selectors = html.xpath('//*[@id="top"]/div[3]/div[2]/div/div[1]/div[2]/div[2]/ul/li[1]')
    actors = '/'.join(actor_selectors[0].xpath('//h5/a/text()')[:2])
    director_selectors = html.xpath('//*[@id="tabcont1"]/dl/dd[1]/p/a/text()')
    directors = '/'.join(director_selectors)
    return {
        'actor':actors,
        'director':directors
    }



def parser_json(jsonlist):
    #解析json数据，并保存至数据库
    mysqlclent = MySQLClient()
    for jsondate in json.loads(jsonlist):
        MovieUrl = 'http://www.cbooo.cn/m/'+jsondate.get('MovieID')
        actor_director = parser_page(MovieUrl)
        jsondate['url'] = MovieUrl
        jsondate['actor'] = actor_director.get('actor')
        jsondate['director'] = actor_director.get('director')
        mysqlclent.insert('chinamovie',jsondate)



def calculate(col):
    #统计演员以及导演名称的出现次数
    mysqlclent = MySQLClient()
    model = collections.defaultdict(lambda: 0)
    result_lists = mysqlclent.select('chinamovie',col)
    result_dict = {}
    for key,value in enumerate(result_lists):
        result_lists[key] = ''.join(value).split('/')
    features = [j for i in result_lists for j in i]
    for f in features:
        model[f] += 1
    for key,value in model.items():
        result_dict['name'] = key
        result_dict['count'] = value
        result_dict['type'] = col
        mysqlclent.insert('word_freq',result_dict)





if __name__ == '__main__':

    for i in range(5):
        URL = 'http://www.cbooo.cn/BoxOffice/getInland?pIndex={page}&t=0'.format(page=i+1)
        jsonlist = downloadpage(URL)
        parser_json(jsonlist)
    calculate('actor')
    calculate('director')
