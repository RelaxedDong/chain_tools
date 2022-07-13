#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2022/6/17 7:11 PM
# @Author  : donghao
import os

from dotenv import load_dotenv
load_dotenv()
PROJECT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

OPENSEA_API_KEY = os.environ.get("OPENSEA_API_KEY")

MONGO_USER = os.environ.get("MONGODB_MONGO_USER")
MONGO_HOST = os.environ.get("MONGODB_DB_HOST")
MONGO_PORT = 27017
MONGO_PASSWORD = os.environ.get("MONGODB_PASSWORD")
MONGO_DB_NAME = os.environ.get("MONGODB_DB_NAME")
MONGO_REPLSET_NAME = "rs0"
MONGO_POOL_SETTING = {
    'db_setting': {
        "host": MONGO_HOST,
        "port": MONGO_PORT,
        "user": MONGO_USER,
        "passwd": MONGO_PASSWORD,
        "db": MONGO_DB_NAME,
        # "replset": MONGO_REPLSET_NAME
    },
    "pool_size": 5,
}
