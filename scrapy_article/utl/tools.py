#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# @Time    : 2018/4/19 15:35
# @Author  : ysj
from collections import Sequence


def get(squence=None, index=0, default=0):
    if not isinstance(squence, Sequence):
        raise TypeError('sequence must be a Sequence')
    try:
        return squence[index]
    except IndexError:
        return default


def typed_property(name, expected_type):
    storage_name = '_' + name
    @property
    def prop(self):
        return getattr(self, storage_name)
    @prop.setter
    def prop(self, value):
        if not isinstance(value, expected_type):
            raise TypeError('{} must be a {}'.format(name, expected_type))
        setattr(self, storage_name, value)
        return prop


class Person:
    name = typed_property('name', str)

    age = typed_property('age', int)

    def __init__(self, name, age):
        self.name = name
        self.age = age


Person('sad', 'sadas')


from functools import partial
String = partial(typed_property, expected_type=str)
Integer = partial(typed_property, expected_type=int)
# Example:
class Person:
    name = String('name')
    age = Integer('age')
    def __init__(self, name, age):
        self.name = name
        self.age = age

Person('sad', 'sadas')