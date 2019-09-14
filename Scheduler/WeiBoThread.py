#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:俊坚
# datetime:2019/8/28 21:52
# software: PyCharm

from threading import Thread
import time
from CookiesPool.tester import weiboValidTester
from CookiesPool.generator import weiboCookiesGenerator
from PageParser.weiboPageParser import weiboPageParser
from DownLoad.DownLoader import weiboDownloader
from  Repository.UrlRepository import UrlRepository


class WeiBoThread(Thread):
    def __init__(self,jobname):
        Thread.__init__(self)
        self.jobname = jobname
        self.Parser = weiboPageParser()
        self.downloader = weiboDownloader()
        self.urlRepo = UrlRepository('weibo')
        self.tester = weiboValidTester()
        self.generatotr = weiboCookiesGenerator()

    def testCookies(self):
        self.tester.run()
        self.generatotr.run()

    def initurllist(self):
        initPage = self.downloader.download(start_url)
        self.Parser.init_url_repo(initPage)

    def run(self):
        print('{}开始爬取'.format(self.jobname))
        while (True):
            url = self.urlRepo.urlPop()
            if url:
                if url.startswith('https://d.weibo.com/'):
                    print('列表页', url)
                    url_list_page = self.downloader.download(url)
                    self.Parser.processListPage(url_list_page)
                else:
                    print('文章页', url)
                    detail_page = self.downloader.download(url)
                    self.Parser.processDetailPage(detail_page)
            else:
                print('队列中的url解析完毕')
            time.sleep(2)

if __name__ == '__main__':
    jobname = '初始化线程'
    init_thread = WeiBoThread(jobname=jobname)
    init_thread.testCookies()

    threads = []
    for i in range(2):
        jobname = '爬虫线程{}'.format(i)
        t = WeiBoThread(jobname=jobname)
        threads.append(t)
        t.start()



    [thread.join() for thread in threads]