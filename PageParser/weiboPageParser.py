#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:俊坚
# datetime:2019/7/31 22:20
# software: PyCharm
import  traceback
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

    def processListPage(self, page):
        """
        解析列表页获取文章页url 和下一页列表页url
        :param page:
        :return:
        """
        text = page.get('text')
        pageurl = page.get('url')
        try:
            detail_url_html = re.search(r'\{(.*?)"domid":"Pl_Core_F4RightUserList__4"(.*?)\}', text)
            if detail_url_html:
                data = json.loads(detail_url_html.group(), strict=False)
                url_soup = BeautifulSoup(data.get('html'), 'lxml')
                urllist_selectors = url_soup.select('dt.mod_pic')
                # 获取详细页url
                for urllist_selector in urllist_selectors:
                    detail_url = 'https:' + urllist_selector.select('a')[0]['href']
                    # print(detail_url)
                    self.lowlevel_db.addUrl(detail_url)
                nexturl_list = re.findall(
                    r'<a bpfilter="page" class="page next S_txt1 S_line1" href="(.*?)"><span>下一页</span></a>',
                    str(url_soup))
                if nexturl_list:
                    next_url = 'https://d.weibo.com' + nexturl_list[0].replace('amp;', '')
                    # print(next_url)
                    self.highlevel_db.addUrl(next_url)
                else:
                    print('已经是最后一页')
        except Exception as e:
            # print(str(e))
            traceback.print_exc()

    def processDetailPage(self, page):
        """
        解析文章页，获取博主信息存储于MySQL
        :param page:ff
        :return:
        """
        text = page.get('text')
        pageurl = page.get('url')
        try:
            self.info_data['url'] = pageurl
            domain = re.findall(r'.com\/(.+?)\?', str(pageurl))
            blogger_type = re.findall(r'refer_flag=(.*)', str(pageurl))
            id = re.findall(r'\[\'oid\'\]=\'(.*?)\'', text)
            print(id)
            # 博主分类
            if blogger_type:
                self.info_data['blogger_type'] = blogger_type[0]
            # 个性域名
            if domain:
                self.info_data['domain_name'] = domain[0]
            # id
            if id:
                self.info_data['ID'] = id[0]
            first_part = re.search(r'\{(.*?)"domid":"Pl_Official_Headerv6__1"(.*?)\}', text)
            if first_part:
                data = json.loads(first_part.group(), strict=False)
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
                    else:
                        self.info_data['authentication'] = '官方认证'
                # 等级
                level = re.findall(r'<em class="W_icon icon_member(.*?)"', str(firstsoup.find_all('em')))
                if level and level[0] != '_dis':
                    self.info_data['vip_level'] = level[0]
                # 性别
                if firstsoup.i['class'][1].split('_')[2] == 'female':
                    self.info_data['gender'] = '0'
                else:
                    self.info_data['gender'] = '1'
                # 简介
                self.info_data['introduction'] = firstsoup.select("div.pf_intro")[0].get_text().strip()
            second_part = re.search(r'\{(.*?)"domid":"Pl_Core_T8CustomTriColumn__3"(.*?)\}', text)
            if second_part:
                data = json.loads(second_part.group(), strict=False)
                secondsoup = BeautifulSoup(data.get('html'), 'lxml')
                # 关注数
                self.info_data['followers_num'] = secondsoup.select('strong')[0].get_text()
                # 粉丝数
                self.info_data['fans_num'] = secondsoup.select('strong')[1].get_text()
                # 微博数
                self.info_data['weets_num'] = secondsoup.select('strong')[2].get_text()
            third_part = re.search(r'\{(.*?)"domid":"Pl_Core_UserInfo__6"(.*?)\}', text)
            if third_part:
                data = json.loads(third_part.group(), strict=False)
                thirdsoup = BeautifulSoup(data.get('html'), 'lxml')
                select_list = thirdsoup.select('.item_text.W_fl')
                for key, value in enumerate(select_list):
                    if re.search(r'^((?!毕业于|简介：|个性域名：).)*$', value.get_text().strip()):
                        if key == 0:
                            # 所在城市
                            self.info_data['city'] = value.get_text().strip()
                        else:
                            if re.search(r'.*年.*', value.get_text().strip()):
                                self.info_data['birthday'] = value.get_text().strip()
        except Exception as e:
            print(str(e))
            traceback.print_exc()
            # self.mysqlclent.insert('weibo_blogger', self.info_data)

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
        try:
            url_html = re.search(r'\{(.*?)"ns":"pl.content.textnewlist.index"(.*?)\}', text)
            if url_html:
                data = json.loads(url_html.group(), strict=False)
                url_soup = BeautifulSoup(data.get('html'), 'lxml')
                url_selectors = url_soup.select('.item_link.S_txt1')
                for url_selector in url_selectors:
                    url = 'https:' + url_selector['href']
                    if len(re.findall(r'[_]', str(url))) == 3:
                        # print(url)
                        self.highlevel_db.addUrl(url)
        except Exception as e:
            print(str(e))
            traceback.print_exc()


if __name__ == '__main__':
    weibo = weiboPageParser()
    URL = 'https://d.weibo.com/1087030002_2975_1003_0#'
    downloader = weiboDownloader()
    page = downloader.download(URL)
    # data = page.get('text')
    # print(data)
    # print()


    weibo.processListPage(page)
    # weibo.processDetailPage(page)
    # weibo.get_info_data()
    # weibo.init_url_repo(page)