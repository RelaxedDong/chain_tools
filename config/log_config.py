#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2022/4/2 12:45 PM
# @Author  : donghao
import logging
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_PATH = os.path.join(BASE_DIR, "logs")
if not os.path.isdir(LOGS_PATH):
    os.mkdir(LOGS_PATH)


def get_logger(logger_name, log_level=logging.INFO):
    path = os.path.join(LOGS_PATH, f"{logger_name}.log")
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    if not logger.handlers:
        # 创建两个handler
        fh = logging.FileHandler(path, encoding="utf-8")
        ch = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s,%(msecs)d %(levelname)-2s [%(filename)s:%(lineno)d] %(message)s",
            datefmt="%Y/%m/%d %X"
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)
    return logger


info_logger = get_logger('info_logger')
error_logger = get_logger('error_logger')
mysql_insert_logger = get_logger('mysql_insert_logger')


if __name__ == '__main__':
    info_logger.info('testtest 1')
    try:
        a = 1 / 0
    except Exception as e:
        error_logger.exception(e)
