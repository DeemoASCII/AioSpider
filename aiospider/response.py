#!/usr/bin/env python3
# encoding: utf-8
# time    : 2019/10/10 3:46 下午
import re
from _sha256 import sha256
from http.cookies import SimpleCookie
from typing import Dict, Optional

import ujson
from cchardet import detect
from pyquery import PyQuery

from aiospider.models import BaseTask
from aiospider.request import Request


class Response(BaseTask):
    """
    Return a friendly response
    """

    def __init__(
            self,
            url: str,
            method: str,
            *,
            metadata: Optional[Dict] = None,
            cookies,
            history,
            headers,
            status: int = -1,
            callback: Optional[str] = None,
            request: Request,
            content: bytes,
            age: int
    ):
        super().__init__(request.priority - 5, request.dont_filter, age)
        self._callback = callback
        self._url = url
        self._method = method
        self._metadata = metadata or {}
        self._cookies = cookies
        self._history = history
        self._headers = headers
        self._content_type = self._headers.get('Content-Type')
        self._status = status
        self._ok = self._status == 0 or 200 <= self._status <= 299
        self._request = request
        self._content = content
        self._encoding = re.search(r'(?<=charset=).*',
                                   self._content_type).group().lower() if 'charset' in self._content_type else detect(
            content).get('encoding')

    @property
    def content(self):
        return self._content

    @property
    def callback(self) -> str:
        return self._callback

    @property
    def ok(self) -> bool:
        return self._ok

    @ok.setter
    def ok(self, value: bool):
        self._ok = value

    @property
    def encoding(self):
        return self._encoding

    @property
    def url(self):
        return self._url

    @property
    def method(self):
        return self._method

    @property
    def metadata(self):
        return self._metadata

    @property
    def cookies(self) -> dict:
        if isinstance(self._cookies, SimpleCookie):
            cur_cookies = {}
            for key, value in self._cookies.items():
                cur_cookies[key] = value.value
            return cur_cookies
        else:
            return self._cookies

    @property
    def history(self):
        return self._history

    @property
    def headers(self):
        return self._headers

    @property
    def status(self):
        return self._status

    @property
    def request(self):
        return self._request

    @property
    def json(self):
        """Read and decodes JSON response."""

        return ujson.loads(self.text) if 'application/json' in self._content_type else None

    @property
    def text(self) -> str:
        """Read response payload and decode."""
        return self._content.decode(self._encoding)

    @text.setter
    def text(self, value):
        self.text = value

    def __repr__(self):
        return f"<AioSpiderResponse url[{self._method}]: {self._url} status:{self._status} callback: {self._callback}>"

    def __str__(self):
        return f"<AioSpiderResponse url[{self._method}]: {self._url} status:{self._status} callback: {self._callback}>"

    @property
    def doc(self) -> PyQuery:
        return PyQuery(self.text) if 'application/json' not in self._content_type else None

    @doc.setter
    def doc(self, value):
        self.doc = value

    @property
    def taskId(self):
        dupe_str = sha256()
        dupe_str.update(('Response from:' + self._request.taskId).encode())
        return dupe_str.hexdigest()
