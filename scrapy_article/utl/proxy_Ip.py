#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# @Time    : 2018/4/26 15:23
# @Author  : ysj

import requests



def get(ip, port, type_='http'):
    proxy = {type_: "{2}://{0}:{1}".format(ip, port, type_)}
    print(proxy)
    try:
        res = requests.get(url='https://www.baidu.com', proxies=proxy, timeout=5)
        print(res)
    except Exception:
        pass
    else:
        print(res.status_code)
        print('ok')
        return True

header = """Host:www.xicidaili.com
If-None-Match:W/"1d228f16e7278f1b356476cd0ad20d4f"
Referer:http://www.xicidaili.com/api
Upgrade-Insecure-Requests:1
User-Agent:Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.4882.400 QQBrowser/9.7.13059.400
"""
def get_dict(value):
    import re
    s = (re.split(r'(?!^):', x.strip(), 1) for x in value.split('\n') if x)
    return dict(s)



from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time, random


def get_value(values):
    value = random.randint(10, 15)
    print(values,value)
    time.sleep( value)
    print(values,'-----end-----')


def main():
    with ThreadPoolExecutor(max_workers=3) as pool:
        pool.map(get_value, range(10))

def main2():
    with ProcessPoolExecutor(max_workers=3) as pool:
        pool.map(get_value, range(10))



import requests


if __name__ == '__main__':
    s = requests.get(url='http://python.lqhy.xyz/test', proxies={'http': 'http://183.6.111.7:808'})
    print(s)

['113.121.45.8', '48085', '高匿', 'HTTPS', '1分钟', '18-04-27 12:55']
['180.121.132.53', '3128', '高匿', 'HTTPS', '1分钟', '18-04-27 12:55']
['125.104.244.205', '25560', '高匿', 'HTTPS', '1分钟', '18-04-27 12:55']
['60.177.226.242', '18118', '高匿', 'HTTPS', '5天', '18-04-27 12:54']
['183.159.84.198', '18118', '高匿', 'HTTPS', '19天', '18-04-27 12:53']
['182.99.240.196', '61234', '高匿', 'HTTPS', '3小时', '18-04-27 12:53']
['60.177.229.200', '18118', '高匿', 'HTTPS', '18小时', '18-04-27 12:53']
['183.6.111.7', '808', '透明', 'HTTPS', '10小时', '18-04-27 12:52']
['223.241.78.147', '18118', '高匿', 'HTTPS', '25天', '18-04-27 12:50']

