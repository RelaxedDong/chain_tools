#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2022/6/18 2:03 PM
# @Author  : donghao
from main import app


def test_basic_test_client():
    request, response = app.test_client.get("/monitor/new_east_mints")
    assert 'records' in response.json
    assert response.status == 200
