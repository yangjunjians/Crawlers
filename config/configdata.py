#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:俊坚
# datetime:2019/7/31 22:05
# software: PyCharm

#redis 地址
REDIS_HOST = '192.168.1.105'

#redis 端口
REDIS_POST = 6379

#redis 密码
REDIS_PASSWORD = 'redis'

#MySQL 地址
MYSQL_HOST = '127.0.0.1'
#MySQL 端口
MYSQL_PORT =  3306
#MySQL 用户名
MYSQL_USER = 'root'
#MySQL 密码
MYSQL_PASSWORD = '1234567'
#MySQL 数据库
MYSQL_DATABASE = 'spiders'
#MySQL 字符集
MYSQL_CHARSET = 'utf8'

#cookies生成器使用的浏览器
BROWSER_TYPE = 'chrome'

#站点对应的生成类
GENERATOR_MAP = {
    'weibo':"WeiboCookiesGenerator"
}

#站点对应的测试类
TESTER_MAP = {
    'weibo':'WeiboVailTester'
}

#站点生成CookiesURL
GENERATURL_MAP = {
    'weibo':'https://weibo.com/'
}

#站点测试URL
TESTURL_MAP ={
    'weibo':'https://d.weibo.com/'
}

weibo_info = {
    'username':'无',
    'authentication':'无',
    'vip_level':0,
    'gender':'无',
    'introduction':'无',
    'followers_num':0,
    'fans_num':0,
    'weets_num':0,
    'city':'未知',
    'birthday':'无',
    'domain_name':'未知',
    'ID':'未知'
}