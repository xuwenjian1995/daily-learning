#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-05-15 15:16
# @Author  : zhangyicheng@datagrand.com
from __future__ import unicode_literals

UPLOAD_DIR = './upload'

# redis conf
REDIS_HOST = 'redis'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PWD = ''

# database conf
MYSQL_HOST = 'mysql'
MYSQL_DB_NAME = 'contract'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'
MYSQL_PORT = 3306

is_english = False  # Is source language English

default_field_config_json = 'label_quality_check/conf/default_field_config.json'

# Label quality check queue name
LABEL_QUALITY_CHECK_QUEUE = 'label:quality_check:queue'

MODEL_EVALUATE_QUEUE = 'model:evaluate:queue'

MODEL_QUEUE = 'queue:a'

# Enable http server(sync server), False by default
ENABLE_HTTP_SERVER = False
