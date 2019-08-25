#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:俊坚
# datetime:2019/7/31 22:20
# software: PyCharm
import  traceback
from  lxml import etree
import re
import json
import emoji
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
        if text:
            try:
                detail_url_html = re.search(r'\{(.*?)"domid":"Pl_Core_F4RightUserList__4"(.*?)\}', text)
                if detail_url_html:
                    # print(detail_url_html.group())
                    data = json.loads(detail_url_html.group(), strict=False)
                    html = etree.HTML(str(data.get('html')))
                    #判断返回的页面内容是否为空
                    error_selector = html.xpath('//div[@class="WB_empty"]')
                    if len(error_selector) == 0:  #内容不为空
                        urllist_selectors =html.xpath('//dt[@class="mod_pic"]/a/@href')
                        # 获取详细页url
                        for urllist_selector in urllist_selectors:
                            detail_url = 'https:' + urllist_selector
                            # print(detail_url)
                            self.lowlevel_db.addUrl(detail_url)
                        nexturl_selector = html.xpath('//a[@class="page next S_txt1 S_line1"]/@href')
                        # print(nexturl_selector)
                        if  nexturl_selector :
                            next_url = 'https://d.weibo.com' + nexturl_selector[0]
                            # print(next_url)
                            self.highlevel_db.addUrl(next_url)
                        else:
                            print('已经是最后一页')
                    else:#内容为空
                        print(data.get('html'))
                        self.highlevel_db.addUrl(page.get('url'))
            except Exception as e:
                traceback.print_exc()
        else :
            print(text)

    def processDetailPage(self, page):
        """
        解析文章页，获取博主信息存储于MySQL
        :param page:ff
        :return:
        """
        text = page.get('text')
        pageurl = page.get('url')
        if text and pageurl:
            try:
                self.info_data['url'] = pageurl
                domain = re.findall(r'.com\/(.+?)\?', str(pageurl))
                blogger_type = re.findall(r'refer_flag=(.*)', str(pageurl))
                id = re.findall(r'\[\'oid\'\]=\'(.*?)\'', str(text))
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
                    html = etree.HTML(str(data.get('html')))
                    # 昵称
                    self.info_data['username'] = html.xpath('//h1[@class="username"]')[0].text
                    # 认证
                    auth = html.xpath('//div[1]/div/div[2]/div[1]/a/em/@class')
                    if auth:
                        if auth[0][15:] == 'approve_gold':
                            self.info_data['authentication'] = '金V个人认证 '
                        elif auth[0][15:] == 'approve':
                            self.info_data['authentication'] = '个人认证'
                        else:
                            self.info_data['authentication'] = '官方认证'
                    # 等级
                    level = html.xpath('//div[1]/div/div[2]/div[2]/a/em/@class')
                    if level and level[0] != 'W_icon icon_member_dis':
                        self.info_data['vip_level'] = level[0][-1:]
                    # 性别
                    gender = html.xpath('//div[1]/div/div[2]/div[2]/span/a/i/@class')
                    if gender:
                        if gender[0][15:] == 'female':
                            self.info_data['gender'] = '0'
                        else:
                            self.info_data['gender'] = '1'
                    # 简介
                    introduction = html.xpath('//div[@class="pf_intro"]')
                    if introduction:
                        self.info_data['introduction'] = emoji.demojize(introduction[0].text.strip())

                second_part = re.search(r'\{(.*?)"domid":"Pl_Core_T8CustomTriColumn__3"(.*?)\}', text)
                if second_part:
                    data = json.loads(second_part.group(), strict=False)
                    html = etree.HTML(str(data.get('html')))
                    selectors = html.xpath('//a[@class="t_link S_txt1"]/strong')
                    # print(selectors)
                    if selectors:
                        # 关注数
                        self.info_data['followers_num'] = selectors[0].text
                        # 粉丝数
                        self.info_data['fans_num'] = selectors[1].text
                        # 微博数
                        self.info_data['weets_num'] = selectors[2].text

                third_part = re.search(r'\{(.*?)"domid":"Pl_Core_UserInfo__6"(.*?)\}', text)
                if third_part:
                    data = json.loads(third_part.group(), strict=False)
                    html = etree.HTML(str(data.get('html')))
                    select_list = html.xpath('//span[@class="item_text W_fl"]')
                    for select in select_list:
                        if select.text:
                            if re.search(r'^((?!毕业于|简介：|个性域名：|博客地址：|友情链接).)*$', select.text.strip()) and len(select.text.strip()) >0:
                                if re.search(r'.*月.*', select.text.strip()):
                                    self.info_data['birthday'] = select.text.strip()
                                else:
                                    # 所在城市
                                    self.info_data['city'] = select.text.strip()
            except Exception as e:
                print(str(e))
                traceback.print_exc()
            self.mysqlclent.insert('weibo_blogger', self.info_data)
        else:
            # print('text',text)
            print('url',pageurl)
            self.lowlevel_db.addUrl(pageurl)
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
                html = etree.HTML(str(data.get('html')))
                url_selectors = html.xpath('//ul[@class="ul_item clearfix"]/li/a/@href')
                for url_selector in url_selectors:
                    url = 'https:' + url_selector
                    if len(re.findall(r'[_]', str(url))) == 3:
                        # print(url)
                        self.highlevel_db.addUrl(url)
        except Exception as e:
            print(str(e))
            traceback.print_exc()


if __name__ == '__main__':
    weibo = weiboPageParser()
    URL = 'https://d.weibo.com/1087030002_2975_1001_0#'
    downloader = weiboDownloader()
    page = downloader.download(URL)


    weibo.processListPage(page)
    # weibo.processDetailPage(page)
    # weibo.get_info_data()
    # weibo.init_url_repo(page)
    # ValueError: can only parse strings