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
from conf.conf import idps_host,tag_type_checkpoint_dict

from tools.utils.ftp_download import MyFTP
from tools.utils.simple_utils import get_uuid
from route.dahua.pdfdeal import pdfdeal
from tools.utils.des3_utils import Prpcrypt
from tools.idps import idps_utils
from tools.utils import simple_utils

from route.dahua import dahua_utils




class CompareInTest(Resource):
    '''
    curl -H "Content-Type: application/json" -X POST -d '{"type":"0"}' 127.0.0.1:9999/dahua/comporein
    '''
    def post(self):
        ftp_path = None
        from_where = None
        rowid = None
        doc_code = None
        user_code = None
        try:
            # ============参数获取
            try:
                ftp_path = json.loads(request.data).get("ftp_path",None)
                from_where = json.loads(request.data).get("from",None)
                rowid = json.loads(request.data).get("rowid",None)
                doc_code = json.loads(request.data).get("doc_code", None)
                user_code = json.loads(request.data).get("user_code", None)

                dhlog.info("ftp_path:{0}".format(ftp_path))
                dhlog.info("from_where:{0}".format(from_where))
                dhlog.info("rowid:{0}".format(rowid))
                dhlog.info("doc_code:{0}".format(doc_code))
                dhlog.info("user_code:{0}".format(user_code))

            except:
                raise Exception("参数获取出错:{0}".format(traceback.format_exc()))
            if ftp_path == None:
                raise Exception("ftp_path参数获取失败")
            elif from_where == None:
                raise Exception("from参数获取失败")
            elif rowid == None:
                raise Exception("rowid参数获取失败")
            elif user_code == None:
                raise Exception("user_code参数获取失败")
        except Exception as e:
            return jsonify({"flag": "fail",  #流程运行正常
                "doc_code": doc_code, #文档编号
                "from": from_where,  # 0web  1app  2邮箱
                "rowid": rowid, #请求id
                "wrong_info":str(e),  #如果有错则显示错误信息
                "ftp_path": ftp_path,
                "user_code": user_code
            })
        from route.dahua.testjson import testjson as result
        result["doc_code"] = doc_code
        result["from"] = from_where
        result["rowid"] = rowid
        result["wrong_info"] = u""
        result["ftp_path"] = ftp_path
        result["user_code"] =user_code
        return jsonify(result)

# 测试样例 ftp://10.1.1.191:21/crm/contract/F9vS907wNraM87dwC3c1-15QI0OH.pdf'
class CompareIn2(Resource):
    '''
    curl -H "Content-Type: application/json" -X POST -d '{"ftp_path":"123","from":"1","rowid":"1","user_code":"123"}' 127.0.0.1:9999/dahua/comporein
    '''
    def post(self):
        # ftp_path = None
        from_where = None
        rowid = None
        doc_code = None
        user_code = None
        file = None
        file_name = None
        try:
            # ============参数获取
            try:
                file = request.files['file']
                file_name = file.filename
                if simple_utils.file_extension(file_name) not in ['.pdf']:
                    raise Exception("请上传pdf格式文件")
                # ftp_path = json.loads(request.data).get("ftp_path", None)
                # from_where = json.loads(request.data).get("from", None)
                # rowid = json.loads(request.data).get("rowid", None)
                # doc_code = json.loads(request.data).get("doc_code", None)
                # user_code = json.loads(request.data).get("user_code", None)

                from_where = request.form.get("from", None)
                rowid = request.form.get("rowid", None)
                doc_code = request.form.get("doc_code", None)
                user_code = request.form.get("user_code", None)


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
        except Exception as e:
            return_json = {"flag": "fail",  # 流程运行正常
                            "doc_code": doc_code,  # 文档编号
                            "from": from_where,  # 0web  1app  2邮箱
                            "rowid": rowid,  # 请求id
                            "wrong_info": str(e),  # 如果有错则显示错误信息
                            "file_name": file_name,
                            "user_code": user_code
                            }
            dhlog.info(return_json)
            return jsonify(return_json)
        dhlog.info("参数获取成功")
        # =============ftp文件下载   文件下载到files目录去
        file_uuid = get_uuid()
        try:
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
        except:
            # ftp.quit()
            return_json = {"flag": "fail",  # 流程运行正常
                            "doc_code": doc_code,  # 文档编号
                            "from": from_where,  # 0web  1app  2邮箱
                            "rowid": rowid,  # 请求id
                            "wrong_info": "文件流保存出错:{0}".format(traceback.format_exc()),  # 如果有错则显示错误信息
                            "file_name": file_name,
                            "user_code": user_code
                            }
            dhlog.info(return_json)
            return jsonify(return_json)
        dhlog.info("文件流保存成功")
        # ==============文档编号获取======
        if dahua_utils.doc_code_check(doc_code) == False:
            doc_code = pdfdeal(file_uuid)
            if dahua_utils.doc_code_check(doc_code) == False:
                # doc_code = "2071910176560001"  #测试数据
                return_json = {"flag": "fail",  # 流程运行正常
                            "doc_code": u"",  # 文档编号
                            "from": from_where,  # 0web  1app  2邮箱
                            "rowid": rowid,  # 请求id
                            "wrong_info": u"合同编号获取失败",  # 如果有错则显示错误信息
                            "file_name": file_name,
                            "user_code": user_code
                            }
                dhlog.info(return_json)
                return jsonify(return_json)
        dhlog.info("获取到文档编号为:{0}".format(doc_code))
        # =============调用大华接口获取文档详情======
        doc_info = None
        try:
            doc_info = dahua_utils.get_doc_info(doc_code)
        except Exception as e:
            return_json = {"flag": "fail",  # 流程运行正常
                            "doc_code": doc_code,  # 文档编号
                            "from": from_where,  # 0web  1app  2邮箱
                            "rowid": rowid,  # 请求id
                            "wrong_info": str(e),  # 如果有错则显示错误信息
                            "file_name": file_name,
                            "user_code": user_code
                            }
            dhlog.info(return_json)
            return jsonify(return_json)
        # if doc_info==None or doc_info.get("status",None) != "Approving":
        #     return_json = {"flag": "fail",  # 流程运行正常
        #                     "doc_code": doc_code,  # 文档编号
        #                     "from": from_where,  # 0web  1app  2邮箱
        #                     "rowid": rowid,  # 请求id
        #                     "wrong_info": "文档状态为{0}，无需审核".format(doc_info["status"]),  # 如果有错则显示错误信息
        #                     "ftp_path": ftp_path,
        #                     "user_code": user_code
        #                     }
            dhlog.info(return_json)
            return jsonify(return_json)
        dhlog.info("文档详情获取成功")
        # =============判断类型========================
        # 标准（不管套不套打了）
        if  doc_info["standard_type"] == "1":
            try:
                doc_type = doc_info["standard_type"]  # 文档类型用于区分 模板及审核规则
                # 根据doc_type配置对应的type_id 和 checkt_id_list
                conf_doc_info = tag_type_checkpoint_dict.get(doc_type,tag_type_checkpoint_dict["other"])
                type_id = conf_doc_info["type_id"]
                checkt_id_list = conf_doc_info["checkt_id_list"]
            except Exception as e:
                return_json = {"flag": "fail",  # 流程运行正常
                                "doc_code": doc_code,  # 文档编号
                                "from": from_where,  # 0web  1app  2邮箱
                                "rowid": rowid,  # 请求id
                                "wrong_info": str(e),  # 如果有错则显示错误信息
                                "file_name": file_name,
                                "user_code": user_code
                                }
                dhlog.info(return_json)
                return jsonify(return_json)
            try:
                audit_result_info =idps_utils.check_saomiao(type_id=type_id,checkt_id_list=checkt_id_list,file_path="files/{0}.pdf".format(file_uuid),extra_conf=doc_info["ht_info"])
                dhlog.info(audit_result_info)
                task_id = audit_result_info["task_id"]
                audit_result = idps_utils.check_info(task_id)
                result = dahua_utils.format_check_info_in(audit_result,task_id)
                return_json = {
                    "flag": "success",
                    "doc_code": doc_code,
                    "from": from_where,
                    "rowid": rowid,  # 请求id
                    "file_name": file_name,
                    "user_code": user_code,
                    "result": result
                }
                return jsonify(return_json)
            except Exception as e:
                return_json = {"flag": "fail",  # 流程运行正常
                                "doc_code": doc_code,  # 文档编号
                                "from": from_where,  # 0web  1app  2邮箱
                                "rowid": rowid,  # 请求id
                                "wrong_info": "审核调用出错:{0}".format(traceback.format_exc()),  # 如果有错则显示错误信息
                                "file_name": file_name,
                                "user_code": user_code
                                }
                dhlog.info(return_json)
                return jsonify(return_json)
        # 非标
        else:
            return "非标"



class CompareIn(Resource):
    '''
    curl -H "Content-Type: application/json" -X POST -d '{"ftp_path":"123","from":"1","rowid":"1","user_code":"123"}' 127.0.0.1:9999/dahua/comporein
    '''
    def post(self):
        ftp_path = None
        from_where = None
        rowid = None
        doc_code = None
        user_code = None
        try:
            # ============参数获取
            try:

                ftp_path = json.loads(request.data).get("ftp_path", None)
                from_where = json.loads(request.data).get("from", None)
                rowid = json.loads(request.data).get("rowid", None)
                doc_code = json.loads(request.data).get("doc_code", None)
                user_code = json.loads(request.data).get("user_code", None)

                # from_where = request.form.get("from", None)
                # rowid = request.form.get("rowid", None)
                # doc_code = request.form.get("doc_code", None)
                # user_code = request.form.get("user_code", None)


                dhlog.info("ftp_path:{0}".format(ftp_path))
                dhlog.info("from_where:{0}".format(from_where))
                dhlog.info("rowid:{0}".format(rowid))
                dhlog.info("doc_code:{0}".format(doc_code))
                dhlog.info("user_code:{0}".format(user_code))

            except:
                raise Exception("参数获取出错:{0}".format(traceback.format_exc()))
            if ftp_path == None:
                raise Exception("ftp_path参数获取失败")
            # elif from_where == None:
            #     raise Exception("from参数获取失败")
            # elif rowid == None:
            #     raise Exception("rowid参数获取失败")
            # elif user_code == None:
            #     raise Exception("user_code参数获取失败")
        except Exception as e:
            return_json = {"flag": "fail",  # 流程运行正常
                            "doc_code": doc_code,  # 文档编号
                            "from": from_where,  # 0web  1app  2邮箱
                            "rowid": rowid,  # 请求id
                            "wrong_info": str(e),  # 如果有错则显示错误信息
                            "ftp_path": ftp_path,
                            "user_code": user_code
                            }
            dhlog.info(return_json)
            return jsonify(return_json)
        dhlog.info("参数获取成功")
        # =============ftp文件下载   文件下载到files目录去
        file_uuid = get_uuid()
        try:
            # ftp地址转换
            ftp_host_tmp = "{0}:{1}".format(ftp_host,ftp_port)
            if ftp_host_tmp not in ftp_path:
                raise Exception("ftp格式错误")
            ftp_path = ftp_path.split(ftp_host_tmp)[1][1:]
            ftp = MyFTP(host=ftp_host, user=ftp_username, passwd=ftp_password, port=ftp_port)
            new_file_name = "{0}.{1}".format(file_uuid,ftp_path.split(".")[-1])
            new_file_path = "files/{0}".format(new_file_name)
            ftp.download_file(new_file_path,ftp_path)
            ftp.quit()
            dhlog.info("ftp文件下载成功:{0}".format(file_uuid))
            # file.save("files/{0}.pdf".format(file_uuid))
        except:
            ftp.quit()
            return_json = {"flag": "fail",  # 流程运行正常
                            "doc_code": doc_code,  # 文档编号
                            "from": from_where,  # 0web  1app  2邮箱
                            "rowid": rowid,  # 请求id
                            "wrong_info": "ftp文件下载出错:{0}".format(traceback.format_exc()),  # 如果有错则显示错误信息
                            "ftp_path": ftp_path,
                            "user_code": user_code
                            }
            dhlog.info(return_json)
            return jsonify(return_json)
        dhlog.info("ftp文件下载成功")
        # ==============文档编号获取======
        if dahua_utils.doc_code_check(doc_code) == False:
            doc_code = pdfdeal(file_uuid)
            if dahua_utils.doc_code_check(doc_code) == False:
                # doc_code = "2071910176560001"  #测试数据
                return_json = {"flag": "fail",  # 流程运行正常
                            "doc_code": u"",  # 文档编号
                            "from": from_where,  # 0web  1app  2邮箱
                            "rowid": rowid,  # 请求id
                            "wrong_info": u"合同编号获取失败",  # 如果有错则显示错误信息
                            "ftp_path": ftp_path,
                            "user_code": user_code
                            }
                dhlog.info(return_json)
                return jsonify(return_json)
        dhlog.info("获取到文档编号为:{0}".format(doc_code))
        # =============调用大华接口获取文档详情======
        doc_info = None
        try:
            doc_info = dahua_utils.get_doc_info(doc_code)
        except Exception as e:
            return_json = {"flag": "fail",  # 流程运行正常
                            "doc_code": doc_code,  # 文档编号
                            "from": from_where,  # 0web  1app  2邮箱
                            "rowid": rowid,  # 请求id
                            "wrong_info": str(e),  # 如果有错则显示错误信息
                            "ftp_path": ftp_path,
                            "user_code": user_code
                            }
            dhlog.info(return_json)
            return jsonify(return_json)
        # if doc_info==None or doc_info.get("status",None) != "Approving":
        #     return_json = {"flag": "fail",  # 流程运行正常
        #                     "doc_code": doc_code,  # 文档编号
        #                     "from": from_where,  # 0web  1app  2邮箱
        #                     "rowid": rowid,  # 请求id
        #                     "wrong_info": "文档状态为{0}，无需审核".format(doc_info["status"]),  # 如果有错则显示错误信息
        #                     "ftp_path": ftp_path,
        #                     "user_code": user_code
        #                     }
            dhlog.info(return_json)
            return jsonify(return_json)
        dhlog.info("文档详情获取成功")
        # =============判断类型========================
        # 标准（不管套不套打了）
        if  doc_info["standard_type"] == "1":
            try:
                doc_type = doc_info["standard_type"]  # 文档类型用于区分 模板及审核规则
                # 根据doc_type配置对应的type_id 和 checkt_id_list
                conf_doc_info = tag_type_checkpoint_dict.get(doc_type,tag_type_checkpoint_dict["other"])
                type_id = conf_doc_info["type_id"]
                checkt_id_list = conf_doc_info["checkt_id_list"]
            except Exception as e:
                return_json = {"flag": "fail",  # 流程运行正常
                                "doc_code": doc_code,  # 文档编号
                                "from": from_where,  # 0web  1app  2邮箱
                                "rowid": rowid,  # 请求id
                                "wrong_info": str(e),  # 如果有错则显示错误信息
                                "ftp_path": ftp_path,
                                "user_code": user_code
                                }
                dhlog.info(return_json)
                return jsonify(return_json)
            try:
                audit_result_info =idps_utils.check_saomiao(type_id=type_id,checkt_id_list=checkt_id_list,file_path="files/{0}.pdf".format(file_uuid),extra_conf=doc_info["ht_info"])
                dhlog.info(audit_result_info)
                task_id = audit_result_info["task_id"]
                audit_result = idps_utils.check_info(task_id)
                result = dahua_utils.format_check_info_in(audit_result,task_id)
                return_json = {
                    "flag": "success",
                    "doc_code": doc_code,
                    "from": from_where,
                    "rowid": rowid,  # 请求id
                    "ftp_path": ftp_path,
                    "user_code": user_code,
                    "result": result
                }
                return jsonify(return_json)
            except Exception as e:
                return_json = {"flag": "fail",  # 流程运行正常
                                "doc_code": doc_code,  # 文档编号
                                "from": from_where,  # 0web  1app  2邮箱
                                "rowid": rowid,  # 请求id
                                "wrong_info": "审核调用出错:{0}".format(traceback.format_exc()),  # 如果有错则显示错误信息
                                "ftp_path": ftp_path,
                                "user_code": user_code
                                }
                dhlog.info(return_json)
                return jsonify(return_json)
        # 非标
        else:
            return "非标"











class CompareOut(Resource):
    def post(self):
        # 参数获取
        ftp_a_path = None
        data_c_json = None

        # ftp文件下载

        # 调用关键信息抽取

        # 调用审核模块

        # 抽取结果与json进行对比

        # 修改数据库结果

        # 格式化返回数据

        # 返回


class CompareOutMail(Resource):
    def post(self):
        # 参数获取
        title = None
        content = None
        file = None
        try:
            title = str(json.loads(request.data).get("title",None))
            content = json.loads(request.data).get("content",None)
            file = request.files["file"]
        except:
            raise Exception("参数获取出错:{0}".format(traceback.format_exc()))
        if title == None:
            raise Exception("title参数获取失败")
        elif content == None:
            raise Exception("content参数获取失败")
        elif file == None:
            raise Exception("file参数获取失败")

        # 解析title和content是否有模板编号

        # 如果没有解析出来则调用文档抽取进行

        # 如果没有获取到模板结果则返回

        # 调用对方接口根据模板编号获取模板的ftp地址

        # ftp文件下载

        # 调用比对接口

        # 比对结果筛选去除

        # 连接数据库修改结果

        # 附件的关键信息抽取

        # 格式化返回结果

        # 调用比对结果上传接口

        # 调用抽取结果上传接口

        # 返回










if __name__ == "__main__":
    print(random())
