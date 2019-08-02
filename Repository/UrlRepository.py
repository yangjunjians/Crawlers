#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:俊坚
# datetime:2019/7/31 22:23
# software: PyCharm

from database.dblink import RedisClent

class UrlRepository(object):
    def __init__(self,website):
        self.website = website
        self.highlevel_db = RedisClent('highlevel', self.website)
        self.lowlevel_db = RedisClent('lowlevel', self.website)

    def urlPop(self):
        url = self.highlevel_db.popurl()
        if not url:
            url = self.lowlevel_db.popurl()
        return  url

    def addHigh(self,url):
        self.highlevel_db.addUrl(url)

    def addlow(self,url):
        self.lowlevel_db.addUrl(url)