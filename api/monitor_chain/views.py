#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2022/7/11 4:33 PM
# @Author  : donghao
import os.path

from sanic import response, json

from api.monitor_chain.view_manager import get_new_east_mint_records
from config import settings
from sanic import Blueprint


monitor_blue = Blueprint('monitor', url_prefix='/monitor')  # 创建一个蓝图from .views import *


@monitor_blue.route('/index')
async def mint_list(request):
    index_path = os.path.join(settings.PROJECT_DIR, "templates", "index.html")
    return await response.file(index_path)


@monitor_blue.route('/new_east_mints')
async def mint_list(request):
    records = await get_new_east_mint_records(1657527703556)
    return json({
        "records": records
    })
