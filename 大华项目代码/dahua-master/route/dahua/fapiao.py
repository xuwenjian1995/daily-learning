#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/12/26 10:52
import os, sys, re, json, traceback, time
from flask_restful import Resource
from flask import render_template, request
from tools.utils.simple_utils import get_uuid,file_extension
from tools.idps.idps_utils import ocr_fapiao
from dahua_log import dhlog


class Fapiao(Resource):
    def get(self):
        return render_template("fapiao.html", boo=False)

    def post(self):
        file = request.files["file"]
        uuid = get_uuid()
        new_file_name = "{0}{1}".format(uuid, file_extension(file.filename))
        dhlog.info(new_file_name)
        # print(new_file_name)
        try:
            file.save("files/{0}".format(new_file_name))
        except:
            dhlog.error("文件保存失败:{0}".format(traceback.format_exc()))
            return "文件保存失败"
        # print("开始识别")
        result = ocr_fapiao("files/{0}".format(new_file_name))
        if not result:
            result = ocr_fapiao("files/{0}".format(new_file_name))
        if not result:
            result = ocr_fapiao("files/{0}".format(new_file_name))
        if not result:
            result = ocr_fapiao("files/{0}".format(new_file_name))
        if not result:
            return "识别失败请重试"
        # print(result)
        info = list()
        for each in result["img_data_list"][0]["extract_result"]:
            info.append([each["item_name"], each["item_content"]])
        return render_template("fapiao.html", boo=True, result=info, img_path="/pdf/{0}".format(new_file_name))







if __name__ == "__main__":
    pass
