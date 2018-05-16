# -*- coding: utf-8 -*- 
#!/usr/bin/env python
import mysql.connector
import argparse
import logging
import json
import os
import re

"""
提取数据库中的视频信息，生成Markdown文件
"""

# 解析命令行参数
parser = argparse.ArgumentParser(description = "crawl pornhub ...")
parser.add_argument("-c", "--config", help="crawler config file", required = True)
parser.add_argument("-t", "--taskname", help="task name", required = True)
parser.add_argument("-l", "--level", help="logging level", required = False)
parser.add_argument("-d", "--dir", help="directory the movies store", required = False)

args = parser.parse_args()

# 设置日志级别
if (args.level == "debug"):
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

# 读取配置文件
C = ""
with open(args.config, "r") as read_file:
    C = json.load(read_file)

logging.info("scan movies and update status...")

db = mysql.connector.connect(user=C["db"]["user"], password=C["db"]["password"], 
    host=C["db"]["host"], database=C["db"]["database"], use_unicode=True)
cursor = db.cursor()

# 遍历目录，查看已经下载的视频文件
for (dirpath, dirnames, filenames) in os.walk(args.dir):
    for file in filenames:
        matchobj = re.match('.*_(\d+).mp4', file)
        if matchobj == None:
            logging.error("invalid movie name: %s!", file)
            break
        cursor.execute("update pornhub.movie set download = 1 where mid = %d" % int(matchobj.group(1)))
        db.commit()


logging.info("done!")
# cursor.close()
db.close()