# -*- coding: utf-8 -*- 
#!/usr/bin/env python
import requests
import logging
import json
import bs4
import re

# 解析电影列表页面
def parse_movie_list_html(html):
    soup = bs4.BeautifulSoup(html, "html.parser")
    ul = soup.find('ul', attrs={'class':'nf-videos videos search-video-thumbs'})
    # 将解析结果存放在哈希表
    info = {}
    # 所有的视频存放在`li`元素中
    movies_li = ul.find_all('li')
    for movie_li in movies_li:
        # 获取视频的`data-d`
        data_id = movie_li['data-id']
        # 获取视频的`title`和`url`
        movie_span = movie_li.find('span', attrs={'class':'title'})
        movie_title = movie_span.find('a').string
        movie_url = movie_span.find('a')['href']
        # 获取视频的评分人数
        rating_span = movie_li.find('span', attrs={'class':'views'})
        views_str = rating_span.find('var').string
        views = trans_views(views_str)
        # 存储结果到哈希表
        info[str(movie_title)] = {'url':str(movie_url), 'data-id':int(data_id), 'views':views}
        # logging.debug('save movie %s!', movie_title)
    return info

# 视频的观看次数以`views`格式为`5.6M`或`3.9K`等，我们将其转换为数字
def trans_views(views_str):
    matchobj = re.match('(\d+(\.)?\d*)([M|K])', views_str)
    count = float(matchobj.group(1))
    unit = matchobj.group(3)
    if unit == 'M':
        return count*1000000
    else:
        return count*1000

# 修改url，添加前缀和分类标签
def fix_url(info, url_prefix):
    for k, v in info.items():
        v['url'] = url_prefix + v['url']
    return

# 存储pornhub电影列表，movie列表存储在pornhub.movie中，表定义如下:
#     create table movie(mid bigint primary key, name varchar(128) not null, 
#       url varchar(256) not null, views bigint not null, status int not null);
# 
# 状态信息status:
#     0 - 未处理任务
#     1 - 已经获取了电影的详细信息
def import_movies(db, info):
    # SQL语句
    # Notes:
    #   the parameter markers used by mysql.connector may look the same as the %s used 
    #   in Python string formatting but the relationship is only coincidental
    #   if you use %d it will throw: `Not all parameters were used in the SQL statement`
    sql = ("insert ignore into pornhub.movie values (%s, %s, %s, %s, %s)")
    cursor = db.cursor()

    for k, v in info.items():  
        cursor.execute(sql, [v['data-id'], k, v['url'], v['views'], 0])
    db.commit()
    cursor.close()
    return

# 获取电影的具体信息
def update_movie_info(db, mid, html):
    soup = bs4.BeautifulSoup(html, "html.parser")
    cursor = db.cursor()
    # 获取电影浏览量
    count_div = soup.find('div', attrs={'class':'rating-info-container'})
    # 如果不包含rating信息
    if count_div is None:
        sql = "update movie set status = -2 where mid = %s"
        cursor.execute(sql, [str(mid)])
        db.commit()
        cursor.close()
        return
    count = count_div.find('span', attrs={'class':'count'}).text.replace(',', '')
    # 更新浏览量
    sql = "update movie set views = %s, status = 1 where mid = %s"
    cursor.execute(sql, [str(count), str(mid)])
    # 获取演员
    detail_div = soup.find('div', attrs={'class':'video-detailed-info'})
    movie_star_list = detail_div.find('div', attrs={'class':'pornstarsWrapper'}).find_all('a', attrs={'data-mxptype':'Pornstar'})
    # 插入演员表和演员列表
    sql_star = "insert ignore into star values(%s, %s, %s)"
    sql_casts = "insert ignore into casts (mid, sid) values (%s, %s)"
    for s in movie_star_list:
        cursor.execute(sql_star, [s['data-id'], s['data-mxptext'], "https://www.pornhub.com" + s['href']])
        cursor.execute(sql_casts, [mid, s['data-id']])
    # 插入电影分类
    sql_category = "insert ignore into category values(%s, %s)"
    category_list = detail_div.find('div', attrs={'class':'categoriesWrapper'}).find_all('a', onclick=re.compile('^ga'))
    for c in category_list:
        cursor.execute(sql_category, [mid, c.text])
    # 插入电影的tag
    sql_tag = "insert ignore into tag values(%s, %s)"
    tag_list = detail_div.find('div', attrs={'class':'tagsWrapper'}).find_all('a', recursive=False)
    for t in tag_list:
        cursor.execute(sql_tag, [mid, t.text])
    # 提交所有修改
    db.commit()
    cursor.close()
    return


