#!/usr/bin/env python3
# encoding: utf-8
# time    : 2019/10/21 5:12 下午
import re

import ujson
from pyquery import PyQuery

from aiospider.item import Item
from aiospider.request import Request
from spiders import parse_salary, parse_work_year, parse_loc, parse_degree
from spiders.zhaopin import ZPSpiders


class JobItem(Item):
    # url = ''
    name = ''
    description = None
    address = None
    employer = ''
    headcount = None
    years = None
    degree = None
    salary_low = None
    salary_high = None
    location_ids = None
    status = 1
    openid = ''
    publish_date = None


def parse_job_detail(resp):
    job = JobItem()
    job.url = resp.url
    job.name = resp.doc('.zp_posit').text()
    job.salary_low, job.salary_high = parse_salary(resp.doc('.zp_wage').text())
    job.description = resp.doc('.posit_claim_detail').text()
    job.years = parse_work_year(resp.doc('.exp').text())
    job.location_ids = parse_loc(resp.doc('.addr').text())
    job.degree = parse_degree(resp.doc('.edu').text())
    job.employer = resp.doc('.buss_name').text()
    job.publish_date = resp.doc('.freshdate').text()
    job.openid = re.search(r'(?<=jobdetail_)\d+(?=\.)', resp.url).group() + '@一览英才'
    return job


class YLYCSpider(ZPSpiders):
    name = '一览英才网'

    start_urls = ["4", "825", "6", "41", "216", "5", "837", "822", "188", "343", "865", "172", "877", "340", "418",
                  "812"]
    base_url = 'http://m.job1001.com/search/'

    async def start(self):
        for url in self.start_urls:
            params = {
                'totalid': url,
                '1': 1,
                'fromtype': 'page',
                'page': 0
            }
            yield Request(method='post', url=self.base_url, params=params, callback='self.parse',
                          priority=10, proxy=self.proxy, proxy_auth=self.proxy_auth, metadata=params)

    async def parse(self, resp):
        if resp.ok:
            params = resp.metadata
            count = 0
            doc = resp.doc
            if 'getAllJobList' in resp.url:
                data = ujson.loads(resp.text)
                doc = PyQuery(data['info']['html'])
            for item in doc('li > a').items():
                count += 1
                job_url = 'http:' + item.attr('href')
                yield Request(method='get', url=job_url, callback='self.job_detail', priority=7,
                              proxy=self.proxy, proxy_auth=self.proxy_auth)
            if 'totalid' in resp.url:
                if count >= 20:
                    params['page'] += 1
                    yield Request(method='POST', url=self.base_url, params=params, callback='self.parse',
                                  proxy=self.proxy, proxy_auth=self.proxy_auth, priority=10, metadata=params)

    async def job_detail(self, resp):
        if resp.ok:
            self.logger.info(resp.doc('title').text())
            comp_url = resp.doc('.posit_detail').attr('href')
            job = parse_job_detail(resp)
            if comp_url:
                yield Request(method='get', url='http:' + comp_url, callback='self.comp_detail',
                              proxy=self.proxy, proxy_auth=self.proxy_auth, priority=5)
            yield job

    async def comp_detail(self, resp):
        if resp.ok:
            self.logger.info(resp.doc('title').text())
            description = resp.doc('.buss_brief p').text()
            address = resp.doc('.comp_palce_row').text()
            comp_id = re.search(r'(?<=companydetail_).*?(?=\.htm)', resp.url).group()
            yield Request(method='get',
                          url=f'http://m.job1001.com/company/ajax/?detail=getAllJobList&v=3.0&company_id={comp_id}',
                          callback='self.parse', proxy=self.proxy, proxy_auth=self.proxy_auth, priority=3)


if __name__ == '__main__':
    YLYCSpider.run()
