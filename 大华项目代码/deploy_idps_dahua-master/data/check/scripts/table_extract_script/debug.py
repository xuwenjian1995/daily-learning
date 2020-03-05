# coding=utf-8
# email:  lihanqing@datagrand.com
# create: 2018/7/18-下午4:30
from __future__ import unicode_literals

from table_extract.app.driver import logger_online


def run(context):
    logger_online.info('debug script')
    result = context.get('result', None)
    if result is None:
        context.update({'result': {}})
