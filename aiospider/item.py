#!/usr/bin/env python3
# encoding: utf-8
# time    : 2019/10/18 11:46 上午
from _sha256 import sha256

import ujson

from aiospider.models import BaseTask


class ItemMeta(type):
    """
    Metaclass for an item
    """

    def __new__(cls, name, bases, attrs):
        __fields = []
        if annotations := attrs.get('__annotations__'):
            __fields = [field_name
                        for field_name, _ in annotations.items()]

        attrs["fields"] = __fields
        new_class = type.__new__(cls, name, bases, attrs)
        return new_class


class Item(metaclass=ItemMeta):
    """
    Item class for each item
    """

    @property
    def dict(self):
        result = {}
        for each in self.fields:
            result[each] = eval(f'self.{each}')
        return result

    @dict.setter
    def dict(self, value):
        self.dict = value

    def __repr__(self):
        return f"<AioSpiderItem {ujson.dumps(self.dict, ensure_ascii=False)}>"

    def __str__(self):
        return f"<AioSpiderItem {ujson.dumps(self.dict, ensure_ascii=False)}>"


class Result(BaseTask):

    def __init__(self, url, item, *, priority: int, dont_filter: bool = False, age: int = 3 * 60 * 60 * 24):
        super().__init__(priority, dont_filter, age)
        self.item = item
        self.url = url

    def __repr__(self):
        return f"<AioSpiderResult from url: {self.url} >"

    def __str__(self):
        return f"<AioSpiderResult from url: {self.url} >"

    @property
    def taskId(self) -> str:
        dupe_str = sha256()
        dupe_str.update(ujson.dumps(self.item.dict).encode())
        return dupe_str.hexdigest()
