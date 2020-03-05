#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/11/26 下午5:40
import os, sys, re, json, traceback, time
from flask_restful import Resource
from flask import Flask, request, jsonify
from random import random
from tools.utils import simple_utils as utils
from tools.utils.convertPDF import convert_pdf_to_png,shot_of_png,qrcode_parser
from conf.conf import location_foot,location_head,location_middle
from tools.idps.idps_utils import ocr_png

from dahua_log import dhlog


def pdfdeal(file_uuid):
    doc_code = False
    # 将pdf转换成图片
    if convert_pdf_to_png(file_uuid):  # file_uuid_page.png
        # 截图 正文
        if shot_of_png(file_uuid, location_middle, type="middle"):
            message = ocr_png("files/{0}_middle.png".format(file_uuid))
            dhlog.info("content_ocr:{0}".format(message))
            if message:
                message = message.replace(u"，", u",")
                pat_middle = u"审编号为([\d\s\-]+)"
                middle_result = re.findall(pat_middle, message)
                dhlog.info("middle_result_re:{0}".format(middle_result))
                if len(middle_result) > 0 and len(middle_result[0]) > 8:
                    doc_code = re.sub(u"[\s]", "", middle_result[0])
                    if len(doc_code) <= 8:
                        doc_code = False
        # 截图 页脚二维码
        if doc_code == False and shot_of_png(file_uuid, location_foot, type="foot"):
            foot_result = qrcode_parser(file_uuid)
            dhlog.info("foot_code:{0}".format(foot_result))
            if foot_result:
                doc_code = foot_result
        # 截图 页眉
        if doc_code == False and shot_of_png(file_uuid, location_head, type="head"):
            message = ocr_png("files/{0}_head.png".format(file_uuid))
            dhlog.info("head_ocr:{0}".format(message))
            if message:
                message = message.replace(u"：", u":")
                pat_middle = u"合同编号:?([\d\s\-]+)"
                head_result = re.findall(pat_middle, message)
                dhlog.info("head_result_re:{0}".format(head_result))
                if len(head_result) > 0 and len(head_result[0]) > 8:
                    doc_code = re.sub(u"[\s]", "", head_result[0])
                    if len(doc_code) <= 8:
                        doc_code = False
    else:
        return False
    return doc_code


class PDFDeal(Resource):
    def post(self):
        # 获取到pdf并保存
        file = request.files.get("file")
        file_name = file.filename
        file_uuid = utils.get_uuid()
        upload_path = os.path.join('files', file_uuid + utils.file_extension(file_name))
        file.save(upload_path)
        doc_code = pdfdeal(file_uuid)
        return doc_code








if __name__ == "__main__":
    pass
