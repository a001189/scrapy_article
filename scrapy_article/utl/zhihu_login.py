#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# @Time    : 2018/4/16 15:06
# @Author  : ysj
import time
import requests
import base64
import json
from hashlib import sha1
import hmac

try:
    import cookielib
except Exception as e:
    import http.cookiejar as cookielib
# 忽略报错
requests.packages.urllib3.disable_warnings()
# 使用session 登录
session = requests.Session()
session.cookies = cookielib.LWPCookieJar(filename='requests_coo.txt')

headers = {
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
           'HOST': 'www.zhihu.com',
           'Referer': 'https://www.zhihu.com/signin?next=%2F',
           'Authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20'
           }

post_data = {
        'client_id': 'c3cef7c66a1843f8b3a9e6a1e3160e20',
        'grant_type': 'password',
        'timestamp': int(time.time()),
        'source': 'com.zhihu.web',
        'signature': None,
        'username': None,
        'password': None,
        'captcha': None,
        'lang': 'en',
        'ref_source': 'homepage',
        'utm_source': ''
    }

try:
    session.cookies.load(ignore_discard=True,ignore_expires=True)
    print('cookie信息加载成功')
except Exception as e:
    print("cookie信息加载失败")


def ensure_bytes(value):
    """字节确保，方便后续加密签名"""
    return value if isinstance(value, bytes) else value.encode('utf-8')


def check_login(session):
    """传入session对象， 使用地址判断是否登录"""
    res = session.get('https://www.zhihu.com/settings/profile', headers=headers, verify=False)
    code = res.status_code
    if code < 300:
        print('已登录成功')
        return True
    else:
        print('未登录或登录失败')
        return False


def get_signature(**kwargs):
    """登录签名，先加载默认字符串"""
    hm = hmac.new(b'd1b964811afb40118a12068ff74a12f4', None, sha1)
    try:
        hm.update(ensure_bytes(kwargs['client_id']))
        hm.update(ensure_bytes(kwargs['grant_type']))
        hm.update(ensure_bytes(kwargs['timestamp']))
        hm.update(ensure_bytes(kwargs['source']))
    except KeyError as ex:
        print('缺少参数', ex)
    return hm.hexdigest()


def sign_in():
    """实际登录api"""
    post_url = 'https://www.zhihu.com/api/v3/oauth/sign_in'
    session.post(post_url, data=post_data, headers=headers, verify=False)
    if check_login(session):
        session.cookies.save(ignore_expires=True, ignore_discard=True)


def log_in(username, password)
    # 先请求验证码地址，看是否需要验证码

    post_data['signature'] = get_signature(**post_data)
    post_data['username'] = username
    post_data['password'] = password
    response = session.get('https://www.zhihu.com/api/v3/oauth/captcha?lang=en', headers=headers, verify=False)
    show_captcha = response.json()['show_captcha']
    if not show_captcha:
        sign_in()
    else:
        # 有验证吗，重新请求获取验证码
        response = session.put('https://www.zhihu.com/api/v3/oauth/captcha?lang=en', headers=headers, verify=False)
        img = json.loads(response.content)['img_base64']
        img = img.encode('utf-8')
        img_data = base64.b64decode(img)
