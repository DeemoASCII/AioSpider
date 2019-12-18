#!/usr/bin/env python3
# encoding: utf-8
# time    : 2019/10/10 1:45 下午
import asyncio
import pickle
from _signal import SIGINT, SIGTERM
from asyncio import QueueEmpty, CancelledError
from inspect import isasyncgen, iscoroutine
from time import time
from typing import List, Optional

import aiohttp
import uvloop
from aiohttp import ClientResponse

from aiospider.exceptions import InvalidFunc, RequestStatusError
from aiospider.item import Item, Result
from aiospider.models import BaseTask
from aiospider.request import Request
from aiospider.response import Response
from aiospider.utils.log import get_logger
from aiospider.utils.retry import retry


class AioSpider:
    name: str = 'AioSpider'
    start_urls: List[str] = []
    request_delay: int = 0
    retry_delay: int = 5
    use_redis = False
    concurrency = 10  # 控制并发

    ruler = {}
    cookies = []
    retry_exceptions = []

    def __init__(self, name, ruler):
        self.queue = None
        if name:
            self.name = name
        if ruler:
            self.ruler = ruler
        self.client: Optional[aiohttp.ClientSession] = None
        self.dupe_tasks: List[str] = []
        self.logger = get_logger(name=self.name)
        self.sem = asyncio.Semaphore(self.concurrency)
        self.tasks_queue: List[BaseTask] = []
        self.failed_counts = 0
        self.success_counts = 0
        self.delay = 300
        self.last_display = None

    async def _add_task(self, task: BaseTask):
        if task.dont_filter or task.taskId not in self.dupe_tasks or 0 < task.expire < int(time()):
            self.dupe_tasks.append(task.taskId)
            await self.queue.put(task)

    async def _workflow(self, sem, cookie=None):
        async with sem:
            while True:
                if not self.last_display or self.last_display + self.delay < int(time()):
                    self.last_display = int(time())
                    self.logger.info(f'目前已经成功抓取了{self.success_counts}个页面！')
                    self.logger.info(f'目前抓取失败的页面有{self.success_counts}个！')
                task = await self.queue.get()
                try:
                    if isinstance(task, Request):
                        await self._process_request(task, cookie)
                    if isinstance(task, Response):
                        await self._process_callback(task)
                    if isinstance(task, Result):
                        await self._process_result(task)
                except (KeyboardInterrupt, CancelledError) as e:
                    raise e
                except Exception as e:
                    self.logger.exception(e)
                finally:
                    self.queue.task_done()
                    await asyncio.sleep(self.request_delay)

    async def _process_request(self, request: Request, cookie=None):
        request = await self.request_middleware(request, cookie)
        self.logger.debug(request)
        response = await self._request(request)
        self.logger.debug(response)
        await self._add_task(response)

    async def _process_callback(self, response: Response):
        if response.callback:
            func = eval(response.callback)
            callback_result = func(response)
            if iscoroutine(callback_result):
                result = await callback_result
                if result:
                    if isinstance(result, Item):
                        result = await self._process_item(result, response)
                    await self._add_task(result)
            elif isasyncgen(callback_result):
                async for each in func(response):
                    if isinstance(each, Item):
                        each = await self._process_item(each, response)
                    await self._add_task(each)
            else:
                raise InvalidFunc(f'Invalid func type {type(callback_result)}')

    async def _process_item(self, item: Item, resp: Response):
        result = Result(url=resp.url, item=item, priority=resp.priority - 5, dont_filter=resp.dont_filter, age=resp.age)
        return result

    async def _process_result(self, result):
        item = result.item
        await self.pipeline(item)

    async def _process_response(self, resp: ClientResponse, req: Request):
        content = await resp.read()
        response = Response(url=str(resp.url), method=resp.method, metadata=req.metadata,
                            cookies=resp.cookies, headers=resp.headers,
                            history=resp.history, status=resp.status,
                            callback=req.callback, request=req, content=content, age=req.age)
        if response.ok:
            self.success_counts += 1
        else:
            self.failed_counts += 1
        return response

    async def start(self):
        for url in self.start_urls:
            task = Request(method='get', url=url, callback='self.parse', dont_filter=True, priority=1)
            yield task

    @retry(Exception, sleep=retry_delay)
    async def _request(self, task: Request) -> Response:
        async with self.client.request(
                method=task.method,
                url=task.url,
                params=task.params,
                data=task.data,
                json=task.json,
                headers=task.headers,
                cookies=task.cookies,
                auth=task.auth,
                allow_redirects=task.allow_redirects,
                max_redirects=task.max_redirects,
                proxy=task.proxy,
                proxy_auth=task.proxy_auth,
                verify_ssl=task.verify_ssl,
                ssl=task.ssl
        ) as resp:
            if resp.status >= 500 or 400 <= resp.status < 404:
                raise RequestStatusError(f'response status code: {resp.status}')
            response = await self._process_response(resp, task)
            return response

    async def _main(self):
        self.logger.info('AioSpider started！！！！！Use memory queue..')
        self.loop = asyncio.get_event_loop()
        self.queue = asyncio.PriorityQueue(maxsize=1000000)
        self.client = aiohttp.ClientSession()
        await self.before_start()
        for _signal in (SIGINT, SIGTERM):
            self.loop.add_signal_handler(
                _signal, lambda: asyncio.create_task(self._stop(_signal)))
        await self._load_task()
        if self.queue.empty():
            async for task in self.start():
                await self._add_task(task)
        if self.cookies:
            workers = [asyncio.create_task(self._workflow(self.sem, cookie)) for cookie in self.cookies]
        else:
            workers = [asyncio.create_task(self._workflow(self.sem)) for _ in range(self.concurrency)]
        for worker in workers:
            self.logger.info(f'Worker started: {id(worker)}')
        await self.queue.join()
        await self.client.close()
        await self._cancel_tasks()

    async def _stop(self, _signal):
        await self.client.close()
        self.logger.info(f"Stopping spider: {self.name}")
        self._save_task()
        await self._cancel_tasks()

    def stop(self):
        pass

    @staticmethod
    async def _cancel_tasks():
        tasks = []
        for task in asyncio.Task.all_tasks():
            if task is not asyncio.tasks.Task.current_task():
                tasks.append(task)
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    def _start(self):
        try:
            asyncio.run(self._main())
        finally:
            self.logger.info('AioSpider Finished！！！！！')
            self.logger.info(
                f"Total requests: {self.failed_counts + self.success_counts}"
            )
            if self.failed_counts:
                self.logger.info(f"Failed requests: {self.failed_counts}")
            self.stop()

    @classmethod
    def run(cls, name=None, ruler=None):
        uvloop.install()
        spider_ins = cls(name=name, ruler=ruler)
        spider_ins._start()
        return spider_ins

    async def parse(self, response):
        self.logger.info(response.doc('title').text())
        raise NotImplementedError('parse is not implemented')

    async def _load_task(self):
        try:
            with open(f'{self.name}_dupe_tasks', 'rb') as f:
                self.dupe_tasks = pickle.load(f)
        except FileNotFoundError:
            pass
        try:
            with open(f'{self.name}_tasks_queue', 'rb') as f:
                self.tasks_queue = pickle.load(f)
        except FileNotFoundError:
            pass
        if self.tasks_queue:
            for task in self.tasks_queue:
                await self._add_task(task)

    def _save_task(self):
        with open(f'{self.name}_dupe_tasks', 'wb') as f:
            pickle.dump(self.dupe_tasks, f)

        while True:
            try:
                task = self.queue.get_nowait()
                self.tasks_queue.append(task)
                self.queue.task_done()
            except QueueEmpty:
                break

        with open(f'{self.name}_tasks_queue', 'wb') as f:
            pickle.dump(self.tasks_queue, f)

    async def pipeline(self, item):
        pass

    async def request_middleware(self, request, cookie=None):
        return request

    async def before_start(self):
        pass
