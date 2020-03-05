# coding: utf-8
from __future__ import unicode_literals

# fields_analysis服务的名称
FIELDS_ANALYSIS_NAME = 'fields_analysis'

# 模型评估时，消息队列的名称
MODEL_EVALUATE_QUEUE = 'model:evaluate:queue'

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

services = {
    'fuzzy_extract': True,
    'diff_extract': True,
    'table_extract': True,
}

# 条款group配置
groups = []

# 使用group的子服务
enable_group_services = [
    'dl_extract',
]
