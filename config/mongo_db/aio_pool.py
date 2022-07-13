import asyncio
from urllib.parse import quote_plus

import motor

from utils.function_tools import Singleton, get_cur_time_ms
import motor.motor_asyncio as async_motor


class AIOPool(metaclass=Singleton):
    def __init__(self, db_dict_setting, is_debug=False):
        db_setting = db_dict_setting['db_setting']
        pool_size = db_dict_setting['pool_size']
        self.is_debug = is_debug
        self.client = self.__create_pool(db_setting, pool_size)
        self.initialize()
        self.current_collection = None

    def initialize(self):
        '''
        # fixme 集成标准的mongo关于时间的处理
        https://www.mongodb.com/docs/manual/reference/operator/update/currentDate/
        '''
        pass

    def __create_pool(self, db_setting, pool_size):
        uri = f'mongodb://{quote_plus(db_setting["user"])}:{quote_plus(db_setting["passwd"])}' \
              f'@{db_setting["host"]}:{db_setting["port"]}/{db_setting["db"]}'
        self.db = db_setting["db"]
        pool = async_motor.AsyncIOMotorClient(uri, maxPoolSize=pool_size)
        return pool

    async def insert(self, collection_name: str, document: dict):
        collection = self.client[self.db][collection_name]
        async with await self.client.start_session() as s:
            document["create_at"] = document["update_at"] = get_cur_time_ms()
            result = await collection.insert_one(document, session=s)
        return result.inserted_id

    async def insert_many(self, collection: str, documents: [dict]):
        collection = self.client[self.db][collection]
        async with await self.client.start_session() as s:
            for document in documents:
                document["create_at"] = document["update_at"] = get_cur_time_ms()
            result = await collection.insert_many(documents, session=s)
        return result.inserted_ids

    async def update(self, collection_name: str, filters: dict, document: dict, upsert=True):
        collection = self.client[self.db][collection_name]
        async with await self.client.start_session() as s:
            current_time_ms = get_cur_time_ms()
            if "$set" in document:
                document["$set"]["update_at"] = current_time_ms
            else:
                document["$set"] = {"update_at": current_time_ms}

            if "$setOnInsert" in document:
                document["$setOnInsert"]["create_at"] = current_time_ms
            else:
                document["$setOnInsert"] = {"create_at": current_time_ms}
            result = await collection.update_one(filters, document, upsert, session=s)
        return result

    async def update_many(self, collection_name: str, filters: dict, document: dict, upsert=True):
        collection = self.client[self.db][collection_name]
        async with await self.client.start_session() as s:
            if "$set" in document:
                document["$set"]["update_at"] = get_cur_time_ms()
            result = await collection.update_many(filters, document, upsert, session=s)
        return result

    async def find(self, collection_name: str, filters,
                   projection: list = None,
                   limit: int = 0,
                   sort: list = None,
                   skip: int = None,
                   collation_conf=None):
        collection = self.client[self.db][collection_name]
        async with await self.client.start_session() as s:
            cursor = collection.find(filters, projection=projection, limit=limit, sort=sort, session=s)
            if skip is not None:
                cursor = collection.find(filters, projection=projection, limit=limit, sort=sort, session=s).skip(skip)
            if collation_conf:
                cursor = cursor.collation(collation_conf)
            result = await cursor.to_list(None)
        return result

    async def delete_one(self, collection_name: str, filters):
        collection = self.client[self.db][collection_name]
        async with await self.client.start_session() as s:
            result = await collection.delete_one(filters, session=s)
        return result

    async def delete_many(self, collection_name: str, filters):
        collection = self.client[self.db][collection_name]
        async with await self.client.start_session() as s:
            result = await collection.delete_many(filters, session=s)
        return result

    async def find_one(self, collection_name: str, filters,
                       projection: list = None,
                       sort: list = None,
                       collation_conf=None):
        result_list = await self.find(collection_name, filters, projection=projection, limit=1, sort=sort,
                                      collation_conf=collation_conf)
        if not result_list:
            return {}
        return result_list[0]

    async def get_count(self, collection_name, filters):
        collection = self.client[self.db][collection_name]
        return await collection.count_documents(filters)

    async def update_self(self, filters: dict, document: dict, upsert=True):
        return await self.update(self.current_collection, filters, document, upsert)

    async def find_self_one(self, filters, projection: list = None, sort: list = None, collation_conf=None):
        return await self.find_one(self.current_collection, filters, projection, sort, collation_conf)

    async def find_self(self, filters, projection: list = None, limit: int = 0, sort: list = None,
                        skip: int = None, collation_conf=None):
        return await self.find(self.current_collection, filters, projection, limit, sort, skip, collation_conf)

    async def insert_self(self, document: dict):
        return await self.insert(self.current_collection, document)
