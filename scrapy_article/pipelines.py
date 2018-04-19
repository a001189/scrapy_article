# -*- coding: utf-8 -*-
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
import codecs
import json
import MySQLdb
from MySQLdb.cursors import DictCursor
from twisted.enterprise import adbapi
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ScrapyArticlePipeline(object):
    def process_item(self, item, spider):
        return item


class ImageJobbolePipeline(ImagesPipeline):
    """重写完成后的，path路径提取"""

    def item_completed(self, results, item, info):
        """判断 front_image_url 是否在items；不在则忽略"""
        if self.images_result_field in item.fields:
            for ok, x in results:
                if ok:
                    item[self.images_result_field] = x['path']
            # imagepipeline 下载 item 必须为数组，下载过后，变为str
            item['front_image_url'] = str(item['front_image_url']).strip('[]')
        # 可能存在部分没有图片，或无法访问的情况，设置为'',
        # 如：http://tech-blog.oss-cn-hangzhou.aliyuncs.com/requirements-specification-apes-dog-fight.jpg
            if not item['front_image_url']:
                item['front_image_url'] = ''
        return item
    # 以下函数会覆盖上面的函数
    # def process_item(self, item, spider):
    #
    #     return item


class JsonJobbolePipline:
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        item['create_date'], temp = str(item['create_date']), item['create_date']
        lines = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(lines)
        item['create_date'] = temp
        return item

    def spider_closed(self, spider):
        self.file.close()


class JsonJobboleExportPipline(JsonItemExporter):
    """scrapy自身提供的json保存接口"""
    def __init__(self):
        super().__init__()
        self.file = open('articl_export.json', 'wb')
        self.exportor = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exportor.start_exporting()

    def close_spider(self, spider):
        self.exportor.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exportor.export_item(item)
        return item


class MysqlPipeline:
    """ sql插入操作"""
    def __init__(self):
        self.conn = MySQLdb.connect('rm-uf69d6mp154aocu5tbo.mysql.rds.aliyuncs.com', 'root', '123QWEqwe', 'article_spider',
                                    charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        item.get_sql()
        self.conn.commit()

    def close_spider(self, spider):
        self.conn.close()


class MysqlTwistedPipeline:
    """twisted框架中的异步数据库操作，只支持关系数据库"""

    @classmethod
    def from_settings(cls, setting):
        mysql_info = setting['MYSQL_INFO']
        mysql_info['cursorclass'] = DictCursor
        dbpool = adbapi.ConnectionPool('MySQLdb', **mysql_info)
        # 增加创建表 未测试是否kexing
        try:
            dbpool.runInteraction(cls.create_table)
        except Exception as e:
            print(e)
        return cls(dbpool)

    def __init__(self, dbpool):
        """接收上一步的连接池"""
        self.dbpool = dbpool

    def process_item(self, item, spider):
        """twsited 异步插入sql"""
        # 增加无法下载图片的本地地址
        if item.__class__.__name__ == 'JobboleArticleItemTwo':
            item['front_image_path'] = item['front_image_path'] or 'null'
        qurey = self.dbpool.runInteraction(self.do_insert, item)
        # 错误处理
        qurey.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        """异步sql插入sql，错误处理"""
        print(failure)
        print(item.fields.keys())
        print(item._values.keys())
        print(item.fields.keys() - item._values.keys())
        # for key, value in item._values.items():
        #     print(key, value, sep=': ')
        pass

    def do_insert(self, cursor, item):
        if item.__class__.__name__ == 'JobboleArticleItemTwo':
            # 保留jobbole的爬取sql插入方式
            col_names = ','.join(item._values.keys())
            # print(item._values.keys(),len(list(item._values.keys())),sep='\n')
            # 占位符
            num_s = ('%s,' * len(item._values.keys())).strip(',')
            insert_sql = """
                                insert into jobbole_artile({0}) 
                                VALUES({1})
                            """.format(col_names, num_s)  # 保持个数一致，防止有些参数未取到
            cursor.execute(insert_sql, item._values.values())
        else:

            insert_sql = item.get_sql()
            print(insert_sql)
            # values = (item[x] for x in item.fields.keys())
            cursor.execute(insert_sql)

    @staticmethod
    def create_table(cursor, table='jobbole_artile'):
        create_sql = """
        CREATE TABLE `{}` (
          `url_object_id` varchar(50) NOT NULL,
          `title` varchar(255) NOT NULL,
          `create_date` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
          `url` varchar(300) DEFAULT NULL,
          `front_image_url` varchar(255) DEFAULT NULL,
          `front_image_path` varchar(255) DEFAULT NULL,
          `comment_nums` int(11) NOT NULL DEFAULT '0',
          `fav_nums` int(11) NOT NULL DEFAULT '0',
          `praise_nums` int(11) NOT NULL DEFAULT '0',
          `tags` varchar(255) DEFAULT NULL,
          `content` longtext NOT NULL,
          PRIMARY KEY (`url_object_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
      """.format(table)

        try:
            cursor.execute(create_sql)
        except Exception as e:
            print(e)
