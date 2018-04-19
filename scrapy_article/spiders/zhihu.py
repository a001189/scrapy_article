# -*- coding: utf-8 -*-
import re
import datetime
import json
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
    # question的第一页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccollapsed_counts%2Creviewing_comments_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.author.is_blocking%2Cis_blocked%2Cis_followed%2Cvoteup_count%2Cmessage_thread_token%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"

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
                if question_id not in question_id_pool:
                    print(question_url)
                    # with open('question_url.txt', 'w+') as f:
                    #     f.write(question_id + ':' + question_url + '\n')
                    question_id_pool.append(question_id)
                    yield scrapy.Request(question_url, headers=self.headers, meta={'question_id': question_id},
                                         callback=self.question_detail)
                    # yield scrapy.Request(question_url, headers=self.headers, callback=self.parse)
                else:
                    # print('%s already exists' % question_id)
                    pass
            else:
                yield scrapy.Request(url=url, headers=self.headers, dont_filter=True)

    def question_detail(self, response):
        """
        scrapy shell -s USER_AGENT="Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0" https://www.zhihu.com/question/22044254


        """
        loader = ItemLoader(item=QuestionItem(), response=response)
        loader.add_value('zhihu_id', response.meta.get('question_id'))
        loader.add_css('title', '.QuestionHeader-title::text')
        loader.add_css('content', '.QuestionHeader-detail span::text')
        loader.add_value("url", response.url)
        loader.add_css("answer_num", ".List-headerText span::text")
        loader.add_css("comments_num", ".QuestionHeader-Comment button::text")
        loader.add_css('watch_user_num', '.NumberBoard-itemValue::text')
        loader.add_css('click_num', '.NumberBoard-itemValue::text')
        loader.add_css('topics', '.QuestionTopic div::text')
        loader.add_value('crawl_time', datetime.datetime.now())
        question_item = loader.load_item()
        yield scrapy.Request(url=self.start_answer_url.format(response.meta.get('question_id'), 20, 0),
                             headers=self.headers, callback=self.answer_detail)
        yield question_item
        pass

    def answer_detail(self, response):
        pass
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        next_url = ans_json["paging"]["next"]

        # 提取answer的具体字段
        for answer in ans_json["data"]:
            answer_item = AnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["praise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()
            print(answer_item.fields.keys()-answer_item.keys())
            yield answer_item
        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.answer_detail)


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