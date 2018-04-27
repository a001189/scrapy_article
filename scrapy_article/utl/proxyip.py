#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# @Time    : 2018/4/27 16:58
# @Author  : ysj
import socket
from scrapy.selector import Selector
from fake_useragent import UserAgent
import requests

us = UserAgent()


def get_ip(url):

    header = {
        'Host': 'www.xicidaili.com',
        'Referer': 'http://www.xicidaili.com/api',
        'Upgrade-Insecure-Requests': '1',
    }
    header.update({'User-Agent': us.random})
    response = requests.get(url, headers=header)
    selector = Selector(response)


def connect_check(ip, port='1080'):
    """检查端口是否可用"""
    # 导入python socket模块方法
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.settimeout(0.2)
    try:
        sk.connect((ip, port))
    except Exception:
        return False
    else:
        return True
    finally:
        sk.close()
def web_connect_check(ip, port, type_):
    """检查代理可用性"""
    if type_ not in ('https', 'http'):
        type_ = 'http'
    proxy = {
        type_: '{}://{}:port'
    }
