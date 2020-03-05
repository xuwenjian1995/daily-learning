#!/usr/bin/env python
# coding=utf-8
# author: jingjian@datagrand.com
# datetime:2019-11-28 10:39
import os, sys, re, json, traceback, time
import _locale

_locale._getdefaultlocale = (lambda *args: ['en_US', 'utf8'])

import requests
from conf.conf import idps_host,idps_username,idps_password

host = idps_host  # 'http://idps2-data-dev.test.datagrand.cn/api/'
# user_info = dict(token='', username='admin', password='datadev')
user_info = dict(token='', username=idps_username, password=idps_password)
# from dahua_log import dhlog

def login():
    """登陆
    """
    login_response = requests.post(
    host + 'login',
    data={
        'username': user_info['username'],
        'password': user_info['password']
    })
    if login_response.status_code >= 400:
        # dhlog.info('µÇÂ¼Ê§°Ü£¬ÇëÁªÏµ´ï¹ÛÏî?¸ºÔð?')
        # exit()
        raise Exception("登陆失败")
    user_info['token'] = login_response.json().get('access_token')


def headers_generator():
    """生成身份认证 headers
    """
    return {'Authorization': 'Bearer ' + user_info['token']}


def request_with_jwt(url, method, **kw):
    """使用jwt认证登陆简单封装requests
    Arguments:
    url {[str]} -- [请求地址]
    method {[str]} -- [请求方法]
    Returns:
    [response] -- [requests的相应]
    """
    # 检测是否有token, 没有则登陆获取
    if not user_info['token']:
        login()
    if method == 'GET':
        response = requests.get(url, headers=headers_generator(), **kw)
    else:
        response = {
            'PUT': requests.put,
            'POST': requests.post,
            'DELETE': requests.delete,
        }[method](
            url, headers=headers_generator(), **kw)
    # 检测token是否合法，不合法则登陆获取token，再发送相同请求
    if response.status_code == 401:
        login()
        return request_with_jwt(url=url, method=method, **kw)
    else:
        return response




# # 获取前1000个文档类型
# tag_types_response = request_with_jwt(
# url=host + 'tag_types', data={
#     'start': 0,
#     'number': 1000
#     }, method='GET')
# tag_types = tag_types_response.json()
# # 第一个文档类型的ID
# first_type_id = tag_types.get('items')[0].get('id')
# # 第一个文档类型的名称
# first_type_name = tag_types.get('items')[0].get('name')
# print(first_type_name)
# # 获取第一个文档类型下所有的文档条款
# tags_response = request_with_jwt(
#     url=host + 'tags/{}'.format(first_type_id),
#     data={
#         'start': 0,
#         'number': 1000
#     },
#     method='GET')
# tags = tags_response.json()
# # print(json.dumps(tags,ensure_ascii=False,indent=2))
#
#
#
#
#
# # 使用第一个文档类型的模板抽取本地文件
# extract_response = request_with_jwt(
#         url=host + 'extracting/instant',
#         method='POST',
#         data={'docType': first_type_id},
#         files={'file': open('C:\\Users\\¾°½¡\\Desktop\\1.pdf', 'rb')},
#     )
# extract_result = extract_response.json()
# print(json.dumps(extract_result,ensure_ascii=False,indent=2))


# extract_response = request_with_jwt(
#         url=host + 'review',
#         method='POST',
#         data={'async_task':'false','data':json.dumps({'docType': first_type_id,'check_point_id_list':[1]})},
#
#         files={'file': open('C:\\Users\\¾°½¡\\Desktop\\1.pdf', 'rb')},
#     )
# extract_result = extract_response.json()
# print(json.dumps(extract_result,ensure_ascii=False,indent=2))