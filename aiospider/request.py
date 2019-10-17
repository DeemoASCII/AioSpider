#!/usr/bin/env python3
# encoding: utf-8
# time    : 2019/10/10 3:46 下午
import inspect
import re
from _sha256 import sha256
from typing import Optional, Dict, Any

import ujson
from faker import Faker
from httpx import QueryParamTypes, HeaderTypes, CookieTypes, AuthTypes, CertTypes, VerifyTypes, TimeoutTypes
from httpx.models import ProxiesTypes, AsyncRequestData, URLTypes, RequestFiles

fake = Faker(locale='zh_CN')


class Request:
    def __init__(self, method: str, url: URLTypes, callback: str = None,
                 data: AsyncRequestData = None,
                 metadata: Optional[Dict] = None,
                 dont_filter: bool = False,
                 priority: int = 1,
                 params: QueryParamTypes = None,
                 headers: HeaderTypes = None,
                 cookies: CookieTypes = None,
                 stream: bool = None,
                 auth: AuthTypes = None,
                 allow_redirects: bool = True,
                 cert: CertTypes = None,
                 verify: VerifyTypes = None,
                 timeout: TimeoutTypes = 20,
                 trust_env: bool = None,
                 proxies: ProxiesTypes = None,
                 files=None,
                 json: Any = None,
                 ):
        self.method = method
        self.url = url
        self.params = params
        self.data = data
        self.headers = headers if headers else {'User-Agent': fake.chrome()}
        self.cookies = cookies
        self.callback = callback
        # self.dupe_str = self.to_dupe()
        self.metadata = metadata or {}
        self.dont_filter = dont_filter
        self.retries = 0
        self.proxies = proxies
        self.priority = priority
        self.stream = stream
        self.auth = auth
        self.allow_redirects = allow_redirects
        self.cert = cert
        self.verify = verify
        self.timeout = timeout
        self.trust_env = trust_env
        self.files = files
        self.json = json

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
        return f'AioSpiderRequest<{self.method.upper()} {self.url} callback={self.callback}>'

    def __str__(self):
        return f'AioSpiderRequest<{self.method.upper()} {self.url} callback={self.callback}>'

    def __eq__(self, other):
        if isinstance(other, Request):
            return self.priority == other.priority
        else:
            raise TypeError(f'"==" not supported between instances of "Request" and "{type(other)}"')

    def __lt__(self, other):
        if isinstance(other, Request):
            return self.priority < other.priority
        else:
            raise TypeError(f'"<" not supported between instances of "Request" and "{type(other)}"')

    def __gt__(self, other):
        if isinstance(other, Request):
            return self.priority > other.priority
        else:
            raise TypeError(f'">" not supported between instances of "Request" and "{type(other)}"')

    @staticmethod
    def func_name(p):
        for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
            m = re.search(r'func_name\((.*)\)', line)
            if m:
                return m.group(1)
