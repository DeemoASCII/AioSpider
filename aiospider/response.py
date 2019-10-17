#!/usr/bin/env python3
# encoding: utf-8
# time    : 2019/10/10 3:46 下午

from typing import Dict, Optional

from cchardet import detect
from httpx import AsyncResponse
from pyquery import PyQuery

from aiospider.request import Request


class Response:

    def __init__(self, resp: AsyncResponse, task: Request, metadata: Optional[Dict] = None):
        if metadata is None:
            metadata = {}
        self.data = resp
        self.metadata = metadata
        self.request = task
        self.status_code = resp.status_code
        self.ok = True if resp.status_code == 200 else False

    @property
    def raw(self, encoding='utf-8') -> str:
        self.data.encoding = encoding
        return self.data.text

    @property
    def json(self) -> Dict:
        return self.data.json()

    @property
    def content(self):
        return self.data.content

    @property
    def doc(self) -> PyQuery:
        self.data.encoding = detect(self.data.content).get('encoding', 'utf-8')
        doc = PyQuery(self.data.text)
        # parsed_uri = urlparse(str(self.data.url))
        # doc.make_links_absolute(base_url=f'{parsed_uri.scheme}://{parsed_uri.netloc}')
        return doc
