#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2022/6/16 7:02 PM
# @Author  : donghao
import os

import aiohttp
from dotenv import load_dotenv
load_dotenv()


from utils.function_tools import fail_safe
OPENSEA_API_KEY = os.environ.get("OPENSEA_API_KEY")

HEADERS = {"X-API-Key": OPENSEA_API_KEY}


@fail_safe(error_return={})
async def get_opensea_collection_info(contract_address):
    url = f"https://api.opensea.io/api/v1/asset_contract/{contract_address}"
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(url) as response:
            return await response.json()
