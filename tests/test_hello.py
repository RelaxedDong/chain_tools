#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2022/6/18 2:03 PM
# @Author  : donghao

from bin.main import app


def test_basic_test_client():
    request, response = app.test_client.get("/")
    response_json = response.json
    assert response_json['version'] == 2
    assert response.status == 200
