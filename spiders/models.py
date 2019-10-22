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

    def job_validate(self):
        try:
            self.validate_employer()
            return True
        except AssertionError:
            return False

    def validate_employer(self):
        assert len(self.employer) <= 64

    def validate_name(self):
        assert len(self.name) <= 64
