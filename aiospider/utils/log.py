#!/usr/bin/env python3
# encoding: utf-8
# time    : 2019/10/10 4:38 下午


import logging


def get_logger(name="mesoor"):
    logging_format = "[%(asctime)s] %(levelname)-5s %(name)-8s"
    logging_format += "%(message)s"
    logging.basicConfig(
        format=logging_format, level=logging.DEBUG, datefmt="%Y:%m:%d %H:%M:%S"
    )
    logging.getLogger("asyncio").setLevel(logging.INFO)
    logging.getLogger("websockets").setLevel(logging.INFO)
    return logging.getLogger(name)
