#!/usr/bin/env python3
# encoding: utf-8
# time    : 2019/10/17 2:08 下午
import re

from aleph.mappers.taggers.parsers import parse_salary_amount

from spiders import loc_normalizer
from spiders.edu_dicts import DEGREE_NORMALIZE, DEGREE_NUMS


def parse_salary(text):
    if not text:
        return 0, 0
    text = re.sub(r'\+', '', text)
    res = parse_salary_amount(text)
    if res:
        return round(res[0]), round(res[1])
    else:
        return 0, 0


def parse_loc(loc):
    if not loc:
        return None
    loc = loc.strip()
    norm = loc_normalizer.normalize(loc)
    if norm:
        loc_id, province, city, county = norm
        return [loc_id]
    else:
        return


def parse_work_year(text):
    if isinstance(text, str):
        if re.search(r'\d+(?=年)?', text):
            years = int(re.search(r'\d+(?=年)?', text).group())
        else:
            years = 0
        return years
    return text


def parse_degree(text):
    if not text:
        return None
    if '不限' in text:
        return -4
    for k, v in DEGREE_NORMALIZE.items():
        if k in text:
            degree = DEGREE_NUMS.get(v.strip(), -4)
            return degree
    return None
