#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2022/5/24 4:25 PM
# @Author  : donghao
import asyncio
import functools
import json

from utils.redis_db.redis_clients import RedisUtil


def get_cache_key(fn, build_without_params, *args, **kwargs) -> str:
    if build_without_params:
        key = u"{func_module}#{func_name}".format(func_module=fn.__module__, func_name=fn.__name__)
    else:
        key = u"{func_module}#{func_name}:|{call_args}".format(
            func_module=fn.__module__,
            func_name=fn.__name__,
            call_args=str((args, kwargs)),
        )
    return key


def async_func_cache(ttl: int = 60, build_without_params=False):
    def decorator(fn):
        @functools.wraps(fn)
        async def memorize(*args, **kwargs):
            key = get_cache_key(fn, build_without_params, args, kwargs)
            cache_result = await RedisUtil.get(key)
            if cache_result:
                return json.loads(cache_result)
            result = await fn(*args, **kwargs)
            await RedisUtil.set(key, json.dumps(result), ex=ttl)
            return result

        return memorize

    return decorator


def mutex_func_cache_dec(ttl=10, lock_default_return=None):
    def decorator(fn):
        @functools.wraps(fn)
        async def memorize(*args, **kwargs):
            key = get_cache_key(fn, args, kwargs)
            lock_key = key + "lock"
            is_has = await RedisUtil.set(lock_key, 2, nx=True, ex=ttl)
            try:
                if not is_has:
                    return lock_default_return
                result = await fn(*args, **kwargs)
                return result
            finally:
                await RedisUtil.delete(lock_key)

        return memorize

    return decorator


async def clear_func_cache(func, *args, **kwargs):
    key = get_cache_key(func, args, kwargs)
    await RedisUtil.delete(key)
    print(f"clear cache:{key}")


# @async_func_cache(60)
@mutex_func_cache_dec(lock_default_return="666")
async def my_test(*args, **kwargs):
    # print('from cache')
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


async def main_mutex_func_cache_dec():
    import asyncio
    tasks = []
    loop = asyncio.get_event_loop()
    tasks.extend(
        [
            loop.create_task(my_test("1", "2")),
            loop.create_task(my_test("1", "2")),
            loop.create_task(my_test("1", "2")),
        ]
    )
    result = await asyncio.gather(*tasks)
    print(result)


if __name__ == '__main__':
    asyncio.run(main_mutex_func_cache_dec())
