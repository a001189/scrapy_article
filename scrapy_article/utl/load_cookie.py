#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# @Time    : 2018/4/18 18:10
# @Author  : ysj
import os
import http.cookiejar as cookielib
import requests
from scrapy_article.utl.ZhiHuLogIn import ZhiHu


cookie_file = os.path.join(os.path.dirname(__file__), 'zhihu_cookie.txt')


def load_cookie(filename=cookie_file):
    """加载cookie文件"""

    cookie = cookielib.LWPCookieJar()
    cookie.load(filename, ignore_discard=True, ignore_expires=True)
    return requests.utils.dict_from_cookiejar(cookie)


def get_dict_cookie(account='18516157608', password='******'):
    login = ZhiHu(account, password)
    return requests.utils.dict_from_cookiejar(login.session.cookies)


if __name__ == '__main__':
    print(load_cookie())
    print(get_dict_cookie('18516157608', '*****'))