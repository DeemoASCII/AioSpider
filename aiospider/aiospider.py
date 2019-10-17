#!/usr/bin/env python3
# encoding: utf-8
# time    : 2019/10/10 1:45 下午
import asyncio
import concurrent
import json
import pickle
import socket
from typing import List, Dict

import h11
import httpx
import uvloop

from redisqueue import RedisQueue
from request import Request
from response import Response
from utils.log import get_logger
from utils.retry import retry


class RemoteException(Exception):
    pass


class AioSpider:
    name: str = 'AioSpider'
    start_urls: List[str] = []
    request_delay: int = 0
    retry_delay: int = 5
    use_redis = False
    concurrency = 10  # 控制并发

    retry_exceptions = []

    def __init__(self):
        self.queue = None
        self.client: httpx.AsyncClient = httpx.AsyncClient()
        self.dupe_tasks: List[str] = []
        self.logger = get_logger(name=self.name)
        self.sem = asyncio.Semaphore(self.concurrency)
        self.task_queue: List[Request] = []

    async def add_task(self, task: Request):
        if task.dont_filter:
            self.dupe_tasks.append(task.taskId)
            await self.queue.put(task)
        elif task.taskId not in self.dupe_tasks:
            self.dupe_tasks.append(task.taskId)
            await self.queue.put(task)

    async def _workflow(self, sem):
        async with sem:
            while True:
                task = await self.queue.get()
                try:
                    resp = await self._request(task)
                    if task.callback:
                        result = await eval(task.callback)(resp)
                        if result:
                            await self.result(result)
                except KeyboardInterrupt:
                    self.task_queue.append(task)
                    self._stop()
                    raise KeyboardInterrupt
                except Exception as e:
                    self.logger.error(task)
                    self.logger.exception(e)
                finally:
                    self.queue.task_done()
                    await asyncio.sleep(self.request_delay)

    async def start(self):
        for url in self.start_urls:
            task = Request(method='get', url=url, callback='self.parse', dont_filter=True, priority=1)
            await self.add_task(task)

    @retry(httpx.exceptions.ProxyError, concurrent.futures._base.TimeoutError, ConnectionResetError, RemoteException,
           socket.gaierror, h11._util.RemoteProtocolError, *retry_exceptions,
           sleep=retry_delay)
    async def _request(self, task: Request):
        resp = await self.client.request(
            method=task.method.upper(), url=task.url, data=task.data, files=task.files,
            json=task.json, params=task.params, headers=task.headers, stream=task.stream,
            timeout=task.timeout, auth=task.auth, allow_redirects=task.allow_redirects,
            proxies=task.proxies, cookies=task.cookies, cert=task.cert, verify=task.verify, trust_env=task.trust_env)
        await resp.close()
        if resp.status_code >= 500:
            self.logger.error(f'遇到了状态码为{resp.status_code}的错误')
            raise RemoteException()
        resp = Response(resp=resp, task=task, metadata=task.metadata)
        return resp

    async def _memory_main(self):
        self.logger.info('爬虫启动！！！！！使用内存队列..')
        self.queue = asyncio.PriorityQueue(maxsize=1000000)
        if self.task_queue:
            for task in self.task_queue:
                await self.queue.put(task)
        if self.queue.empty():
            await self.start()
        tasks = [asyncio.create_task(self._workflow(self.sem)) for _ in range(self.concurrency)]
        await self.queue.join()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _redis_main(self):
        self.logger.info('爬虫启动！！！！！')
        self.queue = RedisQueue()
        if self.queue.empty():
            await self.start()
        tasks = [asyncio.create_task(self._workflow(self.sem)) for _ in range(self.concurrency)]
        await self.queue.join()
        # for task in tasks:
        #     task.cancel()
        await asyncio.wait(tasks)

    def _stop(self):
        while True:
            if self.queue.empty():
                break
            task = self.queue.get_nowait()
            self.task_queue.append(task)
            self.queue.task_done()

    def stop(self):
        pass

    def run(self):
        try:
            with open(f'{self.name}_dupe_tasks', 'rb') as f:
                self.dupe_tasks = list(pickle.load(f))
        except FileNotFoundError:
            pass
        try:
            with open(f'{self.name}_task_queue', 'rb') as f:
                self.task_queue = pickle.load(f)
        except FileNotFoundError:
            pass

        uvloop.install()
        try:
            if self.use_redis:
                asyncio.run(self._redis_main())
            else:
                asyncio.run(self._memory_main())
        finally:
            self.logger.info('爬虫关闭！！！！！')
            with open(f'{self.name}_dupe_tasks', 'wb') as f:
                pickle.dump(set(self.dupe_tasks), f)
            with open(f'{self.name}_task_queue', 'wb') as f:
                pickle.dump(self.task_queue, f)
            if not self.use_redis:
                self._stop()
            self.stop()

    async def parse(self, response):
        self.logger.info(response.doc('title').text())
        pass

    async def result(self, result: Dict):
        pass
