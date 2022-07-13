#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2022/7/11 4:49 PM
# @Author  : donghao
from bson import ObjectId

from api.db_manager import mint_record_db, project_info_db


async def get_new_east_mint_records(create_at):
    records = await mint_record_db.find_self({"create_at": {"$gte": create_at}}, limit=1000, sort=[('create_at', -1)])
    project_ids = [ObjectId(record["project_id"]) for record in records]
    project_records = await project_info_db.find_self({"_id": {"$in": project_ids}})
    project_id_to_info = {str(project["_id"]): project for project in project_records}
    for record in records:
        project_info = project_id_to_info.get(record['project_id']) or {}
        project_info['_id'] = str(project_info['_id'])
        record.pop("_id")
        record['project_info'] = project_info
    return records
