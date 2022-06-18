#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2022/4/6 11:22 AM
# @Author  : donghao
import aioredis

from utils.function_tools import run_sync

REDIS_HOST = 'auth.redis.anbbit.prod'
REDIS_PORT = 6379
REDIS_PASSWD = ''
REDIS_DEFAULT_POOL_MAXSIZE = 5
KAFKA_SERVERS = ['kafka.anbbit.prod:9092', ]


DEFAULT_DB = 0

DEFUAL_REDIS_CONFIG = {
    "server": REDIS_HOST,
    "port": REDIS_PORT,
    "db": DEFAULT_DB,
    "password": REDIS_PASSWD,
    "maxsize": REDIS_DEFAULT_POOL_MAXSIZE,
}


class RedisUtilManager(object):
    DEFAULT_EXPIRE_TM_SEC = 5 * 60 + 10
    DEFAULT_POOL_MAXSIZE = 5

    def __init__(self):
        self.redis = run_sync(self._create_pool(DEFUAL_REDIS_CONFIG))

    async def _create_pool(self, redis_config):
        address = f"redis://{redis_config['server']}:{redis_config['port']}"
        password = redis_config['password'] if redis_config['password'] else None
        return await aioredis.from_url(address, password=password, db=redis_config['db'], encoding='utf-8')

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance


RedisUtil = RedisUtilManager.instance()
