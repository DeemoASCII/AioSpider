#!/usr/bin/env python3
# encoding: utf-8
# time    : 2019/10/10 3:46 下午
from _sha256 import sha256
from typing import Optional, Dict, Any, Mapping, Union

import ujson
from aiohttp import BasicAuth, ClientTimeout
from aiohttp.helpers import sentinel
from aiohttp.typedefs import StrOrURL, LooseCookies, LooseHeaders
from faker import Faker

from aiospider.exceptions import InvalidRequestMethod
from aiospider.models import BaseTask

fake = Faker(locale='zh_CN')

METHOD = {'GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH'}


class Request(BaseTask):
    def __init__(self, method: str, url: StrOrURL, callback: str = None,
                 params: Optional[Mapping[str, str]] = None,
                 data: Any = None,
                 json: Any = None,
                 metadata: Optional[Dict] = None,
                 dont_filter: bool = False,
                 priority: int = 10,
                 cookies: Optional[LooseCookies] = None,
                 headers: LooseHeaders = None,
                 auth: Optional[BasicAuth] = None,
                 allow_redirects: bool = True,
                 max_redirects: int = 10,
                 proxy: Optional[StrOrURL] = None,
                 proxy_auth: Optional[BasicAuth] = None,
                 timeout: Union[ClientTimeout, object] = sentinel,
                 verify_ssl: Optional[bool] = None,
                 etag:int=1
                 ):
        super().__init__(priority, dont_filter)
        self.method = method.upper()
        if self.method not in METHOD:
            raise InvalidRequestMethod(f"{self.method} method is not supported")
        self.url = url
        self.params = params
        self.data = data
        self.headers = headers or {'User-Agent': fake.chrome()}
        self.cookies = cookies
        self.callback = callback
        self.metadata = metadata or {}
        self.proxy = proxy
        self.proxy_auth = proxy_auth
        self.auth = auth
        self.allow_redirects = allow_redirects
        self.timeout = timeout
        self.json = json
        self.max_redirects = max_redirects
        self.verify_ssl = verify_ssl
        self.etag = etag

    @property
    def taskId(self) -> str:
        dupe_str = sha256()
        if not self.params and not (self.data or self.json):
            dupe_str.update((self.method + self.url).encode('utf-8'))
        elif self.params and (self.data or self.json):
            dupe_str.update(
                (self.method + self.url + ujson.dumps(self.params) + ujson.dumps(self.data or self.json)).encode(
                    'utf-8'))
        elif self.params and not (self.data or self.json):
            dupe_str.update(
                (self.method + self.url + ujson.dumps(self.params)).encode('utf-8'))
        elif not self.params and (self.data or self.json):
            dupe_str.update(
                (self.method + self.url + ujson.dumps(self.data or self.json)).encode('utf-8'))
        return dupe_str.hexdigest()

    def __repr__(self):
        return f'<AioSpiderRequest url[{self.method}]: {self.url} callback={self.callback}>'

    def __str__(self):
        return f'<AioSpiderRequest url[{self.method}]: {self.url} callback={self.callback}>'
