#!/usr/bin/env python3
# encoding: utf-8
# time    : 2019/10/12 4:18 下午

from aiohttp import BasicAuth
from pyquery import PyQuery
from urllib.request import quote

from aiospider.aiospider import AioSpider
from aiospider.request import Request
from spiders.models import Job
from utils.edu_dicts import DEGREE_NUMS

gs_degree_map = {1: '初中', 2: '高中', 3: '中专', 4: '中专', 5: '专科', 6: '本科', 7: '硕士', 8: '博士', 9: 'MBA', 0: '不限'}


class MiCaSpider(AioSpider):
    name = '光速列客'
    start_urls = ['https://www.91lieke.com/api/pass/recruitment/1181762252382928896',
                  'https://www.91lieke.com/api/pass/recruitment/1181760245119057920',
                  'https://www.91lieke.com/api/pass/recruitment/1178460652839108608']
    concurrency = 15

    proxy = 'http://http-pro.abuyun.com:9010'
    proxy_auth = BasicAuth('H1C874789LK67IJP', '5C00CC9500B2633F')

    async def parse(self, resp):
        if resp.ok:
            data = resp.json.get('data').get('jobs')
            for job in data:
                employer = job.get('companyName')
                openid = '光速列客@' + job.get('id')
                name = job.get('jobName')
                salary_high = job.get('maxSalaryConvert')
                salary_low = job.get('minSalaryConvert')
                headcount = job.get('recruitNumber')
                years = job.get('minWorkingLife')
                publish_date = job.get('publishDate')
                location_id = job.get('workCityId')
                address = job.get('workAddress')
                degree = DEGREE_NUMS[gs_degree_map[job.get('minimumDegree') or 0]]
                j = Job(name=name, openid=openid, employer=employer, salary_low=salary_low, salary_high=salary_high,
                        headcount=headcount, publish_date=publish_date, location_ids=[location_id], address=address,
                        degree=degree, years=years, )
                task = Request(method='get', url=f'https://www.91lieke.com/api/pass/job/{job.get("id")}',
                               dont_filter=True,
                               priority=10, metadata=j.to_dict(), callback='self.detail_page')
                yield task

    async def detail_page(self, resp):
        if resp.ok:
            desc = resp.json.get('data').get('jobDesc', '')
            desc = PyQuery(desc).remove('style').text()
            j = resp.metadata
            j.update(description=desc)
            task = Request(method='post', url='https://guangsulieke20191014.mesoor.com/api/jobs', json=j,
                           headers={
                               'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJpYXQiOjE1NjA4MjUyNzcsImV4cCI6MTYyMzg5NzI2NSwidXNlclJvbGUiOjB9.3q2HXTkXzoDNfyHIanl_c-SH0UMvjXVxAbAMAkIwSxY'
                           }, callback='self.create_job', metadata=j)
            yield task

    async def create_job(self, resp):
        if resp.ok:
            self.logger.info('create_job:' + resp.text)
            task = Request(method='put',
                           url=f'https://guangsulieke20191014.mesoor.com/api/open-jobs/{quote(resp.metadata["openid"])}/agora/status?blackList=years&overwrite=true',
                           json={"enabled": True}, headers={
                    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJpYXQiOjE1NjA4MjUyNzcsImV4cCI6MTYyMzg5NzI2NSwidXNlclJvbGUiOjB9.3q2HXTkXzoDNfyHIanl_c-SH0UMvjXVxAbAMAkIwSxY'
                }, callback='self.create_agora')
            yield task
        else:
            request = resp.request
            request.dont_filter = True
            yield request

    async def create_agora(self, resp):
        if resp.ok:
            self.logger.info('create_agora:' + resp.text)
        else:
            request = resp.request
            request.dont_filter = True
            yield request


if __name__ == '__main__':
    MiCaSpider.run()
