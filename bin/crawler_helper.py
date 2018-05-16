# -*- coding: utf-8 -*- 
#!/usr/bin/env python
import logging
import json
import bs4
import re

# 解析页面
def parse_html(html):
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

# 存储解析结果
"""
数据存储在表pornhub.movie中，表定义如下：
    create table movie(mid bigint primary key, name varchar(128) not null, url varchar(256) not null, views bigint not null, status int not null);
    create index idx_movie_views on movie(views) ;
"""
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