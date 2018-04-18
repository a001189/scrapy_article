# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from scrapy import Request
from urllib.parse import urljoin
from scrapy_article.items import JobboleArticleItem, JobboleArticleItemTwo, JobboleItemLoader
from scrapy_article.utl.md5 import get_md5
from scrapy.loader import ItemLoader


class Jobbole2Spider(scrapy.Spider):
    name = 'jobbole2'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1 获取列表页所有文章url 交给scrapy下载后并进行解析
        2 获取下一页的url并交给scrapy进行下载， 下载完成后交给parse

        """
        # 解析列表页中的所有文章url并交给scrapy下载后并进行解析
        #all_article = response.css('#archive .floated-thumb .post-thumb a::attr(href)').extract()
        # for post_url in all_article:
        #     real_url = urljoin(response.url, post_url)
        #     yield Request(url=real_url, meta=None, callback=self.parse_detail)

        all_nodes = response.css('#archive .floated-thumb .post-thumb a')
        for node in all_nodes:
            image_url = node.css('img::attr(src)').extract_first('')
            image_real_url =urljoin(response.url, image_url)
            post_url = node.css('::attr(href)').extract_first('')
            real_url = urljoin(response.url, post_url)
            yield Request(url=real_url, meta={'front_image_url': image_real_url}, callback=self.parse_detail)


        # 提取下一页，交给parse函数
        next_page_url = response.css('.next.page-numbers::attr(href)').extract_first()
        if next_page_url:
            yield Request(url=urljoin(response.url, next_page_url), callback=self.parse)

    def _parse_detail(self, response):
        """文章具体字段提取  原始方法"""
        title = response.css('div.entry-header > h1::text').extract_first()
        create_date_str = response.css('.entry-meta-hide-on-mobile::text').extract_first()
        create_date_re = re.findall('.*?((?:\d+/*)+)', create_date_str)
        create_date = create_date_re[0] if create_date_re else datetime.datetime.now().date().strftime('%Y/%m/%d')
        create_date = datetime.datetime.strptime(create_date, '%Y/%m/%d')
        praise_nums = response.css(".vote-post-up h10::text").extract_first() or 0
        fav_nums_str = response.css(".bookmark-btn::text").extract()[0]
        fav_nums_re = re.findall(r'.*?(\d+).*', fav_nums_str)
        fav_nums = fav_nums_re[0] if fav_nums_re else 0
        comment_nums_str = response.css("a[href='#article-comment'] span::text").extract()[0]
        comment_nums_re = re.findall(r'.*?(\d+).*', comment_nums_str)
        comment_nums = comment_nums_re[0] if comment_nums_re else 0
        tag_list = response.css("p.entry-meta-hide-on-mobile a::text").extract()
        tags = ",".join(x for x in tag_list if '评论' not in x)
        content = response.css('.entry').extract_first()
        # front_image_url = response.meta.get('front_image_url', '')
        front_image_url = [response.meta.get('front_image_url', '')]
        url = response.url
        url_object_id = get_md5(url)

        items = JobboleArticleItem()
        for key in items.fields.keys():
            items[key] = locals().get(key, '')
        yield items

    def parse_detail(self, response):
        """文章具体字段提取  itemloader方法"""
        # itemloader 提取字段
        # loader = ItemLoader(item=JobboleArticleItemTwo(), response=response)
        # 使用提取第一个字段的loader选择器
        loader = JobboleItemLoader(item=JobboleArticleItemTwo(), response=response)
        loader.add_value('url_object_id', get_md5(response.url))
        loader.add_css('title', 'div.entry-header > h1::text')
        loader.add_css('create_date', '.entry-meta-hide-on-mobile::text')
        loader.add_value('url', response.url)
        loader.add_value('front_image_url', response.meta.get('front_image_url', ''))
        loader.add_css('praise_nums', '.vote-post-up h10::text')
        loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
        loader.add_css("fav_nums", ".bookmark-btn::text")
        loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        loader.add_css("content", "div.entry")

        items = loader.load_item()
        yield items



