# -*- coding: utf-8 -*- 
#!/usr/bin/env python
import urllib.request as request
import mysql.connector
import argparse
import requests
import logging
import time
import json
import bs4

# import user define function
from crawler_helper import import_movies
from crawler_helper import parse_movie_list_html
from crawler_helper import fix_url

# 解析命令行参数
parser = argparse.ArgumentParser(description = "crawl pornhub movie list ...")
parser.add_argument("-c", "--config", help="crawler config file", required = True)
parser.add_argument("-t", "--taskname", help="task name", required = True)
parser.add_argument("-l", "--level", help="logging level", required = False)
parser.add_argument("-p", "--proxy", help="use proxy", action="store_true")

args = parser.parse_args()

# 设置日志级别
if (args.level == "debug"):
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

# 读取配置文件
logging.info("load crawler's configuration...")

C = ""
with open(args.config, "r") as read_file:
    C = json.load(read_file)

# shadowsocks代理配置
proxies = {}
if args.proxy:
    proxies = C["proxy"]
    print(proxies)

# 连接数据库
logging.info("connect database <%s> ...", C["db"]["host"])

db = mysql.connector.connect(user=C["db"]["user"], password=C["db"]["password"], 
    host=C["db"]["host"], database=C["db"]["database"], use_unicode=True)

# 执行任务
from_page = C["task"][args.taskname]["from"]
to_page = C["task"][args.taskname]["to"]
url_template = C["task"][args.taskname]["template"]

for page in range(from_page, to_page):
    url = url_template.replace("XXXXX", str(page))
    logging.info("download page `%s` ...", url)
    res = requests.get(url, proxies=proxies)
    if res.status_code == 200:
        movies = parse_movie_list_html(res.text)
        fix_url(movies, C["task"][args.taskname]["output_url_prefix"])
        import_movies(db, movies)
    time.sleep(30)

# 断开数据库连接
logging.info("disconnect database!")
db.close()