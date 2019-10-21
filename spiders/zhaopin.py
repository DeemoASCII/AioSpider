#!/usr/bin/env python3
# encoding: utf-8
# time    : 2019/10/21 2:28 下午
from urllib.request import quote

from aiohttp import BasicAuth

from aiospider.aiospider import AioSpider
from aiospider.request import Request


class ZPSpiders(AioSpider):
    name = '招聘网站爬虫'

    domain = ''

    proxy = 'http://http-pro.abuyun.com:9010'
    proxy_auth = BasicAuth('H1C874789LK67IJP', '5C00CC9500B2633F')

    async def create_job(self, resp):
        if resp.ok:
            self.logger.info('create_job:' + resp.text)
            task = Request(method='put',
                           url=f'https://{self.domain}.mesoor.com/api/open-jobs/{quote(resp.metadata["openid"])}/agora/status?blackList=years&overwrite=true',
                           json={"enabled": True}, headers={
                    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAiLCJpYXQiOjE1NjA4MjUyNzcsImV4cCI6MTYyMzg5NzI2NSwidXNlclJvbGUiOjB9.3q2HXTkXzoDNfyHIanl_c-SH0UMvjXVxAbAMAkIwSxY'
                }, callback='self.create_agora', priority=1)
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
