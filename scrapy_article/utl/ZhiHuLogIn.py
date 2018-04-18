#! /usr/local/bin python3.6
"""
@Time    : 2018/4/17 20:00
@Author  : ysj
@Site    : 
@File    : ZhiHuLogIn.py
@Software: PyCharm
"""
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
import http.cookiejar as cookielib

# 忽略 InsecureRequestWarning报错; verify=True 即可
# requests.packages.urllib3.disable_warnings()


class ZhiHu:
    """
    知乎登录类，实例化后，self.session即相当于登录客户端requests.session
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
               'HOST': 'www.zhihu.com', 'Referer': 'https://www.zhihu.com/signin?next=%2F',
               'Authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20'}

    login_url = 'https://www.zhihu.com/api/v3/oauth/sign_in'
    captcha_url = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=en'
    check_url = 'https://www.zhihu.com/inbox'
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
    """
    测试数据，固定签名，无需签名
    post_data = {
        'client_id': 'c3cef7c66a1843f8b3a9e6a1e3160e20',
        'grant_type': 'password',
        'timestamp': '1515398025518',
        'source': 'com.zhihu.web',
        'signature': '30b129980d00e5efb09f16b0334bf4e8601b060b',
        'username': 1,
        'password': 2,
        'captcha': 3,
        'lang': 'en',
        'ref_source': 'homepage',
        'utm_source': ''
    }
    """

    def __init__(self, account, password, cookie_file='zhihu_cookie.txt'):
        self.session = requests.session()
        self.session.headers = self.headers
        self.cookie_file = cookie_file
        self.session.cookies = cookielib.LWPCookieJar(filename=self.cookie_file)
        self.username = account
        self.password = password
        self.check_count = 0
        try:
            self.session.cookies.load(ignore_discard=True, ignore_expires=True)
            print('cookie信息加载成功')
        except FileNotFoundError:
            print("cookie信息加载失败")
            self.login()
        else:
            if not self.check_login():
                print('cookie登录失败，即将重新登录')
                self.login()
        # self.check_login()

    def login(self):
        """整个登录过程"""
        self.check_count = 0
        self.post_data['username'] = self.username
        self.post_data['password'] = self.password
        self.post_data['captcha'] = self.check_captcha()
        self.post_data['signature'] = self.get_signature()
        self.sign_in()

    def check_login(self):
        """传入session对象， 使用地址判断是否登录"""
        # 不允许跳转，不然总是为200
        res = self.session.get(self.check_url, verify=True, allow_redirects=False)
        code = res.status_code
        if code < 300:
            print('已登录成功')
            return True
        else:
            print('未登录或登录失败')
            return False

    def sign_in(self):
        """实际登录api"""
        response = self.session.post(self.login_url, data=self.post_data, verify=True)
        if self.check_login():
            self.session.cookies.save(ignore_expires=True, ignore_discard=True)
            return True
        else:
            print(response.json())

    def check_captcha(self):
        response = self.session.get(self.captcha_url, verify=True)
        show_captcha = response.json()['show_captcha']
        if not show_captcha:
            return None
        else:
            # 有验证吗，重新请求获取验证码
            response = self.session.put(self.captcha_url, verify=True)
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
            captcha = input('请输入当前目录下图片%s，的验证码:' % filename)
            # sub.terminate()
            # im.close()
            os.remove(filename)
            data = {'input_text': captcha}
            response = self.session.post(self.captcha_url, data=data, verify=True)
            try:
                result = response.json()
            except Exception as ex2:
                print('验证码的post请求响应失败，原因：{}'.format(ex2))
                """ 验证码失败，则再递归3次重新获取验证码"""
                self.check_count += 1
                if self.check_count < 4:
                    self.check_captcha()
            else:
                if result.get('success'):
                    return captcha
                else:
                    print(result)
                    """ 验证码失败，则再递归3次重新获取验证码"""
                    self.check_count += 1
                    if self.check_count < 4:
                        self.check_captcha()

    def get_signature(self):
        """知乎登录签名，先加载默认字符串
        实测比较死板，固定拿任意个对应的时间戳和signature 直接加载到请求参数即可跳过签名步骤
        """
        def ensure_bytes(value):
            """字节确保，方便后续加密签名"""
            return value if isinstance(value, bytes) else value.encode('utf-8')

        hm = hmac.new(b'd1b964811afb40118a12068ff74a12f4', None, sha1)
        try:
            kwargs = self.post_data
            hm.update(ensure_bytes(kwargs['grant_type']))
            hm.update(ensure_bytes(kwargs['client_id']))
            hm.update(ensure_bytes(kwargs['source']))
            hm.update(ensure_bytes(kwargs['timestamp']))
        except KeyError as ex:
            print('缺少参数', ex)
        else:
            return hm.hexdigest()


if __name__ == '__main__':
    login = ZhiHu('18516157608', '123qaz')
    print(login.session.get(login.check_url, allow_redirects=False).status_code)
    # 未登录的为302
    print(requests.get('https://www.zhihu.com/inbox', headers=ZhiHu.headers, allow_redirects=False).status_code)
