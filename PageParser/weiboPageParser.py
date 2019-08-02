#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:俊坚
# datetime:2019/7/31 22:20
# software: PyCharm

from bs4 import BeautifulSoup
import re
import json
from database.dblink import RedisClent,MySQLClient
from DownLoad.DownLoader import weiboDownloader
from config.configdata import weibo_info


class weiboPageParser(object):
    def __init__(self):
        self.website = 'weibo'
        self.highlevel_db = RedisClent('highlevel', self.website)
        self.lowlevel_db = RedisClent('lowlevel', self.website)
        self.info_data = weibo_info
        self.mysqlclent = MySQLClient()

    def processListPage(self,page):
        """
        解析列表页获取文章页url 和下一页列表页url
        :param page:
        :return:
        """
        text = page.get('text')
        Overallsoup = BeautifulSoup(text, 'html.parser')
        script_list = Overallsoup.find_all('script')
        del script_list[0: 5]
        ma = re.compile(r'\{(.+?)\}')
        for script in script_list:
            result = ma.search(script.get_text()).group()
            try:
                data = json.loads(result, strict=False)
                if data.get('domid') == 'Pl_Core_F4RightUserList__4':
                    firstsoup = BeautifulSoup(data.get('html'), 'lxml')
                    urllist_selectors = firstsoup.select('dt.mod_pic')
                    # 获取详细页url
                    for urllist_selector in urllist_selectors:
                        detail_url = 'https:' + urllist_selector.select('a')[0]['href']
                        self.lowlevel_db.addUrl(detail_url)
                    # 获取下一页url
                    nexturl_list = firstsoup.select('div.W_pages')[0].select('a')[-1]
                    iscontain = re.search(r'^((?!href).)*$', str(nexturl_list))
                    if not iscontain:
                        next_url = 'https://d.weibo.com' + nexturl_list['href']
                        self.highlevel_db.addUrl(next_url)
                    else:
                        print('已经是最后一页')

                    break
            except Exception as e:
                print(str(e))


    def processDetailPage(self,page):
        """
        解析文章页，获取博主信息存储于MySQL
        :param page:ff
        :return:
        """
        text = page.get('text')
        pageurl = page.get('url')
        domain = re.search(r'.com\/(.+?)\?', str(pageurl))
        # 个性域名
        self.info_data['domain_name'] = domain.group()[5:-1]
        # id
        self.info_data['ID'] = re.findall(r'\[\'oid\'\]=\'(.*?)\'', text)[0]
        Overallsoup = BeautifulSoup(text, 'html.parser')
        script_list = Overallsoup.find_all('script')
        del script_list[0: 5]
        ma = re.compile(r'\{(.+?)\}')
        for script in script_list:
            result = ma.search(script.get_text()).group()
            try:
                data = json.loads(result, strict=False)
                if data.get('domid') == 'Pl_Official_Headerv6__1':
                    firstsoup = BeautifulSoup(data.get('html'), 'lxml')
                    # 昵称
                    self.info_data['username'] = firstsoup.select('h1.username')[0].get_text()
                    # 认证
                    auth = re.findall(r'<em class="W_icon icon_pf_(.*?)"', str(firstsoup.find_all('em')))
                    if auth:
                        if auth[0] == 'approve_gold':
                            self.info_data['authentication'] = '金V个人认证 '
                        elif auth[0] == 'approve':
                            self.info_data['authentication'] = '个人认证'
                        else :
                            self.info_data['authentication'] = '官方认证'
                    # 等级
                    level = re.findall(r'<em class="W_icon icon_member(.*?)"', str(firstsoup.find_all('em')))
                    if level and level[0] != '_dis':
                        self.info_data['vip_level'] = level[0]
                    # 性别
                    if firstsoup.i['class'][1].split('_')[2] == 'female':
                        self.info_data['gender'] = '0'
                    else :
                        self.info_data['gender'] = '1'
                    # 简介
                    self.info_data['introduction'] = firstsoup.select("div.pf_intro")[0].get_text().strip()
                if data.get('domid') == 'Pl_Core_T8CustomTriColumn__3':
                    secondsoup = BeautifulSoup(data.get('html'), 'lxml')
                    # 关注数
                    self.info_data['followers_num'] = secondsoup.select('strong')[0].get_text()
                    # 粉丝数
                    self.info_data['fans_num'] = secondsoup.select('strong')[1].get_text()
                    # 微博数
                    self.info_data['weets_num'] = secondsoup.select('strong')[2].get_text()
                if data.get('domid') == 'Pl_Core_UserInfo__6':
                    thirdsoup = BeautifulSoup(data.get('html'), 'lxml')
                    select_list = thirdsoup.select('.item_text.W_fl')
                    for key, value in enumerate(select_list):
                        if re.search(r'^((?!毕业于|简介：|个性域名：).)*$', value.get_text().strip()):
                            if key == 0:
                                #所在城市
                                self.info_data['city'] = value.get_text().strip()
                            else:
                                #生日
                                if re.search(r'.*年.*', value.get_text().strip()):
                                    self.info_data['birthday'] = value.get_text().strip()
                # if data.get('domid').startswith('Pl_Official_MyProfileFeed__20'):
                #     fourthsoup = BeautifulSoup(data.get('html'), 'lxml')
                #     domainStr = fourthsoup.select('.W_f14.W_fb.S_txt1')[0]['href']
                #     idStr = fourthsoup.select('.W_f14.W_fb.S_txt1')[0]['usercard']
                #     id = re.search(r'\d+', str(idStr))
                #
                #     # domain = re.search(r'.com\/(.+?)\?', str(domainStr))
                #     # #个性域名
                #     # self.info_data['domain_name'] = domain.group()[5:-1]
                #     #用户id

            except Exception as e:
                print(str(e))
        self.mysqlclent.insert('weibo_blogger', self.info_data)
    def get_info_data(self):
        for data in self.info_data.items():
            print(data)

    def init_url_repo(self,page):
        """
        初始化url仓库
        :param page:
        :return:
        """
        text = page.get('text')
        Overallsoup = BeautifulSoup(text, 'html.parser')
        script_list = Overallsoup.find_all('script')
        del script_list[0: 5]
        ma = re.compile(r'\{(.+?)\}')
        for script in script_list:
            result = ma.search(script.get_text()).group()
            try:
                data = json.loads(result, strict=False)
                if data.get('ns') == 'pl.content.textnewlist.index':
                    firstsoup = BeautifulSoup(data.get('html'), 'lxml')
                    url_selectors = firstsoup.select('.item_link.S_txt1')
                    for url_selector in url_selectors:
                        url = 'https:' + url_selector['href']
                        if len(re.findall(r'[_]', str(url))) == 3:
                            self.highlevel_db.addUrl(url)
                            # print(url)

                    break
            except Exception as e:
                print(str(e))


if __name__ == '__main__':
    weibo = weiboPageParser()
    URL = 'https://d.weibo.com/1087030002_2975_1001_0#'
    downloader = weiboDownloader()
    page = downloader.download(URL)
    # data = page.get('text')
    # print(data)
    # print()


    weibo.processListPage(page)
    # weibo.processDetailPage(page)
    # weibo.get_info_data()
    # weibo.init_url_repo(page)