#! /usr/local/bin python3.6
"""
@Time    : 2018/4/9 21:47
@Author  : ysj
@Site    : 
@File    : main.py
@Software: PyCharm
"""
from scrapy.cmdline import execute

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# execute(['scrapy', 'crawl', 'jobbole2'])
# execute(['scrapy', 'crawl', 'zhihu'])
execute(['scrapy', 'crawl', 'lagou'])

