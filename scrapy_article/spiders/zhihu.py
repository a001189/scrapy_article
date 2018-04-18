# -*- coding: utf-8 -*-
import re
from urllib import parse
import scrapy
import time
from hashlib import sha1
import hmac
from scrapy_article.utl.load_cookie import load_cookie, get_dict_cookie
from scrapy.loader import ItemLoader
from scrapy_article.items import QuestionItem, AnswerItem
from functools import partial


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
        """
        提取页面所有的url， 并跟踪url进一步爬取
        如果url格式为 、question/xxxxxx 就下载，进入解析函数
        """
        all_urls = response.css('a::attr(href)').extract()
        all_urls = (parse.urljoin(response.url, url) for url in all_urls if 'javascript' not in url)
        for url in all_urls:
            'https://www.zhihu.com/question/invited'
            match_str = re.findall(r'(.*(?:question)/(\d+))(?:/|$)', url)
            if match_str:
                question_url, question_id = match_str[0]
                yield scrapy.Request(question_url, headers=self.headers, callback=self.parse_detail)
                print(match_str)
            pass

    def parse_detail(self, response):
        pass

    def start_requests(self):
        self.post_data['signature'] = self.get_signature()

        return [scrapy.Request(url=self.check_url, headers=self.headers, method='GET', meta={'dont_redirect': True},
                               cookies=load_cookie(), callback=self.check_login)]

    def check_login(self, response):
        """用requests登录过，会保存cookie，传入scrapy使用，暂时不考虑scrapy登录"""
        if response.status < 300:
            print('登录成功')
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers)
        else:
            print('未登录,即将拉取验证码，重新登录')
            yield [scrapy.Request(url=self.check_url, headers=self.headers, method='GET', meta={'dont_redirect': True},
                                  cookies=get_dict_cookie(), callback=self.check_login)]

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