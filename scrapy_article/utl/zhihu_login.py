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
import os
import uuid
# from PIL import Image
# from multiprocessing import Process
try:
    import cookielib
except Exception as e:
    import http.cookiejar as cookielib
# 忽略 urllib3报错
requests.packages.urllib3.disable_warnings()

def check_login(session):
    """传入session对象， 使用地址判断是否登录"""
    # 不允许跳转，不然总是为200
    res = session.get('https://www.zhihu.com/settings/profile', verify=False, allow_redirects=False)
    code = res.status_code
    if code < 300:
        print('已登录成功')
        return True
    else:
        print('未登录或登录失败')
        return False


def ensure_bytes(value):
    """字节确保，方便后续加密签名"""
    return value if isinstance(value, bytes) else value.encode('utf-8')


def get_signature(**kwargs):
    """登录签名，先加载默认字符串"""
    hm = hmac.new(b'd1b964811afb40118a12068ff74a12f4', None, sha1)
    try:
        hm.update(ensure_bytes(kwargs['grant_type']))
        hm.update(ensure_bytes(kwargs['client_id']))
        hm.update(ensure_bytes(kwargs['source']))
        hm.update(ensure_bytes(kwargs['timestamp']))
    except KeyError as ex:
        print('缺少参数', ex)
    return hm.hexdigest()


def sign_in(session, post_data):
    """实际登录api"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
               'HOST': 'www.zhihu.com', 'Referer': 'https://www.zhihu.com/signin?next=%2F',
               'Authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20'}
    post_url = 'https://www.zhihu.com/api/v3/oauth/sign_in'
    # response = session.post(post_url, data=post_data, verify=False)
    response = session.post(post_url, data=post_data, headers=
    headers, verify=False)
    if check_login(session):
        session.cookies.save(ignore_expires=True, ignore_discard=True)
        return True


def log_in(username, password, session, post_data):
    # 先请求验证码地址，看是否需要验证码
    check_count = 0
    post_data['signature'] = get_signature(**post_data)
    post_data['username'] = username
    post_data['password'] = password

    def check_captcha():
        nonlocal check_count
        response = session.get('https://www.zhihu.com/api/v3/oauth/captcha?lang=en', verify=False)
        show_captcha = response.json()['show_captcha']
        if not show_captcha:
            return sign_in(session, post_data)
        else:
            # 有验证吗，重新请求获取验证码
            response = session.put('https://www.zhihu.com/api/v3/oauth/captcha?lang=en', verify=False)
            img = json.loads(response.content)['img_base64']
            img = img.encode('utf-8')
            img_data = base64.b64decode(img)
            filename = str(uuid.uuid4()) + 'tpm.gif'
            with open(filename, 'wb') as f:
                f.write(img_data)
            # 多进程显示图片异常，暂时舍弃该功能
            # im = Image.open(filename)
            # sub = Process(target=im.show)
            # sub.start()
            # im.show()
            captcha = input('请输入上述图片%s，的验证码:' % filename)
            # sub.terminate()
            # im.close()
            os.remove(filename)
            data = {'input_text': captcha}
            post_data['captcha'] = captcha
            response = session.post('https://www.zhihu.com/api/v3/oauth/captcha?lang=en', data=data, verify=False)
            try:
                result = response.json()
            except Exception as ex2:
                print('验证码的post请求响应失败，原因：{}'.format(ex2))
                """ 验证码失败，则再递归3次重新获取验证码"""
                check_count += 1
                if check_count < 4:
                    check_captcha()
            else:
                if result.get('success'):
                    return sign_in(session, post_data)
                else:
                    print(result)
                    """ 验证码失败，则再递归3次重新获取验证码"""
                    check_count += 1
                    if check_count < 4:
                        check_captcha()
    return check_captcha()


def main(username, password):
    """登录封装, 登录成功，返回session，失败则为None"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
        'HOST': 'www.zhihu.com',
        'Referer': 'https://www.zhihu.com/',
        'Authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20'
    }

    post_data = {
        'client_id': 'c3cef7c66a1843f8b3a9e6a1e3160e20',
        'grant_type': 'password',
        'timestamp': str(int(time.time())),
        'source': 'com.zhihu.web',
        'signature': None,
        'username': None,
        'password': None,
        'captcha': None,
        'lang': 'en',
        'ref_source': 'homepage',
        'utm_source': ''
    }

    # 使用session 登录
    session = requests.Session()
    session.headers = headers
    session.cookies = cookielib.LWPCookieJar(filename='zhihu_cookie.txt')
    try:
        session.cookies.load(ignore_discard=True, ignore_expires=True)
        print('cookie信息加载成功')
    except Exception as e:
        print("cookie信息加载失败")
        if log_in(username, password, session, post_data):
            return session
    else:
        # 加载cookie成功，则判断cookie是否有效
        if check_login(session):
            return session
        else:
            print('cookie 已失效，即将重新登录')
            if log_in(username, password, session, post_data):
                return session


if __name__ == '__main__':
    s = main('18516157608', '******')
    # 请求用户信息，正常即说明登录成功，和check_login 异曲同工
    print(s.get('https://www.zhihu.com/people/a-li-2-63-13/activities').text)
