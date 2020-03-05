#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/11/12 下午7:16
import os, sys, re, json, traceback, time
from flask_restful import Resource
from flask import Flask, request, jsonify
from random import random
import requests
import base64
# 大华比对
from dahua_log import dhlog

from conf.conf import ftp_password, ftp_username, ftp_host, ftp_port
from conf.conf import des3_key
from conf.conf import dahua_host
from conf.conf import doc_guonei_tag_type_id,doc_guonei_checkpoint_list
from conf.conf import idps_host,tag_type_checkpoint_dict,dahua_in_dataupload

from tools.utils.ftp_download import MyFTP
from tools.utils.simple_utils import get_uuid
from route.dahua.pdfDealIn import pdfdeal
from tools.utils.des3_utils import Prpcrypt
from tools.idps import idps_utils
from tools.utils import simple_utils

from route.dahua import dahuaUtilsIn
import threading

from_app = 1
from_web = 0
from_mail = 2

class DataUpload(threading.Thread):
    '''
    数据上传专门用的线程
    '''
    def __init__(self,doc_code,file_uuid,return_json_thread):
        threading.Thread.__init__(self)
        self.doc_code = doc_code
        self.file_uuid = file_uuid
        self.return_json_thread = return_json_thread



    def run(self):
        # =============调用大华接口获取文档详情======
        try:
            doc_info = dahuaUtilsIn.get_doc_info(self.doc_code)
            dhlog.info("文档详情获取成功")
            # =============判断类型========================
            # 标准（不管套不套打了）
            if doc_info["standard_type"] == "1":
                result = check_type_1(doc_info, self.file_uuid)
                self.return_json_thread["result"] = result
                upload_data(self.return_json_thread)
            elif doc_info["standard_type"] == "2":  # 一单一议全文比对
                return "非标一单一议全文比对"
            else:  # 默认非标 多文档比对
                return "非标 非一单一议"
        except:
            self.return_json_thread["flag"]="fail"
            self.return_json_thread["wrong_info"] = "信息上传出错:{0}".format(traceback.format_exc())
            upload_data(self.return_json_thread)
            #     {
            #     "ftp_path": ftp_path,
            #     "flag": "success",
            #     "doc_code": doc_code,
            #     "from": from_where,
            #     "rowid": rowid,  # 请求id
            #     "file_name": file_name,
            #     "user_code": user_code
            # }

def upload_data(result):
    try:
        dhlog.info("准备发起post请求，其数据为:{0}".format(result))
        headers = {
            'Content-Type': "application/json",
            'Cache-Control': "no-cache",
            'ftoken': "",
            'fapptype': ""
        }
        response = requests.post(
            url=dahua_in_dataupload,
            data=json.dumps({"result":json.dumps(result)}),
            headers=headers
        )
        dhlog.info("请求发送完成")
        dhlog.info(response)
        dhlog.info(response.text)
    except:
        raise Exception("数据上传失败")

# 测试样例 ftp://10.1.1.191:21/crm/contract/F9vS907wNraM87dwC3c1-15QI0OH.pdf'
class CompareIn(Resource):
    def _mail(self):
        kehumingcheng = None
        ftp_path = None
        from_where = None  # app  web   邮箱
        rowid = None
        doc_code = None
        user_code = None
        file = None
        file_name = None
        message_type = None
        doc_info = None
        try:
            # ============参数获取
            ftp_path, from_where, rowid, doc_code, user_code, file, file_name = check_canshu(request)
            # =============ftp文件下载   文件下载到files目录去   现改为文件流直接保存
            file_uuid = get_uuid()
            file_save(file, file_uuid)
            # ==============文档编号获取======
            if dahuaUtilsIn.doc_code_check(doc_code) == False:
                doc_code = get_doc_code(file_uuid)
            # =============调用大华接口获取文档详情======
            doc_info = dahuaUtilsIn.get_doc_info(doc_code)
            kehumingcheng = doc_info["kehumingcheng"]
            dhlog.info("文档详情获取成功")
            # =============判断类型========================
            # 标准（不管套不套打了）
            if doc_info["standard_type"] == "1":

                result = check_type_1(doc_info, file_uuid)

                return_json = {
                    "ftp_path": ftp_path,
                    "flag": "success",
                    "doc_code": doc_code,
                    "from": from_where,
                    "rowid": rowid,  # 请求id
                    "file_name": file_name,
                    "user_code": user_code,
                    "result": result,
                    "kehumingcheng": kehumingcheng
                }
                # upload_data(return_json)
                return jsonify(return_json)
            elif doc_info["standard_type"] == "2":  # 一单一议全文比对

                return "非标"
        except Exception as e:
            return_json = {"ftp_path": ftp_path,
                           "flag": "fail",  # 流程运行正常
                           "doc_code": doc_code,  # 文档编号
                           "from": from_where,  # 0web  1app  2邮箱
                           "rowid": rowid,  # 请求id
                           "wrong_info": "{0}{1}".format(str(e),traceback.format_exc()),  # 如果有错则显示错误信息
                           "file_name": file_name,
                           "user_code": user_code,
                           "kehumingcheng": kehumingcheng
                           }
            dhlog.info(return_json)
            return jsonify(return_json)

    def _notmail(self):
        ftp_path = None
        from_where = None  # app  web   邮箱
        rowid = None
        doc_code = None
        user_code = None
        file = None
        file_name = None
        message_type = None
        doc_info = None
        try:
            # ============参数获取
            ftp_path, from_where, rowid, doc_code, user_code, file, file_name = check_canshu(request)
            # =============ftp文件下载   文件下载到files目录去   现改为文件流直接保存
            file_uuid = get_uuid()
            file_save(file, file_uuid)
            # ==============文档编号获取======

            if dahuaUtilsIn.doc_code_check(doc_code) == False:
                doc_code = get_doc_code(file_uuid)
                return_json = {"ftp_path":ftp_path,
                               "flag": "success",  # 流程运行正常
                               "doc_code": doc_code,  # 文档编号
                               "from": from_where,  # 0web  1app  2邮箱
                               "rowid": rowid,  # 请求id
                               "wrong_info": "",  # 如果有错则显示错误信息
                               "file_name": file_name,
                               "user_code": user_code
                               }
                dhlog.info(return_json)
        except:
            return_json = {"ftp_path": ftp_path,
                           "flag": "fail",  # 流程运行正常
                           "doc_code": doc_code,  # 文档编号
                           "from": from_where,  # 0web  1app  2邮箱
                           "rowid": rowid,  # 请求id
                           "wrong_info": "流程处理出现异常:{0}".format(traceback.format_exc()),  # 如果有错则显示错误信息
                           "file_name": file_name,
                           "user_code": user_code
                           }
            dhlog.info(return_json)
            return jsonify(return_json)
        # 获取到文档编号并且正确
        # =============启用多线程=======
        return_json_thread = {
            "ftp_path": ftp_path,
            "flag": "success",
            "doc_code": doc_code,
            "from": from_where,
            "rowid": rowid,  # 请求id
            "file_name": file_name,
            "user_code": user_code
        }
        data_upload = DataUpload(doc_code, file_uuid, return_json_thread)
        data_upload.start()
        return_json = {"ftp_path": ftp_path,
                       "flag": "success",  # 流程运行正常
                       "doc_code": doc_code,  # 文档编号
                       "from": from_where,  # 0web  1app  2邮箱
                       "rowid": rowid,  # 请求id
                       "wrong_info": "文档处理中...",  # 如果有错则显示错误信息
                       "file_name": file_name,
                       "user_code": user_code
                       }
        dhlog.info(return_json)
        return jsonify(return_json)






    '''
    curl -H "Content-Type: application/json" -X POST -d '{"ftp_path":"123","from":"1","rowid":"1","user_code":"123"}' 127.0.0.1:9999/dahua/comporein
    '''
    def post(self):
        ftp_path = None
        from_where = None   # app  web   邮箱
        rowid = None
        doc_code = None
        user_code = None
        file = None
        file_name = None
        message_type = None
        doc_info = None
        try:
            # 判断请求来自哪里
            from_where = request.form.get("from", None)
            if from_where == None:   # 无法得到该参数则抛出异常结束
                raise Exception("from参数不可为空")
        except Exception as e:
            return_json = {"ftp_path": ftp_path,
                           "flag": "fail",  # 流程运行正常
                           "doc_code": doc_code,  # 文档编号
                           "from": from_where,  # 0web  1app  2邮箱
                           "rowid": rowid,  # 请求id
                           "wrong_info": "{0}".format(str(e)),  # 如果有错则显示错误信息
                           "file_name": file_name,
                           "user_code": user_code
                           }
            dhlog.info(return_json)
            return jsonify(return_json)
        # 如果是邮箱的方式则走邮箱同步流程
        if from_where == from_mail or from_where==str(from_mail):
            return self._mail()
        # 否则走app或web的异步流程
        else:
            return self._notmail()



class ModelIn(Resource):
    def post(self):
        dhlog.info("doc_type:{0}".format(request.form.get("doc_type",None)))
        doc_type = request.form.get("doc_type","other")
        type_id = tag_type_checkpoint_dict.get(doc_type,tag_type_checkpoint_dict["other"])["type_id"]
        with open("conf/model/{0}.json".format(type_id),"r") as f:
            tiaokuan = json.loads(f.read())
        return jsonify(tiaokuan)



class DataRevice(Resource):
    def post(self):
        dhlog.info("接收到请求")
        a = request.form
        b = request.json
        c = request.data
        dhlog.info("form:{0}".format(a))
        dhlog.info("json:{0}".format(b))
        dhlog.info("data:{0}".format(c))
        return "接收成功"


def check_canshu(request):
    try:
        file = request.files['file']
        file_name = file.filename
        if simple_utils.file_extension(file_name) not in ['.pdf']:
            raise Exception("请上传pdf格式文件")

        ftp_path = request.form.get("ftp_path", None)
        from_where = request.form.get("from", None)
        rowid = request.form.get("rowid", None)
        doc_code = request.form.get("doc_code", None)
        user_code = request.form.get("user_code", None)

        dhlog.info("ftp_path:{0}".format(ftp_path))
        dhlog.info("file_name:{0}".format(file_name))
        dhlog.info("from_where:{0}".format(from_where))
        dhlog.info("rowid:{0}".format(rowid))
        dhlog.info("doc_code:{0}".format(doc_code))
        dhlog.info("user_code:{0}".format(user_code))

    except:
        raise Exception("参数获取出错:{0}".format(traceback.format_exc()))
    if file == None:
        raise Exception("file参数获取失败")
    elif from_where == None:
        raise Exception("from参数获取失败")
    elif rowid == None:
        raise Exception("rowid参数获取失败")
    # elif user_code == None:
    #     raise Exception("user_code参数获取失败")

    dhlog.info("参数获取成功")
    return ftp_path,from_where,rowid,doc_code,user_code,file,file_name


def file_save(file,file_uuid):
    # ftp地址转换
    # ftp_host_tmp = "{0}:{1}".format(ftp_host,ftp_port)
    # if ftp_host_tmp not in ftp_path:
    #     raise Exception("ftp格式错误")
    # ftp_path = ftp_path.split(ftp_host_tmp)[1][1:]
    # ftp = MyFTP(host=ftp_host, user=ftp_username, passwd=ftp_password, port=ftp_port)
    # new_file_name = "{0}.{1}".format(file_uuid,ftp_path.split(".")[-1])
    # new_file_path = "files/{0}".format(new_file_name)
    # ftp.download_file(new_file_path,ftp_path)
    # ftp.quit()
    # dhlog.info("ftp文件下载成功:{0}".format(file_uuid))
    file.save("files/{0}.pdf".format(file_uuid))
    dhlog.info("文件流保存成功")


def get_doc_code(file_uuid):
    doc_code = pdfdeal(file_uuid)
    if dahuaUtilsIn.doc_code_check(doc_code) == False:
        # doc_code = "2071910176560001"  #测试数据
        raise Exception("未得到文档编号")
    dhlog.info("获取到文档编号为:{0}".format(doc_code))
    return doc_code


def check_type_1(doc_info,file_uuid):
    doc_type = doc_info["standard_type"]  # 文档类型用于区分 模板及审核规则
    # 根据doc_type配置对应的type_id 和 checkt_id_list
    conf_doc_info = tag_type_checkpoint_dict.get(doc_type, tag_type_checkpoint_dict["other"])
    type_id = conf_doc_info["type_id"]
    checkt_id_list = conf_doc_info["checkt_id_list"]
    with open("conf/model/{0}.json".format(type_id),"r") as f:
        tiaokuan = json.loads(f.read())
    doc_info["ht_info"]["tiaokuan"] = tiaokuan
    audit_result_info = idps_utils.check_saomiao(type_id=type_id, checkt_id_list=checkt_id_list,
                                                 file_path="files/{0}.pdf".format(file_uuid),
                                                 extra_conf=doc_info["ht_info"])
    dhlog.info(audit_result_info)
    task_id = audit_result_info["task_id"]
    audit_result = idps_utils.check_info(task_id)
    result = dahuaUtilsIn.format_check_info_in(audit_result, task_id)
    return result

def check_type_2(doc_info,file_uuid):
    '''
    一单一议     单文件比对
    :param doc_info:
    :param file_uuid:
    :return:
    '''
    doc_type = doc_info["standard_type"]  # 文档类型用于区分 模板及审核规则
    # 根据doc_type配置对应的type_id 和 checkt_id_list
    conf_doc_info = tag_type_checkpoint_dict.get(doc_type, tag_type_checkpoint_dict["other"])
    type_id = conf_doc_info["type_id"]
    checkt_id_list = conf_doc_info["checkt_id_list"]
    audit_result_info = idps_utils.check_saomiao(type_id=type_id, checkt_id_list=checkt_id_list,
                                                 file_path="files/{0}.pdf".format(file_uuid),
                                                 extra_conf=doc_info["ht_info"])
    dhlog.info(audit_result_info)
    task_id = audit_result_info["task_id"]
    audit_result = idps_utils.check_info(task_id)
    result = dahuaUtilsIn.format_check_info_in(audit_result, task_id)
    return result











if __name__ == "__main__":
    pass
