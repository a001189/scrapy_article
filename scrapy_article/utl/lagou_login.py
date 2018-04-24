#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# @Time    : 2018/4/23 9:51
# @Author  : ysj
import requests
import re
import hashlib


def get_md5(word):
    word_bytes = word.encode('utf-8') if isinstance(word, str) else word
    md5 = hashlib.md5()
    md5.update(word_bytes)
    return md5.hexdigest()


def get_lagou(password):
    return get_md5('veenike' + get_md5(password) + 'veenike')


def login(account, password):
    post_data = {
        'isValidate': 'true',
        'password': '',
        # 如需验证码,则添加上验证码
        'request_form_verifyCode': '',
        'submit': '',
        'username': '',
    }
    login_url = 'https://passport.lagou.com/login/login.html'
    post_url = 'https://passport.lagou.com/login/login.json'
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Pragma': 'no-cache',
        'Referer': 'https://www.lagou.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/64.0.3282.140 Safari/537.36',
        'Origin': 'https://passport.lagou.com'
    }
    post_data['username'] = account
    post_data['password'] = get_lagou(password)

    session = requests.session()
    session.headers = header
    # 获取动态请求头,并添加进去
    response = session.get(login_url)
    session.headers['X-Anit-Forge-Token'] = re.findall("window.X_Anti_Forge_Token.*'(.*?)'", response.text)[0]
    session.headers['X_Anti_Forge_Code'] = re.findall("window.X_Anti_Forge_Code.*'(.*?)'", response.text)[0]
    response_post = session.post(post_url, data=post_data)
    del session.headers['X-Anit-Forge-Token']
    del session.headers['X_Anti_Forge_Code']
    s = session.get('https://www.lagou.com/jobs/4096761.html', allow_redirects=False)
    # print(response_post.status_code,response_post.text)

    print(s.text)

if __name__ == '__main__':
    login('18516157608', '123qaz')

