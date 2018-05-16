## Pornhub.com Crawler
### 1. 程序说明
- taskman.py: 任务管理器，用于生产爬虫的任务。我们首先从pornhub的`Categories`页面中按分类爬取视频列表并存入数据库的`movie`表，之后再由爬虫程序(crawler.py)按页面爬取视频的具体信息