#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/11/26 下午3:58
import os, sys, re, json, traceback, time, logging


logging.basicConfig(level=logging.INFO,
                    datefmt='%y-%m-%d %H:%M:%S %z',
                    filename='log/root.log',
                    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    filemode="a")  #设置日志级别为info,此处format为引用日志格式,此处通过定义日志格式来

dhlog = logging.getLogger("dahua")


if __name__ == "__main__":
    pass
