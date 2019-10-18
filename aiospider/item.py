#!/usr/bin/env python3
# encoding: utf-8
# time    : 2019/10/18 11:46 上午

from inspect import isawaitable
from lxml import etree
from typing import Any

from aiospider.field import BaseField


class ItemMeta(type):
    """
    Metaclass for an item
    """

    def __new__(cls, name, bases, attrs):
        __fields = dict(
            {
                (field_name, attrs.pop(field_name))
                for field_name, object in list(attrs.items())
                if isinstance(object, BaseField)
            }
        )
        attrs["__fields"] = __fields
        new_class = type.__new__(cls, name, bases, attrs)
        return new_class


class Item(metaclass=ItemMeta):
    """
    Item class for each item
    """

    pass
