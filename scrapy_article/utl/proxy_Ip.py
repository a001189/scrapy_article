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
