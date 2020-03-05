#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/11/28 下午4:41
import os, sys, re, json, traceback, time
from flask_restful import Resource
from flask import Flask, request, jsonify
from random import random
from tools.utils import simple_utils as utils

class TestExtract(Resource):
    def get(self):
        from tools.idps.idps_utils import extract
        a = extract("32", "/Users/jingjian/datagrand/gitlab/team/orientation/文档智能审阅系统介绍/idps2.0/test_pdf/1.pdf")
        return json.dumps(a)


if __name__ == "__main__":
    pass
