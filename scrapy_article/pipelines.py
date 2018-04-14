# -*- coding: utf-8 -*-
from scrapy.pipelines.images import ImagesPipeline
import codecs
import json
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
        if isinstance(item, dict) or self.images_result_field in item.fields:
            for ok, x in results:
                if ok:
                    item[self.images_result_field] = x['path']
        item['front_image_url'] = str(item['front_image_url']).strip('[]')
        return item


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