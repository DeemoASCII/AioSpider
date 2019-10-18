#!/usr/bin/env python3
# encoding: utf-8
# time    : 2019/10/18 3:21 下午
from aiospider.exceptions import NoTaskIdError
from time import time


class BaseTask:

    def __init__(self, priority: int, dont_filter: bool, age: int):
        self._priority = priority
        self._dont_filter = dont_filter
        self._age = age

    def __eq__(self, other):
        if isinstance(other, BaseTask):
            return self._priority == other._priority
        else:
            raise TypeError(f'"==" not supported between instances of "Task" and "{type(other)}"')

    def __lt__(self, other):
        if isinstance(other, BaseTask):
            return self._priority < other._priority
        else:
            raise TypeError(f'"<" not supported between instances of "Task" and "{type(other)}"')

    def __gt__(self, other):
        if isinstance(other, BaseTask):
            return self._priority > other._priority
        else:
            raise TypeError(f'">" not supported between instances of "Task" and "{type(other)}"')

    @property
    def priority(self) -> int:
        return self._priority

    @priority.setter
    def priority(self, value: int):
        self.priority = value

    @property
    def taskId(self) -> str:
        raise NoTaskIdError('There is no taskId,please rewrite this func')

    @taskId.setter
    def taskId(self, value: str):
        self.taskId = value

    @property
    def dont_filter(self) -> bool:
        return self._dont_filter

    @dont_filter.setter
    def dont_filter(self, value: bool):
        self.dont_filter = value

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int):
        self.age = value

    @property
    def expire(self) -> int:
        return self.age + int(time())

    @expire.setter
    def expire(self, value: int):
        self.expire = value
