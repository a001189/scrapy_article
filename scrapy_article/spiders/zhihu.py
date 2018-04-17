# -*- coding: utf-8 -*-
import scrapy
import time
from hashlib import sha1
import hmac




class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
        'HOST': 'www.zhihu.com',
        'Referer': 'https://www.zhihu.com/signin?next=%2F',
        'Authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20'
    }
    login_url = 'https://www.zhihu.com/api/v3/oauth/sign_in'
    captcha_url = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=en'
    check_url = 'https://www.zhihu.com/inbox'
    # check_url = 'https://www.zhihu.com/'
    post_data = {
        'client_id': 'c3cef7c66a1843f8b3a9e6a1e3160e20',
        'grant_type': 'password',
        'timestamp': str(int(time.time())),
        'source': 'com.zhihu.web',
        'signature': None,
        'username': '18516157608',
        'password': '123qaz',
        'captcha': None,
        'lang': 'en',
        'ref_source': 'homepage',
        'utm_source': ''
    }

    def parse(self, response):
        pass

    def start_requests(self):
        self.post_data['signature'] = self.get_signature()

        return [scrapy.Request(url=self.check_url, headers=self.headers, method='GET', dont_filter=True,
                               callback=self.check_login)]

    def check_login(self, response):
        """实测，用requests登录过，会保存cookie，scrapy也可使用，暂时不考虑scrapy登录"""
        if response.status < 300:
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers)

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