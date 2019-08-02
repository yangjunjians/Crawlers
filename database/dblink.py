#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:俊坚
# datetime:2019/7/31 22:07
# software: PyCharm

import random
import redis
from config.configdata import *
import  pymysql

class RedisClent(object):
    def __init__(self, type, website, host=REDIS_HOST, port=REDIS_POST, password=REDIS_PASSWORD):
        """
        初始化Redis连接
        :param type: Hash存储类型，account or Cookies
        :param website: 网站
        :param host:地址
        :param port:端口号
        :param password:密码
        """
        self.db = redis.StrictRedis(host=host,port=port,password=password,decode_responses=True)
        self.type = type
        self.website = website
    def Hash_name(self):
        """
        获取Hash名称
        :return:Hash名称
        """
        return "{type}:{website}".format(type=self.type,website=self.website)

    def setHash(self,username,value):
        """
        设置键值对
        :param username: key：用户名
        :param value: 密码 or Cookies
        :return:
        """
        return self.db.hset(self.Hash_name(),username,value)
    def getHash(self,username):
        """
        根据key返还对应value
        :param username: key
        :return:
        """
        return self.db.hget(self.Hash_name(),username)
    def deleteHash(self,username):
        """
        根据key删除键值对
        :param username:
        :return:
        """
        return self.db.hdel(self.Hash_name(),username)
    def count(self):
        """
        获取Hash长度
        :return:
        """
        return self.db.hlen(self.Hash_name())
    def random(self):
        """
        获取随机Cookies
        :return:随机Cookies
        """
        return random.choice(self.db.hvals(self.Hash_name()))
    def usernames(self):
        """
        获取所有账户
        :return: 所有用户名
        """
        return self.db.hkeys(self.Hash_name())
    def all(self):
        """
        获取所有键值对
        :return:
        """
        return self.db.hgetall(self.Hash_name())

    def Listname(self):
        """
        获取url队列名称
        :return:
        """
        return "{type}:{website}".format(type=self.type,website=self.website)

    def allurl(self,start=0,end=-1):
        """
        获取指定list中的url
        :return:
        """
        return self.db.lrange(self.Listname(),start,end)

    def addUrl(self,url):
        """
        添加url进队列
        :param urllevel: url优先级
        :param url: url
        :return:
        """
        # listname = self.Listname().get(urllevel)
        self.db.lrem(self.Listname(),0,url)
        self.db.lpush(self.Listname(),url)

    def popurl(self):
        """
        获取url
        :param urllevel:
        :return:
        """
        # listname = self.Listname().get(urllevel)
        return self.db.rpop(self.Listname())

class MySQLClient(object):
    def __init__(self, host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE, charset=MYSQL_CHARSET):
        self.conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, charset=charset)

    def insert(self,table,data):
        """
        :param table: 表名
        :param data: 数据 dict
        :return:
        """
        cursor = self.conn.cursor()
        keys = ','.join(data.keys())
        values = ','.join(['%s']*len(data))
        sql = 'insert into {table}({key}) values({value});'.format(table=table,key=keys,value=values)
        try:
            if cursor.execute(sql,tuple(data.values())):
                self.conn.commit()
                print('inserted Successfully')
        except Exception as e:
            print('insert faided')
            print("error：", str(e))
            self.conn.rollback()
        finally:
            cursor.close()


    def update(self,table,data):
        """
        :param table: 表名
        :param data: 数据 dict
        :return:
        """
        cursor = self.conn.cursor()
        keys = ','.join(data.keys())
        values = ','.join(['%s']*len(data))

        sql = 'insert into {table} ({key}) values ({value}) on duplicate key update '.format(table=table,
                                                                                            key=keys,value=values)
        update = ','.join(["{key} = %s".format(key=key) for key in data])
        sql += update

        try:
            if cursor.execute(sql,tuple(data.values())*2):
                self.conn.commit()
                print('updated Successfully')
        except Exception as e:
            print('update Failed')
            print("error：", str(e))
            self.conn.rollback()
        finally:
            cursor.close()

    def delete(self,table,condition):
        cursor = self.conn.cursor()
        sql = 'delete from {table} where {condition}'.format(table=table,condition=condition)
        try:
            if cursor.execute(sql):
                self.conn.commit()
                print('deleted successfully')
        except Exception as e:
            print('delete Failed')
            print("error：", str(e))
            self.conn.rollback()
        finally:
            cursor.close()

    def select(self,table):
        cursor = self.conn.cursor()
        sql = 'select * from {table}'.format(table=table)
        try:
            if cursor.execute(sql):
                row = cursor.fetchone()
                while row:
                    print('ROW:',row)
                    row = cursor.fetchone()
        except Exception as e:
            print('select Failed')
            print("error：", str(e))
        finally:
            cursor.close()

    def closeClient(self):
        self.conn.close()



if __name__ == '__main__':
    MySQLClient = MySQLClient()
    date = {
        'account':'20180105121',
        'name':'刘彦彤',
        'gender':'女',
        'phone':'13266100048',
        'email':'liuyantong@163.com'
    }
    MySQLClient.insert('teacher',date)
