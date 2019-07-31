#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:俊坚
# datetime:2019/7/31 22:16
# software: PyCharm

from  database.dblink import RedisClent
import  requests
import  json
class PageDownloader(object):
    def __init__(self, website='default'):
        self.website = website
        # self.account_db = RedisClent('account', self.website)
        self.cookies_db = RedisClent('cookies', self.website)

    def download(self,url):
        raise NotImplementedError

class weiboDownloader(PageDownloader):
    def __init__(self,website = 'weibo'):
        PageDownloader.__init__(self,website)

    def download(self,url):

        cookies = json.loads(self.cookies_db.random())
        # cookies = {'LT': '1562599953', 'SUB': '_2A25wJxJBDeRhGeFP7FcY9SbIwjiIHXVTVQSJrDV_PUJbm9B-LRatkW9NQR8eS0TyzrX5K4nQcggCBnfYL_zmpgb1', 'SUBP': '0033WrSXqPxfM725Ws9jqgMF55529P9D9Whp-Ia.AXNpTLPF85nhG5UZ5NHD95QNeKMf1K-RSh.XWs4DqcjMi--NiK.Xi-2Ri--ciKnRi-zN1K-ESKn4eozRSBtt', 'login': '9da7cd806ada2c22779667e8e1c039c2'}
        try:
            response = requests.get(url, cookies=cookies, timeout=5, allow_redirects=False)
            if response.status_code == 200:
                return {
                    'status':1,
                    'text':response.text
                }
            else :
                return {
                    'status':2,
                    'text':response.status_code
                }
        except ConnectionError as e:
            print('发生异常',e.args)

if __name__ == '__main__':
    downloader = weiboDownloader()
    page = downloader.download('https://d.weibo.com/')
    print(page.get('text'))