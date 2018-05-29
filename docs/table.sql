-- 电影列表
-- status:
--    -2: 该视频依法删除
--    -1: 该视频禁止下载
--     0: 视频还未处理
--     1: 已下载视频基本信息
create table movie(
    mid bigint primary key, 
    name varchar(128) not null, 
    url varchar(256) not null, 
    views bigint not null, 
    status int not null);

-- 影星列表
create table star(
    sid bigint primary key,
    name varchar(128) not null,
    url varchar(256)
);

-- 出演电影的明星
create table casts(
    mid bigint not null,
    sid bigint not null,
    primary key(mid, sid),
    foreign key(sid) references star(sid),
    foreign key(mid) references movie(mid)
);

-- 电影分类
create table category(
    mid bigint not null,
    name varchar(32),
    primary key(mid, name),
    foreign key(mid) references movie(mid)
);

-- tag
create table tag(
    mid bigint not null,
    name varchar(32),
    primary key(mid, name),
    foreign key(mid) references movie(mid)
);