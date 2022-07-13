#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2022/6/16 7:02 PM
# @Author  : donghao
import os

import aiohttp
from dotenv import load_dotenv

from config.log_config import error_logger
from utils.function_cache import async_func_cache

load_dotenv()
CACHE_COLLECTION_SLUGS = 60 * 60 * 24 * 7

OPENSEA_API_KEY = os.environ.get("OPENSEA_API_KEY")

HEADERS = {"X-API-Key": OPENSEA_API_KEY}


@async_func_cache(ttl=CACHE_COLLECTION_SLUGS)
async def get_opensea_collection_info(contract_address):
    try:
        print('从OPENSE获取数据')
        url = f"https://api.opensea.io/api/v1/asset_contract/{contract_address}"
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.get(url) as response:
                return await response.json()
    except Exception as e:
        error_logger.exception(e)
        return {}

