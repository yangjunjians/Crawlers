#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:俊坚
# datetime:2019/8/2 20:49
# software: PyCharm
import time
from CookiesPool.tester import weiboValidTester
from CookiesPool.generator import weiboCookiesGenerator
from PageParser.weiboPageParser import weiboPageParser
from DownLoad.DownLoader import weiboDownloader
from  Repository.UrlRepository import UrlRepository
if __name__ == '__main__':
    start_url = 'https://d.weibo.com/1087030002_2975_1003_0#'
    Parser = weiboPageParser()
    downloader = weiboDownloader()
    urlRepo = UrlRepository('weibo')

    tester = weiboValidTester()
    tester.run()
    # #
    generatotr = weiboCookiesGenerator()
    generatotr.run()

    # initPage = downloader.download(start_url)
    # Parser.init_url_repo(initPage)
    #
    while(True):
        url = urlRepo.urlPop()
        if url:
            if url.startswith( 'https://d.weibo.com/'):
                print('列表页', url)
                url_list_page = downloader.download(url)
                Parser.processListPage(url_list_page)
                time.sleep(1)
            else:
                print('文章页', url)
                detail_page = downloader.download(url)
                Parser.processDetailPage(detail_page)
                time.sleep(2)
        else:
            print('队列中的url解析完毕')
        time.sleep(0.5)



