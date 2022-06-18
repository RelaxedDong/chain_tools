#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2022/6/16 6:55 PM
# @Author  : donghao

from sanic import Sanic
from sanic.response import json

app = Sanic("test")


@app.route('/')
async def test(request):
    version = 1
    return json({'hello': 'world', 'version': version})

if __name__ == '__main__':
    app.run()
