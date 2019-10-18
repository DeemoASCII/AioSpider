#!/usr/bin/env python3
# encoding: utf-8
# time    : 2019/10/17 2:56 下午
from typing import Optional, List

from pydantic import BaseModel


class Job(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    employer: str
    headcount: Optional[str] = None
    years: Optional[int] = None
    degree: Optional[int] = None
    salary_low: Optional[int] = None
    salary_high: Optional[int] = None
    location_ids: Optional[List[int]] = None
    status: int = 1
    openid: str
    publish_date: Optional[str] = None

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'address': self.address,
            'employer': self.employer,
            'headcount': self.headcount,
            'years': self.years,
            'degree': self.degree,
            'salary_low': self.salary_low,
            'salary_high': self.salary_high,
            'location_ids': self.location_ids or None,
            'status': self.status,
            'openid': self.openid,
            'publish_date': self.publish_date,
        }
