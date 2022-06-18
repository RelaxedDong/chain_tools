#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2022/6/18 2:03 PM
# @Author  : donghao
import pytest

from main import app


def test_basic_test_client():
    request, response = app.test_client.get("/")
    assert response.json == {'hello': 'world', 'version': 1}
    assert response.status == 200
