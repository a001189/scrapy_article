#! /usr/local/bin python3.6
"""
@Time    : 2018/4/14 22:12
@Author  : ysj
@Site    : 
@File    : md5.py
@Software: PyCharm
"""

import hashlib


def get_md5(word):
    word_bytes = word.encode('utf-8') if isinstance(word, str) else word
    md5 = hashlib.md5()
    md5.update(word_bytes)
    return md5.hexdigest()


def get_lagou(password):
    return get_md5('veenike' + get_md5(password) + 'veenike')


if __name__ == '__main__':
    print(get_md5('你好'))
    print(get_md5(b'hello'))
    print(get_md5(''))
    print(get_lagou('123qaz'))

