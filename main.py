#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2022/6/16 6:55 PM
# @Author  : donghao
from sanic import Sanic
from config import settings
from api.monitor_chain.views import monitor_blue


def create_app():
    app = Sanic("chain_tool")
    app.blueprint(monitor_blue)
    app.config.update_config(settings)
    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True)
