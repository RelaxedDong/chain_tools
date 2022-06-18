#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2022/5/24 4:25 PM
# @Author  : donghao
import asyncio
import functools
import json

from utils.redis_db.redis_clients import RedisUtil


def get_cache_key(fn, *args, **kwargs) -> str:
    return u"{func_module}#{func_name}:|{call_args}".format(
        func_module=fn.__module__,
        func_name=fn.__name__,
        call_args=str((args, kwargs)),
    )


def async_func_cache(ttl: int = 60):
    def decorator(fn):
        @functools.wraps(fn)
        async def memorize(*args, **kwargs):
            key = get_cache_key(fn, args, kwargs)
            cache_result = await RedisUtil.get(key)
            if cache_result:
                return json.loads(cache_result)
            result = await fn(*args, **kwargs)
            await RedisUtil.set(key, json.dumps(result), expire=ttl)
            return result
        return memorize
    return decorator


async def clear_func_cache(func, *args, **kwargs):
    key = get_cache_key(func, args, kwargs)
    await RedisUtil.delete(key)
    print(f"clear cache:{key}")


@async_func_cache(60)
async def my_test(*args, **kwargs):
    print('from cache')
    return {"args": str(args), "kwargs": str(kwargs)}


async def main():
    resp = await my_test("1", "2")
    print(resp)
    resp = await my_test("1", "2")
    print(resp)
    await clear_func_cache(my_test, "1", "2")
    print('***')
    resp = await my_test("1", "2")
    print(resp)
    resp = await my_test("1", "2")
    print(resp)
    resp = await my_test("1", "3")
    print(resp)
    resp = await my_test("1", name="3")
    print(resp)


if __name__ == '__main__':
    asyncio.run(main())
