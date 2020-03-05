#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/4/25 下午6:36

import os
import zipfile


def get_zip_file(input_path, result):
    """
    对目录进行深度优先遍历
    :param input_path:
    :param result:
    :return:
    """
    files = os.listdir(input_path)
    for file in files:
        if os.path.isdir(input_path + '/' + file):
            get_zip_file(input_path + '/' + file, result)
        else:
            result.append(input_path + '/' + file)


def zip_file_path_floder(input_path, output_path):
    """
    压缩文件
    :param input_path: 压缩的文件夹路径
    :param output_path: 解压（输出）的路径
    :param output_name: 压缩包名称
    :return:
    """
    length = 0
    if "/" in input_path:

        file_paths = input_path.split("/")
        if file_paths[len(file_paths) - 1] != "":
            length = len(input_path) - len(file_paths[len(file_paths) - 1])
        else:
            length = len(input_path) - len(file_paths[len(file_paths) - 2]) - 1

    f = zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED)
    filelists = []
    get_zip_file(input_path, filelists)
    for file in filelists:
        # f.write(file)
        f.write(filename=file, arcname=file[length:])
    # 调用了close方法才会保证完成压缩
    f.close()
    return output_path


