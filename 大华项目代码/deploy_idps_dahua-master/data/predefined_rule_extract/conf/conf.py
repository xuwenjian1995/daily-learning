#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-03-27 12:04
# @Author  : zhangyicheng@datagrand.com

# redis conf
REDIS_HOST = 'redis'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PWD = ''

# database conf
MYSQL_HOST = 'mysql'
# MYSQL_HOST = '127.0.0.1'
MYSQL_DB_NAME = 'contract'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'
MYSQL_PORT = 3306
# MYSQL_PORT = 16000

# predefined rule evaluate queue name
PREDEFINED_RULE_EVALUATE_QUEUE = 'predefined_rule:evaluate:queue'

# Enable predefined rule evaluate sync route, False by default
ENABLE_SYNC_EVALUATE = False
