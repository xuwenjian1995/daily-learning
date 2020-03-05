#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/12/19 14:05
import os, sys, re, json, traceback, time, requests
from flask_restful import Resource
from flask import request, jsonify, render_template, redirect, send_file
from dahua_log import dhlog
from conf.conf import TAG_TYPE_IN_DICT, dahua_in_dataupload, ftp_port, ftp_username, ftp_password,ftp_host,DOC_IN_CHECK_REDIECT_KEY,IDPS_SHOW_CHECK_IN_URL,IDPS_SHOW_DIFF_IN_URL
from tools.utils.simple_utils import get_uuid, file_extension
from route.dahua.pdfDealIn import pdfdeal
from tools.utils.ftp_download import MyFTP
from tools.idps import idps_utils
from route.dahua import dahuaUtilsIn
import threading
from tools.utils.des3_utils import Prpcrypt
from route.dahua.dahuaUtilsIn import DataDealIn
from route.dahua.docObjectIn import DocIn
import pymysql

class CompareIn(Resource):
    # 静态变量设置
    FROM_APP = DocIn.FROM_APP
    FROM_WEB = DocIn.FROM_WEB
    FROM_MAIL = DocIn.FROM_MAIL
    FROM_RECHECK = DocIn.FROM_RECHECK
    # 标准非标的判定
    DOC_TYPE_STANDARD = DocIn.DOC_TYPE_STANDARD
    DOC_TYPE_NOT_STANDARD_1 = DocIn.DOC_TYPE_NOT_STANDARD_1
    DOC_TYPE_NOT_STANDARD_N = DocIn.DOC_TYPE_NOT_STANDARD_N
    # 基本状态码
    ASYN_CODE = 202   # 异步返回状态码
    SUCCESS_PASS = 200   # 成功并通过状态码
    SUCCESS_NOT_PASS = 201    # 成功但文档未通过状态码
    ARGS_WRONG = 500    # 参数错误
    UNKNOWN_WRONG = 900   # 未知错误
    FILE_SAVE_WRONG = 400   # 文件保存错误
    DOC_CODE_WRONG = 401   # 文档编号获取错误
    DOC_INFO_WRONG = 301    # 文档信息获取错误
    DOC_STATUS_WRONG = 302   # 文档状态不符合要求错误
    DOC_DEAL_WRONG = 303   # 文档审核/比对错误


    @staticmethod
    def _canshu_check(**kwargs):
        """
        参数检查，部分参数不可为空
        :param kwargs:
        :return:
        """
        for key, value in kwargs.items():
            if not value:
                return None, "{0}值不可为空".format(key)
        dhlog.info("【{0}】参数列表信息:{1}".format(kwargs.get("rowid", None), kwargs))
        return True,

    @staticmethod
    def _file_save(*args):
        """
        文件保存
        :param args:
        :return:
        """
        # noinspection PyBroadException
        try:
            if len(args) == 0:
                raise Exception("文档保存失败，参数长度为0")
            file_name = get_uuid()
            args[0].save("files/{0}.pdf".format(file_name))
            return True, file_name
        except AttributeError:
            return None, traceback.format_exc()
        except Exception:
            return None, traceback.format_exc()

    @staticmethod
    def _doc_code_deal(doc_code, file_name, **kwargs):
        """
        文档编号获取
        :param args:
        :return:
        """
        if not dahuaUtilsIn.doc_code_check(doc_code):
            doc_code = pdfdeal(file_name)
            if not dahuaUtilsIn.doc_code_check(doc_code):
                return None, "未得到文档编号"
            else:
                pat_1 = r"([\d\-]+)_?V\d+"
                pat_result = re.findall(pat_1, doc_code)
                if len(pat_result) > 0:
                    doc_code = pat_result[0]
                if not dahuaUtilsIn.doc_code_check(doc_code):
                    # doc_code = "2071910176560001"  #测试数据
                    return None, "未得到文档编号"
        return True, doc_code

    @staticmethod
    def _doc_info_deal(**kwargs):
        """
        文档信息详情获取
        :param args:
        :return:
        """
        # noinspection PyBroadException
        try:
            return DataDealIn.get_format_doc_info(**kwargs)
        except Exception:
            return None, traceback.format_exc()

    @staticmethod
    def _doc_status_deal(doc_info):
        """
        文档状态判定
        :param args:
        :return:
        """
        doc_status = doc_info.get("status", None)
        kehumingcheng = doc_info.get("kehumingcheng", None)
        zongjine = doc_info.get("zongjine", None)
        yewuguishuren = doc_info.get("yewuguishuren", None)
        if (not doc_status) or (doc_status not in ["Approving"]):
            return None, doc_status, kehumingcheng, zongjine, yewuguishuren, "合同状态不是审批中文档"
        else:
            return True, doc_status, kehumingcheng, zongjine, yewuguishuren
        # return True, doc_status, kehumingcheng, zongjine, yewuguishuren

    @staticmethod
    def _doc_deal(doc_info, **kwargs):
        """
        文档处理
        需要判定from从而确定异步还是同步
        需要判定标准还是非标
        标准需要判定模板编号
        :param file_name: 文件的uuid用于后续的文档处理
        :param from_where:  来自于哪里，用于做初步判定
        :param kwargs:
        :return:
        """

        class DocCheckThread(threading.Thread):
            """
            文档审核专门用的线程 还负责数据的上传
            """

            def __init__(self, doc_info, **kwargs):
                """
                :param file_uuid: 文件名的uuid
                :param doc_info:  文档信息
                :param kwargs: 返回时会用到的数据
                """
                threading.Thread.__init__(self)
                self.doc_info = doc_info
                self.kwargs = kwargs

            def run(self):
                upload_data_kwargs = self.kwargs
                doc_obj = self.kwargs.get("doc_obj", dict())
                # dhlog.info(upload_data)
                doc_standard_type = self.doc_info["standard_type"]  # 是否是标准文件
                if doc_standard_type == CompareIn.DOC_TYPE_STANDARD:  # 标准
                    doc_obj.update(status="{0}=>标准文件流程".format(doc_obj.status), **upload_data_kwargs)
                    # True, success_code, result
                    deal_result = _doc_deal_standard(doc_info, **self.kwargs)
                    if not deal_result[0]:
                        upload_data_kwargs["flag"] = "fail"
                        upload_data_kwargs["wrong_code"] = CompareIn.DOC_DEAL_WRONG
                        upload_data_kwargs["code"] = CompareIn.DOC_DEAL_WRONG
                        upload_data_kwargs["wrong_message"] = deal_result[1]
                        upload_data_kwargs["wrong_info"] = deal_result[1]
                    else:
                        upload_data_kwargs["flag"] = "success"
                        upload_data_kwargs["wrong_code"] = deal_result[1]
                        upload_data_kwargs["code"] = deal_result[1]
                        upload_data_kwargs["wrong_message"] = ""
                        upload_data_kwargs["wrong_info"] = ""
                        upload_data_kwargs["result"] = deal_result[2]
                    self.update_data(upload_data_kwargs)
                else: # 非标
                    doc_obj.update(status="{0}=>非标文件流程".format(doc_obj.status))
                    deal_result = _doc_deal_not_standard(doc_info, **self.kwargs)
                    if not deal_result[0]:
                        upload_data_kwargs["flag"] = "fail"
                        upload_data_kwargs["wrong_code"] = CompareIn.DOC_DEAL_WRONG
                        upload_data_kwargs["code"] = CompareIn.DOC_DEAL_WRONG
                        upload_data_kwargs["wrong_message"] = deal_result[1]
                        upload_data_kwargs["wrong_info"] = deal_result[1]
                    else:
                        upload_data_kwargs["flag"] = "success"
                        upload_data_kwargs["wrong_code"] = deal_result[1]
                        upload_data_kwargs["code"] = deal_result[1]
                        upload_data_kwargs["wrong_message"] = ""
                        upload_data_kwargs["wrong_info"] = ""
                        upload_data_kwargs["result"] = deal_result[2]
                    self.update_data(upload_data_kwargs)

            @staticmethod
            def update_data(result):
                doc_obj = result.get("doc_obj", dict())
                result["doc_obj"] = "文档处理信息已记录"
                # noinspection PyBroadException
                try:
                    headers = {
                        'Content-Type': "application/json",
                        'Cache-Control': "no-cache",
                        'ftoken': "",
                        'fapptype': ""
                    }
                    dhlog.info("【{0}】上传数据内容:{1}".format(kwargs.get("rowid", None), result))
                    response = requests.post(
                        url=dahua_in_dataupload,
                        data=json.dumps({"result": json.dumps(result)}),
                        headers=headers
                    )
                    doc_obj.update(status="{0}=>数据结果已上传".format(doc_obj.status), return_json=result, wrong_info=str(response.content, encoding="utf-8"))
                    dhlog.info("【{0}】数据上传结果:{1}".format(kwargs.get("rowid", None), response.content))
                except Exception as e:
                    doc_obj.update(status="{0}=>输出上传出错:{1}".format(doc_obj.status, traceback.format_exc()), return_json=result)
                    dhlog.error("【{0}】数据上传出错:{1}".format(kwargs.get("rowid", None), traceback.format_exc()))

        def _doc_deal_standard(doc_info, file_name, **kwargs):
            """
            标准文档处理
            :param file_name: 文档名的uuid
            :param doc_info: 用于上传审核信息用的参数
            :param kwargs:
            :return:
            """
            rowid = kwargs.get("rowid", None)
            doc_obj = kwargs.get("doc_obj", dict())
            # doc_obj.update(status=DocIn.STANDARD_CHECKING, **kwargs)
            # noinspection PyBroadException
            try:
                doc_tag_type = doc_info["doc_type"]  # 获取文档的idps文档类型
                doc_conf = TAG_TYPE_IN_DICT.get(doc_tag_type, TAG_TYPE_IN_DICT["other"])
                idps_doc_tag_id = doc_conf["type_id"]
                idps_checkpoint_list = doc_conf["check_id_list"]
                kwargs["idps_doc_type"] = idps_doc_tag_id
                dhlog.info("【{0}】该文档为标准合同，其信息有:doc_tag_id[{1}],checkpoint_list:[{2}]".format(rowid,
                                                                    idps_doc_tag_id, idps_checkpoint_list))
                with open("conf/model/{0}.json".format(idps_doc_tag_id), "r") as f:
                    tiaokuan = json.loads(f.read())
                doc_info["ht_info"]["tiaokuan"] = tiaokuan
                audit_result_info = idps_utils.check_saomiao(type_id=idps_doc_tag_id,
                                                             checkt_id_list=idps_checkpoint_list,
                                                             file_path="files/{0}.pdf".format(file_name),
                                                             extra_conf=doc_info["ht_info"])
                dhlog.info("【{0}】标准流程审核完成".format(rowid))
                doc_obj.update(status="{0}=>数据格式化".format(doc_obj.status), **kwargs)
                task_id = audit_result_info["task_id"]
                result = DataDealIn.get_format_check_info(task_id, **kwargs)
                # audit_result = idps_utils.check_info(task_id)
                # result = dahuaUtilsIn.format_check_info_in(audit_result, task_id)
                # dhlog.info(result)
                success_code = CompareIn.SUCCESS_PASS if result["result"] == "通过" else CompareIn.SUCCESS_NOT_PASS
                # kwargs["result"] = result
                doc_obj.update(status="{0}=>审核完成结果为:{1}".format(doc_obj.status, result["result"]))
                return True, success_code, result
            except Exception as e:
                return None, traceback.format_exc()

        def _doc_deal_not_standard(doc_info, file_name, **kwargs):
            """
            非标文档处理
            :param file_name:
            :param doc_info:
            :param kwargs:
            :return:
            """
            def ftp_download(ftp, ftp_path, file_name, rowid):
                # ftp地址转换
                ftp_host_tmp = "{0}:{1}".format(ftp_host,ftp_port)
                if ftp_host_tmp not in ftp_path:
                    # dhlog.error("【{0}】ftp地址格式有误下载失败:{1}".format(rowid, ftp_path))
                    return None, "【{0}】ftp地址格式有误下载失败:{1}".format(rowid, ftp_path)
                ftp_path = ftp_path.split(ftp_host_tmp)[1][1:]

                # new_file_name = "{0}.{1}".format(file_name, ftp_path.split(".")[-1])
                new_file_path = "files/{0}".format(file_name)
                ftp.download_file(new_file_path, ftp_path)
                dhlog.info("【{0}】ftp文件下载成功:{1}".format(rowid, file_name))
                return True,



            rowid = kwargs.get("rowid", None)
            doc_obj = kwargs.get("doc_obj", dict())
            # doc_obj.update(status=DocIn.NOTSTANDARD_DIFFINIG, **kwargs)
            file_name_list = []
            doc_standard_type = doc_info["standard_type"]
            try:
                ftp_list = doc_info.get("ftp_b_path", None)
                if (not isinstance(ftp_list, list)) or len(ftp_list) == 0:
                    return None, "ftp_list数据不为list或为空list"
                # 实际需要删除
                # ftp_list=[each.replace("docx", "pdf") for each in ftp_list]
                if doc_standard_type == CompareIn.DOC_TYPE_NOT_STANDARD_1:
                    ftp_list = [ftp_list[0]]
                    dhlog.info("【{0}】该文档为非标一单一议合同，其ftp比对文件地址为:{1}".format(rowid, ftp_list[0]))
                else:
                    dhlog.info("【{0}】该文档为非标框架类合同，其ftp比对文件地址为:{1}".format(rowid, ftp_list))
                kwargs["ftp_path_list"] = ftp_list
                doc_obj.update(status="{0}=>待比对ftp地址格式判定通过".format(doc_obj.status), **kwargs)
                ftp = MyFTP(host=ftp_host, user=ftp_username, passwd=ftp_password, port=ftp_port)
                for each in ftp_list:
                    each_name = get_uuid() + file_extension(each)
                    download_result = ftp_download(ftp, each, each_name, rowid)
                    if not download_result[0]:
                        return download_result
                    file_name_list.append(each_name)
                ftp.quit()
                # doc_obj.update(status="{0}=>ftp文件全部下载完成".format(doc_obj.status))
            except Exception as e:
                dhlog.error("【{0}】非标流程ftp文件下载异常:{1}".format(rowid, traceback.format_exc()))
                return None, "【{0}】非标流程ftp文件下载异常:{1}".format(rowid, traceback.format_exc())

            # 开始调用文档比对
            diff_result = []
            doc_obj.update(status="{0}=>下载完成，文档比对中".format(doc_obj.status))
            try:
                for each_name in file_name_list:
                    each_result = idps_utils.diff("files/{0}.pdf".format(file_name), "files/{0}".format(each_name))
                    # dhlog.info(each_result)
                    each_result["result"]["diff"]["id"] = each_result["history_id"]
                    diff_result.append(each_result["result"]["diff"])
            except Exception as e:
                dhlog.error("【{0}】非标流程调用比对异常:{1}".format(rowid, traceback.format_exc()))
                return None, "【{0}】非标流程调用比对异常:{1}".format(rowid, traceback.format_exc())
            doc_obj.update(status="{0}=>比对完成，数据格式化中".format(doc_obj.status))
            format_result = DataDealIn.get_format_diff_info(diff_result, **kwargs)
            if len(format_result) == 0:
                dhlog.error("【{0}】非标流程比对结果格式化异常".format(rowid))
                return None, "【{0}】非标流程比对结果格式化异常".format(rowid)
            dhlog.info("【{0}】非标流程比对完成".format(rowid))
            if doc_standard_type == CompareIn.DOC_TYPE_NOT_STANDARD_1: # 一单一议
                doc_obj.update(status="{0}=>一单一议单比对结果重组".format(doc_obj.status))
                result = format_result[0]
                result["type"] = DataDealIn.DOC_TYPE_NOT_STANDARD_1
                success_code = CompareIn.SUCCESS_PASS
                # kwargs["result"] = result
                # doc_obj.update(status=DocIn.NOTSTANDARD_OVER, **kwargs)
                return True, success_code, result
            else: # 框架类
                doc_obj.update(status="{0}=>框架类多比对结果重组".format(doc_obj.status))
                for each in format_result:
                    each["type"] = DataDealIn.DOC_TYPE_NOT_STANDARD_N
                success_code = CompareIn.SUCCESS_PASS
                # kwargs["result"] = format_result
                # doc_obj.update(status=DocIn.NOTSTANDARD_OVER, **kwargs)
                return True, success_code, format_result


            # return format_result


        # 来自邮箱，同步
        from_where = kwargs.get("from_where", None)
        doc_standard_type = doc_info["standard_type"]
        kwargs["standard_type"] = doc_standard_type
        doc_obj = kwargs.get("doc_obj", dict())
        if from_where in [CompareIn.FROM_MAIL, CompareIn.FROM_RECHECK]:
              # 判断标准或者非标
            if doc_standard_type == CompareIn.DOC_TYPE_STANDARD:  # 标准
                # True, success_code, result
                doc_obj.update(status="{0}=>同步标准流程执行中".format(doc_obj.status), **kwargs)
                deal_result = _doc_deal_standard(doc_info, **kwargs)
                return deal_result
            else:
                doc_obj.update(status="{0}=>同步非标流程执行中".format(doc_obj.status), **kwargs)
                deal_result = _doc_deal_not_standard(doc_info, **kwargs)
                return deal_result

        # 非来自邮箱，异步
        else:
            # 做独立线程处理
            doc_obj.update(status="{0}=>异步流程执行中".format(doc_obj.status), **kwargs)
            doc_check_thread = DocCheckThread(doc_info, **kwargs)
            doc_check_thread.start()
            return True, CompareIn.ASYN_CODE, "文档处理中..."

    @staticmethod
    def _return_fail(wrong_code, wrong_message, **kwargs):
        """
        返回错误结果
        :param wrong_code: 错误编码
                文档保存失败 400      识别合同号失败 401
                合同信息获取失败 301    上传失败 402（不需要关注）
                合同状态非审批中 302  文档审核失败 303
        :param wrong_message:
        :param args:
        :param kwargs:
        :return:
        """
        return_json = kwargs
        return_json["flag"] = "fail"
        return_json["wrong_code"] = wrong_code
        return_json["code"] = wrong_code
        return_json["wrong_message"] = wrong_message
        return_json["wrong_info"] = wrong_message
        return_json["doc_obj"] = "文档处理信息已记录"
        dhlog.info("【{0}】返回请求结果:{1}".format(kwargs.get("rowid", None), return_json))
        return jsonify(return_json)

    @staticmethod
    def _return_success(success_code, **kwargs):
        """
        返回成功结果
        :param success_code: 成功结果编号
               异步返回上传成功处理中 202     文档通过 200    文档未通过 201
        :param args:
        :param kwargs:
        :return:
        """
        doc_obj = kwargs.get("doc_obj", dict())
        return_json = kwargs
        return_json["flag"] = "success"
        return_json["wrong_code"] = success_code
        return_json["code"] = success_code
        return_json["wrong_message"] = kwargs.get("wrong_message", None)
        return_json["wrong_info"] = kwargs.get("wrong_message", None)
        return_json["doc_obj"] = "文档处理信息已记录"
        doc_obj.update(status="{0}=>请求处理结束".format(doc_obj.status),return_json=return_json, **kwargs)
        dhlog.info("【{0}】返回请求结果:{1}".format(kwargs.get("rowid", None), return_json))
        return jsonify(return_json)

    def post(self):
        """
        ftp_path = ftp路径   仅用于回传  可为None
        from_where = None   # app  web   邮箱  不可为空
        rowid = None   用于异步操作，不可为空
        doc_code = None    文档编号  可为空
        user_code = None    用户编码  可为空
        file = None    文件  不可为空
        file_name = None    文件名   不需要传入
        message_type = None    错误类型  不需要传入
        doc_info = None   文档信息  不需要传入
        :return:
        """
        # 参数获取
        time1 = time.time()
        ftp_path = request.form.get("ftp_path", None)
        from_where = request.form.get("from_where", None)
        rowid = request.form.get("rowid", None)
        doc_code = request.form.get("doc_code", None)
        user_code = request.form.get("user_code", None)
        file = request.files['file']
        # 设置返回结果附带的一些参数
        return_json = dict(ftp_path=ftp_path, from_where=from_where, rowid=rowid)
        doc_obj = DocIn(user_code=user_code, doc_code=doc_code, **return_json)  # rowid, from_where, user_code, ftp_path, file_name
        doc_obj.save()
        # 参数检查
        check_result = self._canshu_check(file=file, **return_json)
        return_json["user_code"] = user_code
        return_json["doc_code"] = doc_code
        if not check_result[0]:
            doc_obj.update(status="{0}=>流程中止".format(doc_obj.status), wrong_info=check_result[1], **return_json)
            dhlog.error("【{0}】参数检查未通过:{1}".format(rowid, check_result[1]))
            return self._return_fail(CompareIn.ARGS_WRONG, check_result[1], **return_json)
        dhlog.info("【{0}】参数检查通过".format(rowid))
        doc_obj.update(status="{0}=>参数检查已通过".format(doc_obj.status), **return_json)

        # 文件保存
        save_result = self._file_save(file)
        if not save_result[0]:
            doc_obj.update(status="{0}=>流程中止".format(doc_obj.status), wrong_info=save_result[1], **return_json)
            dhlog.error("【{0}】文件保存失败:{1}".format(rowid, save_result[1]))
            return self._return_fail(CompareIn.FILE_SAVE_WRONG, save_result[1], **return_json)
        file_name = save_result[1]
        return_json["file_name"] = file_name
        dhlog.info("【{0}】文件保存成功:{1}".format(rowid, file_name))
        doc_obj.update(status="{0}=>文件已保存成功".format(doc_obj.status), **return_json)

        # 文档编号抽取
        doc_code_deal_result = self._doc_code_deal(**return_json)
        if not doc_code_deal_result[0]:
            doc_obj.update(status="{0}=>流程中止".format(doc_obj.status), wrong_info=doc_code_deal_result[1], **return_json)
            dhlog.error("【{0}】文档编号识别失败:{1}".format(rowid, doc_code_deal_result[1]))
            return self._return_fail(CompareIn.DOC_CODE_WRONG, doc_code_deal_result[1], **return_json)
        doc_code = doc_code_deal_result[1]
        return_json["doc_code"] = doc_code
        dhlog.info("【{0}】文档编号识别成功:{1}".format(rowid, doc_code))
        doc_obj.update(status="{0}=>文档编号已识别完成".format(doc_obj.status), **return_json)

        # 获取文档详情
        doc_info_deal_result = self._doc_info_deal(**return_json)
        if not doc_info_deal_result[0]:
            doc_obj.update(status="{0}=>流程中止".format(doc_obj.status), wrong_info=doc_info_deal_result[1], **return_json)
            dhlog.info("【{0}】文档信息获取失败:{1}".format(rowid, doc_info_deal_result[1]))
            return self._return_fail(CompareIn.DOC_INFO_WRONG, doc_info_deal_result[1], **return_json)
        doc_info = doc_info_deal_result[1]
        if isinstance(doc_info.get("ht_info", dict()), dict):
            doc_info.get("ht_info", dict())["file_uuid"] = file_name
        dhlog.info("【{0}】文档信息获取成功".format(rowid))
        doc_obj.update(status="{0}=>文档详情获取成功并格式化".format(doc_obj.status), **return_json)

        # 文档状态判定
        doc_status_deal_result = self._doc_status_deal(doc_info)
        doc_status = doc_status_deal_result[1]
        return_json["doc_status"] = doc_status
        return_json["kehumingcheng"] = doc_status_deal_result[2]
        return_json["zongjine"] = doc_status_deal_result[3]
        return_json["yewuguishuren"] = doc_status_deal_result[4]
        if not doc_status_deal_result[0]:
            doc_obj.update(status="{0}=>流程中止".format(doc_obj.status), wrong_info=doc_status_deal_result[5], **return_json)
            dhlog.error("【{0}】文档状态判定未通过:{1}".format(rowid, doc_status_deal_result[5]))
            return self._return_fail(CompareIn.DOC_STATUS_WRONG, doc_status_deal_result[5], **return_json)
        dhlog.info("【{0}】文档状态判定通过:{1}".format(rowid, doc_status))
        doc_obj.update(status="{0}=>文档状态判定通过，继续审核".format(doc_obj.status), **return_json)
        return_json["doc_obj"] = doc_obj

        # 文档处理  审核/比对
        doc_deal_result = self._doc_deal(doc_info, **return_json)
        if not doc_deal_result[0]:
            doc_obj.update(status="{0}=>流程中止".format(doc_obj.status), wrong_info=doc_deal_result[1], **return_json)
            dhlog.error("【{0}】文档审核/比对流程出错:{1}".format(rowid, doc_deal_result[1]))
            return self._return_fail(303, doc_deal_result[1], **return_json)
        success_code = doc_deal_result[1]
        if success_code == CompareIn.ASYN_CODE:  # 异步
            return self._return_success(success_code, result=dict(), wrong_message=doc_deal_result[2],
                                        **return_json)
        else:  # 同步
            time2 = time.time()
            spend_time = str(time2 - time1)
            return self._return_success(success_code, wrong_message="", result=doc_deal_result[2], **return_json,
                                        spend_time = spend_time)


    def get(self):
        rowid = request.args.get("rowid", "")
        from_where = request.args.get("from_where", "")
        doc_code = request.args.get("doc_code", "")
        standard_type = request.args.get("standard_type", "")
        doc_status = request.args.get("doc_status", "")
        username = request.args.get("username", "")
        if username not in ["hugaofeng"]:
            return "请联系相关负责人获取权限"
        num = request.args.get("num", 100)
        try:
            num = int(num)
        except:
            num = 100
        result = DocIn.select_all(rowid=rowid, from_where=from_where, doc_code=doc_code, standard_type=standard_type, doc_status=doc_status, num=num)
        return_result = []
        for each in result:
            each_list = list(each)
            try:
                json_data = each_list[15]
                pat_1 = "reviewDetail/(\d+)\?doc_"
                each_list.append(re.findall(pat_1, json_data)[0])

                # pat_2 = "spend_time.{2,5}([\d\.]+)"
                # each_list.append(re.findall(pat_1, json_data)[0])
            except:
                each_list.append("")
            try:
                json_data = each_list[15]

                pat_2 = "spend_time.{2,5}\"([\d\.]+)"
                each_list.append(re.findall(pat_2, json_data)[0][:5])
            except:
                each_list.append("")

            return_result.append(each_list)
        return render_template('doc_show.html',result=return_result, rowid=rowid, from_where=from_where, doc_code=doc_code, standard_type=standard_type, doc_status=doc_status, num=num,username=username)


class DocInShowCheckRedirect(Resource):
    def get(self):
        uuid = request.args.get("uuid", None)
        if uuid is None:
            return "未查询到该条记录"
        p = Prpcrypt()
        doc_id = p.decrypt(uuid, DOC_IN_CHECK_REDIECT_KEY)
        # return requests.get(IDPS_SHOW_CHECK_IN_URL.format(doc_id)).content
        return render_template("result_show.html", url=IDPS_SHOW_CHECK_IN_URL.format(doc_id))
        # return redirect(IDPS_SHOW_CHECK_IN_URL.format(doc_id))


class DocInShowDiffRedirect(Resource):
    def get(self):
        uuid = request.args.get("uuid", None)
        if uuid is None:
            return "未查询到该条记录"
        p = Prpcrypt()
        doc_id = p.decrypt(uuid, DOC_IN_CHECK_REDIECT_KEY)
        # return requests.get(IDPS_SHOW_CHECK_IN_URL.format(doc_id)).content
        return render_template("result_show.html", url=IDPS_SHOW_DIFF_IN_URL.format(doc_id))

class PdfShow(Resource):
    def get(self):
        file_name = request.args.get("file_name", None)
        if file_name is None:
            return "文件名file_name未存入"
        return send_file("files/{0}.pdf".format(file_name))






if __name__ == "__main__":
    pass
