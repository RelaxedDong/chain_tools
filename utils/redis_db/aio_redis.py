# -*- coding: utf-8 -*-

'''
Created on Nov 27, 2019

@author: gjwang
'''
import logging
import pickle

import aioredis

from utils.function_tools import run_sync


def list_or_args(keys, args):
    # returns a single new list combining keys and args
    try:
        iter(keys)
        # a string or bytes instance can be iterated, but indicates
        # keys wasn't passed as a list
        if isinstance(keys, (str, bytes)):
            keys = [keys]
        else:
            keys = list(keys)
    except TypeError:
        keys = [keys]
    if args:
        keys.extend(args)
    return keys


class _RedisManager(object):
    '''
    Redis connection manager
    '''
    DEFAULT_EXPIRE_TM_SEC = 5 * 60 + 10
    DEFAULT_POOL_MAXSIZE = 5

    def __init__(self, redis_config):
        self.redis = run_sync(self._create_pool(redis_config))

    async def _create_pool(self, redis_config):
        address = f"redis://{redis_config['server']}:{redis_config['port']}"
        print(f"_RedisManager _create_pool address={address} db={redis_config['db']}")
        password = redis_config['password'] if redis_config['password'] else None
        return await aioredis.from_url(address, password=password, db=redis_config['db'], encoding='utf-8')

    async def close(self):
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()
            self.redis = None

    def get_redis(self):
        return self.redis

    # @async_time_consumer
    async def set(self, key, value, expire=DEFAULT_EXPIRE_TM_SEC, pexpire=None):
        try:
            result = await self.redis.set(key, value, ex=expire, px=pexpire)
            if result:
                logging.debug('set success, key=%s, value=%s', key, value)
            else:
                logging.error('set failed, key=%s, value=%s', key, value)
            return result
        except Exception as ex:
            logging.error('_RedisManager set exception=%s, key=%s, value=%s', ex, key, value)

    # @async_time_consumer
    async def get(self, key):
        try:
            return await self.redis.get(key)
        except Exception as ex:
            logging.error('_RedisManager get exception=%s', ex)
        return None

    async def lpush(self, name, *values):
        return await self.redis.lpush(name, *values)

    async def rpush(self, name, *values):
        return await self.redis.rpush(name, *values)

    async def lrange(self, name, start, end):
        return await self.redis.lrange(name, start, end)

    async def incr(self, key):
        return await self.redis.incr(key)

    async def delete(self, key):
        return await self.redis.delete(key)

    async def exists(self, key):
        return await self.redis.exists(key)

    async def hset(self, key, field, value, expire=None):
        return await self.redis.hset(key, field, value)

    async def hget(self, key, field):
        return await self.redis.hget(key, field, encoding='utf-8')

    async def hgetall(self, key):
        return await self.redis.hgetall(key, encoding='utf-8')

    async def hmset(self, name, mapping):
        return await self.redis.hmset(name, mapping)

    async def hmget(self, name, keys, *args):
        args = list_or_args(keys, args)
        return await self.redis.hmget(name, *args)

    async def hmset_with_expire(self, name, mapping, time=None):
        # expire_after = time
        # Complicate mapping object cache with expire time
        r1 = await self.redis.hmset(name, mapping)
        r2 = await self.redis.expire(name, time) if time else None
        return (r1, r2)

    async def hdel(self, name, *keys):
        return await self.redis.hdel(name, *keys)

    async def hexists(self, name, key):
        return await self.redis.hexists(name, key)

    async def expire(self, name, time):
        """
        Set an expire flag on key ``name`` for ``time`` seconds. ``time``
        can be represented by an integer or a Python timedelta object.
        """
        return await self.redis.expire(name, time)

    async def expire_at(self, name, when):
        return await self.redis.expireat(name, when)

    async def zcount(self, name, start_score, end_score):
        try:
            return await self.redis.zcount(name, start_score, end_score)
        except Exception as ex:
            logging.error(f'_Redis zcount ex={ex}, key={name}, '
                          f'start_score={start_score}, end_score={end_score}')
            raise ex

    async def zremrangebyscore(self, name, start_score, end_score):
        try:
            return await self.redis.zremrangebyscore(name, start_score, end_score)
        except Exception as ex:
            logging.error(f'_Redis zremrangebyscore exception={ex}, key={name}, '
                          f'start_score={start_score}, end_score={end_score}')

    async def zadd(self, name, score, value):
        try:
            result = await self.redis.zadd(name, score, value)
            if result:
                logging.debug(f'zadd success, key={name}, score={score}, value={value}')
            else:
                logging.error(f'zadd failed,  key={name}, score={score}, value={value}')
            return result
        except Exception as ex:
            logging.error(f'_Redis zadd exception={ex}, key={name}, score={score}, value={value}')

    async def keys(self, pattern):
        # 小心使用通配符， 尤其是用户端的输入 Warning: 尽量不要使用！仅限测试 https://redis.io/commands/keys Warning: consider KEYS as a command
        # that should only be used in production environments with extreme care. It may ruin performance when it is
        # executed against large databases. This command is intended for debugging and special operations,
        # such as changing your keyspace layout. Don't use KEYS in your regular application code. If you're looking
        # for a way to find keys in a subset of your keyspace, consider using SCAN or sets.
        return await self.redis.keys(pattern)

    async def set_object(self, key, obj, expire=DEFAULT_EXPIRE_TM_SEC):
        # save complicate object type to redis
        # Warning The pickle module is not intended to be secure against erroneous or maliciously constructed data.
        # Never unpickle data received from an untrusted or unauthenticated source.
        # Only use it internal
        if isinstance(obj, (int, float, str, list, dict)):
            logging.warning("simple type no need to use pick, just use native type or json.dumps")
        value = pickle.dumps(obj)
        return await self.redis.set(key, value, expire=expire)

    async def get_object(self, key, object_type=None, encoding=None):
        result = await self.redis.get(key, encoding=encoding)
        if object_type:
            # try to contruct with object_type
            return object_type(result)
        else:
            return pickle.loads(result)
