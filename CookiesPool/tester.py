#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:俊坚
# datetime:2019/7/31 22:15
# software: PyCharm
from database.dblink import RedisClent
import json
from config.configdata import *
import requests

class ValidTester(object):
    def __init__(self,website = 'default'):
        self.website = website
        self.account_db = RedisClent('account',self.website)
        self.cookies_db = RedisClent('cookies',self.website)

    def test(self,username,cookies):
        raise NotImplementedError

    def run(self):
        cookies_group = self.cookies_db.all()
        for username,cookies in cookies_group.items():
            self.test(username,cookies)

class weiboValidTester(ValidTester):
    def __init__(self,website = 'weibo'):
        ValidTester.__init__(self,website)

    def test(self,username,cookies):
        print('正在测试:',username)
        try:
            cookies = json.loads(cookies)
        except TypeError:
            print('cookies 格式不合法',username)
            self.cookies_db.deleteHash(username)
            print('删除cookies',username)
            return
        try:
            test_url = TESTURL_MAP[self.website]
            response = requests.get(test_url,cookies=cookies,timeout=5,allow_redirects=False)
            if response.status_code == 200:
                print('cookies有效',username)
            else:
                print(response.status_code)
                print('cookies 失效',username)
                self.cookies_db.deleteHash(username)
                print('删除cookies',username)
        except ConnectionError as e:
            print('发生异常',e.args)




if __name__ == '__main__':
    tester = weiboValidTester()
    tester.run()
