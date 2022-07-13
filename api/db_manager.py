#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2022/7/11 1:36 PM
# @Author  : donghao
from config.mongo_db.aio_pool import AIOPool
from config.settings import MONGO_POOL_SETTING


class ChainToolsDbBase(AIOPool):
    def __init__(self):
        self.project_info = "project_info"
        super(ChainToolsDbBase, self).__init__(MONGO_POOL_SETTING)
        self.current_collection = None


class ProjectInfo(ChainToolsDbBase):
    def __init__(self):
        super(ProjectInfo, self).__init__()
        self.project_info = "project_info"
        self.current_collection = self.project_info

    async def create_project(self, project_info):
        # 创建项目信息
        print('创建项目...')
        exist_info = await self.find_self_one({"contract_address": project_info['contract_address']})
        if exist_info:
            return str(exist_info['_id'])
        db_id = await self.insert_self(project_info)
        return str(db_id)


class MintRecord(ChainToolsDbBase):
    def __init__(self):
        super(MintRecord, self).__init__()
        self.mint_record = "mint_record"
        self.current_collection = self.mint_record


project_info_db = ProjectInfo()
mint_record_db = MintRecord()
