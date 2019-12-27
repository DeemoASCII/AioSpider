#!/usr/bin/env python3
# encoding: utf-8
# time    : 2019/10/25 5:18 下午


from setuptools import setup, find_packages
import sys

setup(
    name="AioSpider",
    version="0.2.21",
    author="yueyue",
    author_email="xxb1021054331@gmail.com",
    description="a crawl framework based on asyncio and aiohttp",
    long_description=open("README.rst").read(),
    packages=find_packages(exclude='spiders'),
    zip_safe=True,
    install_requires=[
        'ujson>=1.35',
        'cchardet>=2.1.4',
        'typing>=3.7.4',
        'redis>=3.3.10',
        'pydantic>=0.29',
        'Faker>=2.0.2',
        'uvloop>=0.13.0',
        'setuptools>=41.0.1',
        'aiohttp>=3.5.4',
        'pyquery>=1.4.0',
    ]
)
