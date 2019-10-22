#!/usr/bin/env python3
# encoding: utf-8
# time    : 2019/10/21 1:17 下午
import re
from urllib.parse import urlparse

from aiospider.request import Request
from spiders import parse_salary, parse_loc, parse_work_year, parse_degree
from spiders.models import Job
from spiders.zhaopin import ZPSpiders


def parse_url(base_url, url):
    parsed_url = urlparse(base_url)
    if url.startswith('/'):
        return parsed_url.scheme + '://' + parsed_url.netloc + url
    elif url.startswith('https'):
        return url.replace('https', 'http')
    return url


class JRZPSpider(ZPSpiders):
    name = '今日招聘'

    domain = 'jinrizhaopin2'

    start_urls = ['http://www.chinahzbj.com/hotjob/com1034528.shtml', 'http://www.jrzp.com/hotjob/com190642.shtml',
                  'http://www.jrzp.com/hotjob/com153816.shtml', 'http://www.jrzp.com/hotjob/com266939.shtml',
                  'http://www.jrzp.com/hotjob/com267198.shtml', 'http://www.jrzp.com/hotjob/com189187.shtml',
                  'http://www.jrzp.com/hotjob/com264198.shtml', 'http://www.jrzp.com/hotjob/com258134.shtml',
                  'http://www.jrzp.com/hotjob/com258651.shtml', 'http://www.jrzp.com/hotjob/com188234.shtml',
                  'http://www.whxzrc.com/hotjob/com2909093.shtml', 'http://www.chinahzbj.com/hotjob/com584840.shtml',
                  'http://www.jrzp.com/hotjob/com261400.shtml', 'http://www.chinahzbj.com/hotjob/com1025412.shtml',
                  'http://www.zjsxjob.com/hotjob/com256066.shtml', 'http://www.sxlfrc.com/hotjob/com259693.shtml',
                  'http://www.hzgsrc.com/hotjob/com2339892.shtml', 'http://www.jrzp.com/hotjob/com262666.shtml',
                  'http://www.jrzp.com/hotjob/com268563.shtml', 'http://www.jrzp.com/hotjob/com153716.shtml',
                  'http://www.jrzp.com/hotjob/com152860.shtml', 'http://www.jrzp.com/hotjob/com262696.shtml',
                  'http://www.jrzp.com/hotjob/com261903.shtml']

    async def parse(self, resp):
        if resp.ok:
            self.logger.info(resp.doc('title').text())
            for item in resp.doc('.listCon > ul > li > a').items():
                task = Request(method='get', url=parse_url(resp.url, item.attr('href')), proxy=self.proxy,
                               proxy_auth=self.proxy_auth,
                               priority=5, callback='self.detail')
                yield task
            next_url = resp.doc('.pageNav > a:contains(下一页)').attr('href')
            if next_url:
                yield Request(method='get', url=parse_url(resp.url, next_url),
                              proxy=self.proxy, proxy_auth=self.proxy_auth,
                              priority=10, callback='self.parse')

    async def detail(self, resp):
        if resp.ok:
            self.logger.info(resp.doc('title').text())
            salary_low, salary_high = parse_salary(resp.doc('.zwm em').text() + '/月')
            items = resp.doc('.jbyq span')
            edu = items.eq(2).text()
            years = items.eq(1).text()
            job = Job(name=resp.doc('.zwjbnr .zwm span').text(), degree=parse_degree(edu),
                      salary_low=salary_low, salary_high=salary_high,
                      location_ids=parse_loc(items.eq(0).text()), years=parse_work_year(years),
                      description=resp.doc(
                          'body > div.main > div.m-con > div > div.mLeft.fl > div:nth-child(1) > div.zwmsCon').text(),
                      address=resp.doc('.gzddCon > span').text(),
                      employer=resp.doc('#comName').text(), openid=re.sub(r'.*?/job|\.shtml', '', resp.url) + '@今日招聘',
                      publish_date=re.sub(r'\s\d+:\d+:\d+', '', resp.doc('.gsmc > span').eq(0).text()))
            task = Request(method='post', url=f'https://{self.domain}.mesoor.com/api/jobs', json=job.to_dict(),
                           headers={
                               'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJpYXQiOjE1NjA4MjUyNzcsImV4cCI6MTYyMzg5NzI2NSwidXNlclJvbGUiOjB9.3q2HXTkXzoDNfyHIanl_c-SH0UMvjXVxAbAMAkIwSxY'
                           }, callback='self.create_job', metadata=job.to_dict(), priority=5)
            yield task


if __name__ == '__main__':
    JRZPSpider.run()
