#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/4/19 下午2:43
import os, sys, re, json, traceback, time
from uuid import uuid4 as uuid
import requests
from conf import conf
from dahua_log import dhlog
from functools import wraps
# from pydocx import PyDocX
from PIL import Image


def time_func(func):
    @wraps(func)
    def _wrap(*args, **kwargs):
        st = time.time()
        rst = func(*args, **kwargs)
        et = time.time()
        output_str = "func: {} costs: {}s".format(func.__name__, et-st)
        dhlog.info(output_str)
        return rst
    return _wrap


def rotate_image(image_path, save_path, rotation):
    try:
        img = Image.open(image_path)
        img_ro = img.rotate(rotation, expand=True)
        img_ro.save(save_path)
        return True
    except Exception as e:
        dhlog.error(e)
        return False


def crop_image(image_path, save_path, rect):
    '''

    :param image_path: 输入图片路径
    :param save_path:  保存截图路径
    :param rect: 截图区域比例
    :return: 是否截图成功
    '''
    try:
        img = Image.open(image_path)
        width, height = img.size
        left = rect["left"] * width
        upper = rect["up"] * height
        right = rect["right"] * width
        lower = rect["down"] * height
        cropped = img.crop((left, upper, right, lower))
        cropped.save(save_path)
        return True
    except Exception as e:
        dhlog.error(e)
        return False


def get_file_names(file_dir, fileType):
    '''
    得到某个目录下所有的文件名
    :param file_dir:文件夹路径
    :param fileType:后缀名
    :return:
    '''
    L = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if os.path.splitext(file)[1] == "." + fileType:
                # L.append(os.path.join(root, file))
                L.append(os.path.join(file))
    return L

def get_folder_names(file_dir):
    '''
    得到某个目录下所有的文件夹名
    :param file_dir:文件夹路径
    :return:
    '''
    L = []
    for root, dirs, files in os.walk(file_dir):
        for file in dirs:
            L.append(os.path.join(file))
    return L

def get_file_names_without_type(file_dir):
    '''
    得到某个目录下所有的文件名
    :param file_dir:文件夹路径
    :return:
    '''
    L = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            L.append(os.path.join(file))
    return L

def get_uuid():
    '''
    获取一个uuid，去除了'-'
    :return:
    '''
    return str(uuid()).replace("-", "")


def file_extension(path):
    '''
    获取一个文件路径的扩展名
    :param path:
    :return:
    '''
    return os.path.splitext(path)[1]


def doc2docx(file_path):
    '''
    将doc使用unoconv服务转换成docx
    :param file_path:
    :return:
    '''
    # 如果是，通过unoconv进行转换
    response = requests.post("http://" + conf.unoconv_host + ":3000/unoconv/docx",
                             files={'file': open(file_path, 'rb')})
    return response.content

# def docx2html(file_path):
#     '''
#     将一个docx转换成html
#     :param file_path:
#     :return:
#     '''
#     return PyDocX.to_html(file_path)

def get_file_name_from_path(path):
    return os.path.basename(path)


class TreeNode(object):
    def __init__(self, name):
        self.parent = None
        self.children = []
        self.name = name
        self.level = 0
        self.path = ""
        self.files = []




if __name__ == "__main__":
    # for a in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', '', '1', '1', '1',]
    print(get_uuid())
    # a = get_file_names("/Users/jingjian/datagrand/2019_2/guojianengyuanshenhua/20190506/download", "")
    # print(len(a))
    # for each in a:
    #     os.system("mv /Users/jingjian/datagrand/2019_2/guojianengyuanshenhua/2019-5-6/00/{0} /Users/jingjian/datagrand/2019_2/guojianengyuanshenhua/2019-5-6/00/{1}.txt".format(each,each))
