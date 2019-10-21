#!/usr/bin/env python3
# encoding: utf-8
# time    : 2019/10/17 2:08 下午
import re

from aleph.mappers.taggers.parsers import parse_salary_amount

from spiders import loc_normalizer


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
