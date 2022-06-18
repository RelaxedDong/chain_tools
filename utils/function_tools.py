#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2022/6/16 7:07 PM
# @Author  : donghao
import asyncio
import functools

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


def run_sync(future, loop=None):
    loop = loop or asyncio.get_event_loop()
    return loop.run_until_complete(future)

