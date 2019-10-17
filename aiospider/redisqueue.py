#!/usr/bin/env python3
# encoding: utf-8
# time    : 2019/10/11 6:06 下午
import asyncio
import collections
import pickle
from asyncio import Queue
import aioredis
import redis
import ujson

from request import Request


class RedisQueue(Queue):

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, password=None, maxsize=100,
                 loop=None):
        super().__init__(maxsize, loop=loop)
        # self.redis = None
        # self.host = host
        # self.port = port
        # self.db = db
        # self.password = password
        self.pool = redis.ConnectionPool(host=host, port=port, db=db, password=password)
        self.__init()

    # async def create_pool(self):
    #     self.redis = await aioredis.create_redis_pool(
    #         f'redis://:{self.password}@{self.host}:{self.port}/{self.db}' if self.password else f'redis://{self.host}:{self.port}/{self.db}',
    #         maxsize=self._maxsize, loop=self._loop)
    #     await self.__init()

    def _init(self, maxsize):
        self._queue = []

    def __init(self):
        r = redis.Redis(connection_pool=self.pool)
        self._unfinished_tasks = r.zcount('task_queue', '-inf', '+inf')

    def _put(self, item):
        r = redis.Redis(connection_pool=self.pool)
        r.zadd('task_queue', item.priority, pickle.dumps(item, protocol=-1))

    def _get(self):
        r = redis.Redis(connection_pool=self.pool)
        task = r.zpopmin('task_queue', count=1)
        return pickle.loads(task)

    def empty(self):
        r = redis.Redis(connection_pool=self.pool)
        """Return True if the queue is empty, False otherwise."""
        return not r.zcount('task_queue', '-inf', '+inf')
