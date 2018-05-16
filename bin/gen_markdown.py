# -*- coding: utf-8 -*- 
#!/usr/bin/env python
import mysql.connector
import argparse
import logging
import json

"""
提取数据库中的视频信息，生成Markdown文件
"""

# 解析命令行参数
parser = argparse.ArgumentParser(description = "crawl pornhub ...")
parser.add_argument("-c", "--config", help="crawler config file", required = True)
parser.add_argument("-t", "--taskname", help="task name", required = True)
parser.add_argument("-l", "--level", help="logging level", required = False)

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

logging.info("create markdown file for movie's tag: %s ...", C["task"][args.taskname]["tag"])

db = mysql.connector.connect(user=C["db"]["user"], password=C["db"]["password"], 
    host=C["db"]["host"], database=C["db"]["database"], use_unicode=True)

# 创建Markdown文件
md = open(C["task"][args.taskname]["tag"] + ".md", 'w')
title = "## Movies of `" + C["task"][args.taskname]["tag"] + "`\n"
md.write(title)
md.write("-----\n")

cursor = db.cursor()
cursor.execute("select * from pornhub.movie where tag = '%s' and download = 0" % C["task"][args.taskname]["tag"])
rs = cursor.fetchall()
for r in rs:
    s = "#### Movie ID: " + str(r[0]) + "\n"
    s += r[2] + "  \n[click!](" + r[3] + ")\n\n"
    md.write(s)

logging.info("done!")
md.close()
cursor.close()
db.close()