#!/usr/bin/env python3
# encoding: utf-8
# time    : 2019/10/12 4:18 下午

from pyquery import PyQuery

from aiospider.request import Request
from spiders.models import Job
from spiders.zhaopin import ZPSpiders
from utils.edu_dicts import DEGREE_NUMS

gs_degree_map = {1: '初中', 2: '高中', 3: '中专', 4: '中专', 5: '专科', 6: '本科', 7: '硕士', 8: '博士', 9: 'MBA', 0: '不限'}


class GSLKSpider(ZPSpiders):
    name = '光速列客'
    start_urls = ['https://www.91lieke.com/api/pass/recruitment/1181762252382928896',
                  'https://www.91lieke.com/api/pass/recruitment/1181760245119057920',
                  'https://www.91lieke.com/api/pass/recruitment/1178460652839108608']

    domain = 'guangsulieke20191014'

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
            task = Request(method='post', url=f'https://{self.domain}.mesoor.com/api/jobs', json=j,
                           headers={
                               'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJpYXQiOjE1NjA4MjUyNzcsImV4cCI6MTYyMzg5NzI2NSwidXNlclJvbGUiOjB9.3q2HXTkXzoDNfyHIanl_c-SH0UMvjXVxAbAMAkIwSxY'
                           }, callback='self.create_job', metadata=j)
            yield task


if __name__ == '__main__':
    GSLKSpider.run()
