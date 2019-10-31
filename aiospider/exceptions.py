#!/usr/bin/env python3
# encoding: utf-8
# time    : 2019/10/18 1:55 下午


class NoTaskIdError(Exception):
    pass


class InvalidRequestMethod(Exception):
    pass


class InvalidFunc(Exception):
    pass


class InvalidParseMethod(Exception):
    pass


class RequestStatusError(Exception):
    pass
