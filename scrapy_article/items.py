# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import time
import datetime
import re
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Join, TakeFirst
from settings import SQL_DATE, SQL_DATE_TIME
from functools import partial
from utl.tools import get_index
from w3lib.html import remove_tags


TakeLast = partial(get_index, index=-1, default=0)



def rm_comma(value):
    if isinstance(value, (int, float)):
        return int(value)
    elif isinstance(value, str):
        try:
            return int(value.replace(',', ''))
        except ValueError:
            return 0
    else:
        return 0


def get_num(value):
    value_re = re.findall(r'.*?(\d+).*', value)
    return int(value_re[0]) if value_re else 0


def tag_filter(value):
    """去掉tag中包含 评论 的 value"""
    return value if '评论' not in value else None


def get_create_date(value):
    create_date_re = re.findall('.*?((?:\d+/*)+)', value)
    return  create_date_re[0] if create_date_re else datetime.datetime.now().date().strftime('%Y/%m/%d')


def convert_date(value, sql_type="%Y/%m/%d"):
    # noinspection PyBroadException
    try:
        create_date = datetime.datetime.strptime(value, sql_type).date()
    except Exception:
        create_date = datetime.datetime.now().date()
    return create_date


date_convert = partial(convert_date, sql_type=SQL_DATE)

date_time_convert = partial(convert_date, sql_type=SQL_DATE_TIME)


def on_duplicate_sql(*args, item: scrapy.Item):
    if args and isinstance(item, scrapy.Item):
        dup_keys = list()

        for index, key in enumerate(args):
            if index == 0:
                update_str = '  ON DUPLICATE KEY UPDATE {}="{}"'.format(key, item.get(key))
            else:
                update_str = '{}="{}"'.format(key, item.get(key))
            dup_keys.append(update_str)
        return ', '.join(dup_keys)
    else:
        return ''



def add_jobbole(value):
    return 'jobbole_' + value

def replace_splash(value):
    """去除斜线"""
    return value.replace('/', '')


def handle_jobaddr(value):
    """地址处理"""
    return ''.join(x.strip() for x in value.split('\n') if '查看地图' not in x)


def handle_strip(value):
    return value


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
        input_processor=MapCompose(get_num, rm_comma)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_num, rm_comma)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_num, rm_comma)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(tag_filter),
        output_processor=Join(',')
    )
    content = scrapy.Field()


class JobboleItemLoader(ItemLoader):
    """ 默认提取第一个值"""
    default_output_processor = TakeFirst()


class ZhiHuItemLoader(JobboleItemLoader):
    pass


class QuestionItem(scrapy.Item):
    """知乎question item"""
    zhihu_id = scrapy.Field()
    topics = scrapy.Field(
        input_processor=Join(',')
    )
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field(
        input_processor=MapCompose(rm_comma)
    )
    comments_num = scrapy.Field(
        input_processor=MapCompose(get_num)
    )
    watch_user_num = scrapy.Field(
        input_processor=MapCompose(rm_comma)
    )
    click_num = scrapy.Field(
        input_processor=MapCompose(rm_comma),
        output_processor=TakeLast
    )
    crawl_time = scrapy.Field(
        input_processor=MapCompose(date_time_convert)
    )
    crawl_update_time = scrapy.Field(
        input_processor=MapCompose(date_time_convert)
    )

    def get_sql(self):
        # col_names = ','.join(self.fields.keys())
        # print(item._values.keys(),len(list(item._values.keys())),sep='\n')
        # 占位符
        num_s = ('%s,' * len(self.fields.keys())).strip(',')
        # # 添加values
        # values = ", ".join(str(self[x]) for x in self.fields.keys())
        mark = ",".join("'{}'" for _ in self.fields.keys())
        insert_sql = """
                   insert into  question ({}) 
                   VALUES({})
                   """.format(mark.replace("'", ''), num_s)  # 保持个数一致，防止有些参数未取到;
        insert_sql = insert_sql.format(*self.keys())

        #  添加重复字段更新
        dup_str = on_duplicate_sql('crawl_update_time', 'watch_user_num', 'click_num', 'comments_num',
                                   item=self)
        return insert_sql + dup_str


class AnswerItem(scrapy.Item):
    """知乎answer item"""
    zhihu_id = scrapy.Field(
        # output_processor=TakeFirst
    )
    url = scrapy.Field(
        # output_processor=TakeFirst
    )
    question_id = scrapy.Field(
        # output_processor=TakeFirst
    )
    author_id = scrapy.Field(
        # output_processor=TakeFirst
    )
    content = scrapy.Field(
        # output_processor=TakeFirst
    )
    praise_num = scrapy.Field(
        # output_processor=TakeFirst
    )
    comments_num = scrapy.Field(
        # output_processor=TakeFirst
    )
    create_time = scrapy.Field(
        input_processor=MapCompose(int, time.localtime, date_time_convert),
        # output_processor=TakeFirst
    )
    update_time = scrapy.Field(
        input_processor=MapCompose(int, time.localtime, date_time_convert),
        # output_processor=TakeFirst
    )
    crawl_time = scrapy.Field(
        input_processor=MapCompose(date_time_convert),
        # output_processor=TakeFirst
    )
    crawl_update_time = scrapy.Field(
        input_processor=MapCompose(date_time_convert),
        # output_processor=TakeFirst
    )

    def get_sql(self):
        """ 暂时未考虑重复代码问题"""
        # col_names = ','.join(self.fields.keys())
        # print(item._values.keys(),len(list(item._values.keys())),sep='\n')
        # 占位符
        num_s = ('%s,' * len(self.fields.keys())).strip(',')
        # # 添加values
        # values = ", ".join(str(self[x]) for x in self.fields.keys())
        mark = ",".join("'{}'" for _ in self.fields.keys())
        insert_sql = """
                   insert into  answer ({}) 
                   VALUES({})
                   """.format(mark.replace("'", ''), num_s)  # 保持个数一致，防止有些参数未取到;
        insert_sql = insert_sql.format(*self.keys())

        #  添加重复字段更新
        dup_str = on_duplicate_sql('crawl_update_time', 'update_time', 'praise_num', 'comments_num',
                                   item=self)
        return insert_sql + dup_str


class LagouJobItem(scrapy.Item):
    # 拉勾网职位
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    tags = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(replace_splash),
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(replace_splash),
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(replace_splash),
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field(
        input_processor=MapCompose(handle_strip),
    )
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, handle_jobaddr),
    )
    company_name = scrapy.Field(
        input_processor=MapCompose(handle_strip),
    )
    company_url = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    # def get_sql(self):
    #     insert_sql = """
    #         insert into lagou_job(title, url, salary, job_city, work_years, degree_need,
    #         job_type, publish_time, job_advantage, job_desc, job_addr, company_url, company_name, job_id)
    #         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE job_desc=VALUES(job_desc)
    #     """
    #
    #     job_id = get_num(self["url"])
    #     params = (self["title"], self["url"], self["salary"], self["job_city"], self["work_years"], self["degree_need"],
    #               self["job_type"], self["publish_time"], self["job_advantage"], self["job_desc"], self["job_addr"], self["company_url"],
    #               self["company_name"], job_id)
    #
    #     return insert_sql, params
    def get_sql(self):
        # col_names = ','.join(self.fields.keys())
        # print(item._values.keys(),len(list(item._values.keys())),sep='\n')
        # 占位符
        num_s = ('%s,' * len(self.keys())).strip(',')
        # # 添加values
        # values = ", ".join(str(self[x]) for x in self.fields.keys())
        mark = ",".join("'{}'" for _ in self.keys())
        insert_sql = """
                   insert into  lagou ({}) 
                   VALUES({})
                   """.format(mark.replace("'", ''), num_s)  # 保持个数一致，防止有些参数未取到;
        insert_sql = insert_sql.format(*self.keys())

        #  添加重复字段更新
        dup_str = on_duplicate_sql('crawl_update_time', item=self)
        return insert_sql + dup_str

class LagouJobItemLoader(JobboleItemLoader):
    pass
