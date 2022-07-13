#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2022/6/16 7:07 PM
# @Author  : donghao
import asyncio
import functools
from time import time

from config.log_config import error_logger


def run_sync(future, loop=None):
    loop = loop or asyncio.get_event_loop()
    return loop.run_until_complete(future)


def fail_safe(_func=None, error_return=None):
    def decorator(func):
        @functools.wraps(func)
        async def _wrapped_func(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_logger.exception(e)
                return error_return

        return _wrapped_func

    if _func:
        return decorator(_func)
    return decorator


def get_cur_time_ms():
    """
    return current timestamp in milliseconds
    """
    return int(time() * 1000)


def get_cur_time_sec():
    """
    return current timestamp in seconds
    """
    return int(time())


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        try:
            key = (cls, str((args, kwargs)))
            return cls._instances[key]
        except KeyError:
            cls._instances[key] = super(Singleton, cls).__call__(*args, **kwargs)
            return cls._instances[key]