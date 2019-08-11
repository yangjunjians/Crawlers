# Crawlers 项目目录
|————CookiesPool
| |————generator.py
| |————tester.py
|————DownLoad
| |————DownLoader.py
|————PageParser
| |————weiboPageParser.py
|————Repository
| |————UrlRepository.py
|————Scheduler
| |————weiboScheduler.py
|————config
| |————configdata.py
|————database
| |————dblink.py
|————login
| |————weiboCookies.py

CookiesPool:cookies池，通过cookies模拟登陆
1，generator.py：cookies生成器,为账号生成新的cookies。
2，tester.py：cookies测试器，测试cookies是否有效,无效删除。

DownLoad：页面内容下载，
1，DownLoader.py：继承编写各自的页面下载器

PageParser：页面内容解析
1，weiboPageParser.py：微博博主页面，找人页面列表页解析。

Repository：url数仓
1，UrlRepository.py：使用redis的list实现的FIFO对列，用于存储url。

Scheduler：调度器
1，weiboScheduler.py：微博页面爬取的调度器

config
1，configdata.py：项目的配置信息

database
1，dblink.py：数据库连接操作实现

login：网站登录实现
1，weiboCookies.py：微博登录实现




