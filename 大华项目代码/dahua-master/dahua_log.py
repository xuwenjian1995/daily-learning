#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/11/26 下午3:58
import os, sys, re, json, traceback, time, logging

filename = os.path.join(os.path.dirname(__file__), 'log/root.log')
print (filename)

dhlog = logging.getLogger()
dhlog.setLevel(logging.INFO)

fileHandler = logging.FileHandler(
    filename=filename,
    mode='a',
    encoding="utf-8"
)

formatter = logging.Formatter(
    fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
    datefmt='%y-%m-%d %H:%M:%S %z'
)
fileHandler.setFormatter(formatter)

dhlog.addHandler(fileHandler)


if __name__ == "__main__":
    pass
