# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import datetime
import re
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Join, TakeFirst


def get_num(value):
    value_re = re.findall(r'.*?(\d+).*', value)
    return int(value_re[0]) if value_re else 0


def tag_filter(value):
    """去掉tag中包含 评论 的 value"""
    return value if '评论' not in value else None


def get_create_date(value):
    create_date_re = re.findall('.*?((?:\d+/*)+)', value)
    return  create_date_re[0] if create_date_re else datetime.datetime.now().date().strftime('%Y/%m/%d')


def convert_date(value):
    try:
        create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception:
        create_date = datetime.datetime.now().date()

    return create_date


def add_jobbole(value):
    return 'jobbole_' + value


class ScrapyArticleItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class JobboleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field()
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    fav_nums = scrapy.Field()
    tags = scrapy.Field()
    content = scrapy.Field()


class JobboleArticleItemTwo(scrapy.Item):
    title = scrapy.Field(
        # 测试
        # input_processor=MapCompose(add_jobbole, add_jobbole)
    )
    create_date = scrapy.Field(
        input_processor=MapCompose(get_create_date, convert_date)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        # imagepipeline 下载 item 必须为数组;设置out_processor覆盖TakeFirst
        output_processor=MapCompose(lambda x: x)
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_num)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_num)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_num)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(tag_filter),
        output_processor=Join(',')
    )
    content = scrapy.Field()


class JobboleItemLoader(ItemLoader):
    """ 默认提取第一个值"""
    default_output_processor = TakeFirst()


class QuestionItem(scrapy.Item):
    """知乎question item"""
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()


class AnswerItem(scrapy.Item):
    """知乎answer item"""
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()
