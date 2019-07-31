#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:俊坚
# datetime:2019/7/31 22:12
# software: PyCharm

from database.dblink import RedisClent
from login.weiboCookies import WeiboCookies
import json


class CookiesGenerator(object):
    def __init__(self,website='default'):
        """
        父类
        初始化站点名称，数据库连接，浏览器
        :param website:
        """
        self.website = website
        self.cookies_db = RedisClent('cookies',self.website)
        self.account_db = RedisClent('account',self.website)


    def new_cookies(self,username,password):
        """
        新生成Cookies，子类重写
        :param username: 用户名
        :param password: 密码
        :return:
        """
        raise NotImplementedError

    def run(self):
        """
        运行，获取用户名，并依此模拟登陆
        :return:
        """
        account_usernames = self.account_db.usernames()
        cookies_usernames = self.cookies_db.usernames()

        for username in account_usernames:
            if not username in cookies_usernames:
                password = self.account_db.getHash(username)
                print('正在生成 ',username,' cookies')
                cookies = json.dumps(self.new_cookies(username,password))
                if self.cookies_db.setHash(username,cookies):
                    print(username,'保存cookies成功！')
                else:
                    print(username,'保存cookies失败！')

class weiboCookiesGenerator(CookiesGenerator):
    def __init__(self,website = 'weibo'):
        """
        :param website:
        """
        CookiesGenerator.__init__(self,website)
        self.website = website

    def new_cookies(self,username,password):
        return  WeiboCookies(username,password).main()



if __name__ == '__main__':
    generatotr = weiboCookiesGenerator()
    generatotr.run()