#! /usr/local/bin python3.6
"""
@Time    : 2018/4/26 20:57
@Author  : ysj
@Site    : 
@File    : tem2p.py.py
@Software: PyCharm
"""
import os
import time
from uuid import uuid4
import urllib.parse as parse
from selenium import webdriver
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from scrapy.selector import Selector
from functools import partial


def get_url(x):
    if x > 1:

        url = 'https://www.6686z.com/Html/84/index-{}.html'.format(x)
    else:
        url = 'https://www.6686z.com/Html/84/'
    return url


# # 文章列表
# s.css('.box.list.channel li a::attr(href)').extract()
# # title
# s.css('.page_title h1::text').extract()
# # 正文
# s.css('.content font::text').extract()


def get_browser():
    chrome_opt = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_opt.add_experimental_option("prefs", prefs)
    browser = webdriver.Chrome(chrome_options=chrome_opt)
    return browser







def download_page(url, browser):
    """文章列表,最多尝试5次"""
    page_down_count = 0

    def get_artile(artcle_url):
        """下载文章"""
        nonlocal count  # 下载标记，最多尝试三次
        browser.get(artile_real_url)
        selector_article = Selector(text=browser.page_source)
        os.path.exists('title') or os.mkdir('title')
        title = 'title/' + selector_article.css('.page_title h1::text').extract_first(str(uuid4())) + '.txt'
        content_list = selector_article.css('.content font::text').extract()
        with open(title, 'w') as f:
            for i in content_list:
                line = '    ' + i.replace('\u3000', ' ').strip() + '\n'
                f.write(line)
        if os.path.getsize(title) < 1024 and count <3:
            time.sleep(5)
            count += 1
            get_artile(artile_url)

    while page_down_count < 5:
        browser.get(url)
        selector = Selector(text=browser.page_source)
        article_url_list = selector.css('.box.list.channel li a::attr(href)').extract()
        if article_url_list:
            for artile_url in article_url_list:
                artile_real_url = parse.urljoin(url, artile_url)
                count = 0
                get_artile(artile_real_url)
            browser.quit()
            break
        else:
            page_down_count += 1


download_page_num = partial(download_page, browser=get_browser())


def main():
    with ProcessPoolExecutor(max_workers=1) as pool:
        urls = (get_url(x) for x in range(1, 233))
        pool.map(download_page_num, urls)


def main2():
    urls = (get_url(x) for x in range(1, 233))
    for url in urls:
        download_page_num(url)


def download_page_num3(tuple_):
    return download_page(*tuple_)


def main3():

    # with ThreadPoolExecutor(max_workers=4) as pool:
    #     urls_browser = ((get_url(x), get_browser()) for x in range(1, 233))
    #     pool.map(download_page_num3, urls_browser)
    # with ThreadPoolExecutor(max_workers=4) as pool:
    #     urls = (get_url(x) for x in range(1, 10))
    #     browsers = (get_browser() for _ in range(1, 10))
    #     pool.map(download_page, urls, browsers)
    for i in range(0, 60):
        for j in range(i*4, (i+1)*4):
            print(j)
        with ThreadPoolExecutor(max_workers=4) as pool:
            urls = (get_url(x) for x in range(i*4, (i+1)*4))
            browsers = (get_browser() for _ in range(i*4, (i+1)*4))
            pool.map(download_page, urls, browsers)



if __name__ == '__main__':
    main3()
    # download_page_num(get_url(1))