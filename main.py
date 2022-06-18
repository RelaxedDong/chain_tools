#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2022/6/16 6:55 PM
# @Author  : donghao
import socket

from sanic import Sanic
from sanic.response import json

version = 1
container_id = socket.gethostname()

app = Sanic("test")


@app.route('/')
async def test(request):
    return json({'hello': 'world', 'version': version, 'container_id': container_id})

if __name__ == '__main__':
    app.run()
