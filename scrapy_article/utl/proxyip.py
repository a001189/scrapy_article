#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# @Time    : 2018/4/27 16:58
# @Author  : ysj
import socket
import MySQLdb
from scrapy.selector import Selector
from fake_useragent import UserAgent
import requests
from concurrent.futures import ThreadPoolExecutor

us = UserAgent()

class MyException(Exception):
    pass


def connect_check(ip, port='1080'):
    """检查端口是否可用"""
    # 导入python socket模块方法
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.settimeout(0.3)
    try:
        sk.connect((ip, int(port)))
    except Exception:
        return False
    else:
        return True
    finally:
        sk.close()


def web_connect_check(ip, port, type_):
    """检查代理可用性"""
    http_type = type_.lower()
    if http_type not in ('https', 'http'):
        http_type = 'http'

    proxy = {
        http_type: '{}://{}:{}'.format(http_type, ip, port)
    }
    try:
        response = requests.get('{}://www.lqhy.xyz/ip'.format(http_type), proxies=proxy, timeout=3).text
    except Exception:
        pass
    else:
        if response == ip:
            return True


def singletion(sqlclass):
    _instance = {}

    def wrapper(*args, **kwargs):
        if not _instance.get('con'):
            _instance['con'] = sqlclass(*args, **kwargs)
        return _instance['con']
    return wrapper


@singletion
class MysqlCoonection:

    MYSQL_INFO = dict(
        host='rm-uf69d6mp154aocu5tbo.mysql.rds.aliyuncs.com',
        user='root',
        password='123QWEqwe',
        db='article_spider',
        charset='utf8',
        use_unicode=True,
    )

    def __init__(self):
        self.con = MySQLdb.connect(**self.MYSQL_INFO)

    def do_sql(self,sql):
        con = self.con
        cursor = con.cursor()
        cursor.execute(sql)
        con.commit()


def get_ip(url):

    header = {
        'Host': 'www.xicidaili.com',
        'Referer': 'http://www.xicidaili.com/api',
        'Upgrade-Insecure-Requests': '1',
    }
    header.update({'User-Agent': us.random})
    response = requests.get(url, headers=header)
    selector = Selector(response)
    ip_list = selector.css('#ip_list tr')[1:]
    if ip_list:
        print(url)
    for line in ip_list:
        ip_info = line.css('*::text').extract()
        ip_info = [x.strip() for x in ip_info if x.strip()]
        # 7
        # ['60.177.227.229', '18118', '浙江杭州', '高匿', 'HTTP', '12天', '18-04-27 20:50']
        if connect_check(*ip_info[:2]):
            if web_connect_check(*ip_info[:2], ip_info[4]):
                yield ip_info





def main():
    count = 0
    # 1 -- 2955

    def pipeline(url):
        nonlocal count
        sql_con = MysqlCoonection()
        ip_gen = get_ip(url)
        for ip_info in ip_gen:
            insert_sql = """
                            insert into ip SELECT null, {},0
                """.format(str(ip_info[:5]).strip('[]'))
            try:
                sql_con.do_sql(insert_sql)
            except Exception as e:
                print(e)
            else:
                count += 1
                print(count)

    base_url = 'http://www.xicidaili.com/nn/{}'
    urls = (base_url.format(x) for x in range(1, 2956))
    with ThreadPoolExecutor(max_workers=20) as pool:
        pool.map(pipeline, urls)


if __name__ == '__main__':
    main()

