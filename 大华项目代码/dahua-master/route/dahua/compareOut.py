#!/usr/bin/env python
# coding=utf-8
# author:chenxianglong@datagrand.com
# datetime:2019/12/13 上午10.00

from route.dahua import aboard_utils
from dahua_log import dhlog
from conf import conf
from tools.utils.simple_utils import time_func, get_uuid
from tools.utils.des3_utils import Prpcrypt
from tools.idps import idps_utils
import os, json, traceback
from flask_restful import Resource
from flask import request, jsonify, render_template
import requests
import xlrd
import base64
import datetime
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix= __name__ + "_")

'''
status code 对应：

200： (返回成功）
301： 请求合同信息数据失败（对应大华获取合同信息接口）
401： 【未抽取到合同模板编号】 或【获取合同模板信息失败】（对应大华获取合同模板信息接口）或【从合同模板中抽取json信息失败】（获取合同模板失败）
400： 抽取或者审核失败
403： 上报对比信息失败（对应大华比对结果上报接口）
405： 登录失败（对应大华登录接口）
406： 上报抽取信息失败（对应大华新建AI草稿合同接口）
407:  上报合同附件失败（对应大华上传合同附件接口）
500： 入参错误
900： 未知错误
'''


class CompareOut(Resource):

    def __init__(self):
        self._uuid = get_uuid()
        self._crm_id_list = list()
        self._check_contract_info_list = list()
        self._report_info = dict()
        self._addition_data = dict()  # 附加一些关键信息，为应对接口添加字段情况 
        self._query = None  # 数据库查询对象

    def init_request(self):
        from app import db
        dhlog.info("初始化请求")
        self._uuid = get_uuid()
        self._crm_id_list = list()
        self._check_contract_info_list = list()
        self._report_info = dict()
        self._addition_data = dict()
        if self.__class__.__name__ == "CompareOutMail":
            origin = "邮箱"
        else:
            origin = "接口"
        if self._query:
            db.session.commit()
            self._query = None
        """
        判断请求中的状态，根据状态选取合适的方法获取数据
        """
        self.record_abroad_status(
            process_status="初始化请求",
            request_time=datetime.datetime.now(),
            origin=origin
        )

    @time_func
    def record_abroad_status(self, **kwargs):
        '''
        记录海外数据获取状态，并写入数据库
        '''
        try:
            from app import db
            from route.dahua.abroad_status_model import AbroadStatusModel
            if not self._query:
                """
                如果没有查询到的对象就将传入的数据作为属性值创建一个对象写入数据库
                """
                # 创建对象
                new_item = AbroadStatusModel(
                    uuid=self._uuid
                )
                for key, val in kwargs.items():
                    setattr(new_item, key, val)
                db.session.add(
                    new_item
                )
                db.session.commit()
                self._query = db.session.query(AbroadStatusModel).filter(AbroadStatusModel.uuid == self._uuid).first()
            else:
                for key, val in kwargs.items():
                    if key == "process_status":
                        """
                        更换请求处理的状态并写入数据库
                        """
                        val = self._query.process_status + " => " + val
                    elif key == "addition_info":
                        val = self._query.addition_info + "\n" + val

                    if hasattr(self._query, key):
                        setattr(self._query, key, val)
                db.session.commit()

        except Exception as e:
            dhlog.error("update_abroad_status_model error, error info:{}".format(e))

    def response_success(self, status=200, **kwarg):
        """
        请求处理成功后，将数据组装成json字符串并加上状态存入数据库
        并将数据作为参数返回到前端
        """
        return_json = dict(
            status=status,
            message='返回成功',
            data=kwarg or dict()
        )
        return_json["data"].update(dict(
            uuid=self._uuid,
            crm_id_list=self._crm_id_list,
            check_contract_info_list=self._check_contract_info_list,
            report_info=self._report_info,
        ))
        dhlog.info("返回成功:{}".format(json.dumps(return_json, ensure_ascii=False, indent=2)))
        self.record_abroad_status(
            process_status = "同步返回成功",
            return_info = json.dumps(return_json, ensure_ascii=False, indent=2)
        )
        return jsonify(return_json)

    def response_fail(self, rsn, status=900, **kwarg):
        """
        请求失败后将数据组成json数据。写入数据库并返回给前端
        """
        dhlog.info(traceback.format_exc())
        return_json = dict(
            status=status,
            message=rsn,
            data=kwarg or dict()
        )
        return_json["data"].update(dict(
            uuid=self._uuid,
            crm_id_list=self._crm_id_list,
            check_contract_info_list=self._check_contract_info_list
        ))
        dhlog.info("返回错误:{}".format(json.dumps(return_json, ensure_ascii=False, indent=2)))
        self.record_abroad_status(
            process_status="同步返回错误",
            return_info=json.dumps(return_json, ensure_ascii=False, indent=2)
        )
        return jsonify(return_json)

    def async_response_fail(self, rsn, status=900, **kwarg):
        dhlog.info(traceback.format_exc())
        return_json = dict(
            status=status,
            code=status,
            message=rsn,
            data=kwarg or dict()
        )
        return_json["data"].update(dict(
            uuid=self._uuid,
            crm_id_list=self._crm_id_list,
            check_contract_info_list=self._check_contract_info_list
        ))
        data = dict(
            result=json.dumps([return_json], ensure_ascii=False)
        )
        try:
            response = requests.post(conf.DH_ABOARD_REPORT_CHECK_RESULT_URL, data=data)
            if response.status_code != 200:
                raise Exception("返回状态码:%s" % response.status_code)

            id_list = json.loads(response.text)
            dhlog.info("异步上报异常成功: {}".format(id_list))
            self.record_abroad_status(
                process_status="异步上报异常成功",
                return_info=json.dumps(return_json, ensure_ascii=False, indent=2)
            )
            if isinstance(id_list, list):
                return list(zip(id_list, return_json))
        except Exception as e:
            dhlog.error("异步上报异常失败: {}".format(e))
            self.record_abroad_status(
                process_status="异步上报异常失败",
                error_info=str(e) + "\n" + traceback.format_exc()
            )

    def async_response_success(self, rsn, status=900, **kwarg):
        return_json = dict(
            status=status,
            code=status,
            message='返回成功',
            data=kwarg or dict()
        )
        return_json["data"].update(dict(
            uuid=self._uuid,
            crm_id_list=self._crm_id_list,
            check_contract_info_list=self._check_contract_info_list,
            report_info=self._report_info,
        ))
        self.record_abroad_status(
            process_status="异步上报结果成功",
            return_info=json.dumps(return_json, ensure_ascii=False, indent=2)
        )

    def _save_upload_file(self, file_data):
        '''
        :param file_data: 下载文件数据
        :param uuid: uuid
        :return: 保存文件路径
        '''
        file_path = conf.FILES_DIR + "{0}.pdf".format(self._uuid)
        file_data.save(file_path)
        dhlog.info("保存上传文件成功: {}".format(file_path))
        self.record_abroad_status(
            process_status="保存文件成功",
            save_file_name=file_path
        )
        return file_path

    def _extract_template_code(self, save_file_path, with_no_and_po=False):
        '''
        :param save_file_path: pdf保存的路径
        :return: 模板编号，异常返回None
        '''
        template_code, busiEntity, no, po = "", "", "", ""
        """
        将PDF保存的同时尝试将PDF转换为图片，并将图片的信息识别出来获取到编号和另一个数据
        """
        if with_no_and_po:
            # 返回图片中的相关信息
            template_code, busiEntity, no, po = aboard_utils.extract_t_code(save_file_path, with_no_and_po=with_no_and_po)
        else:
            template_code, busiEntity = aboard_utils.extract_t_code(save_file_path, with_no_and_po=with_no_and_po)

        self.record_abroad_status(
            process_status="抽取模板编号成功",
            screenshot_extract_info=json.dumps(
                dict(
                    template_code=template_code,
                    busiEntity=busiEntity,
                    no=no,
                    po=po,
                ), ensure_ascii=False, indent=2
            )
        )
        if with_no_and_po:
            return template_code, busiEntity, no, po
        else:
            return template_code, busiEntity

    # 大华接口1：使用文件模板代码去获取模板信息
    # 暂时自定义映射
    @time_func
    def _request_dh_template_info(self, template_code, busi_entity):
        '''
        使用获取到的模版编号或busi_entity来请求接口获取合同模版execl文件，并返回路径
        :param template_code: 模板代码
        :return: 成功返回模板路径，否则返回None
        '''
        try:
            template_xls_path = conf.FILES_DIR + "{}.xlsx".format(template_code or busi_entity)
            if os.path.exists(template_xls_path):
                return template_xls_path
            response = requests.get(conf.DH_GET_TEMPLATE_XLS_URL, params=dict(
                templateNum=template_code, busiEntity=busi_entity
            ))
            with open(template_xls_path, "wb") as fw:
                fw.write(response.content)

        except Exception as e:
            dhlog.error("使用文件模板代码去获取模板信息失败, error:{}".format(e))
            self.record_abroad_status(
                process_status="获取模板信息失败",
                error_info=str(e) + "\n" + traceback.format_exc()
            )
            return None

        dhlog.info("返回模板文件路径: {}".format(template_xls_path))
        return template_xls_path

    # 从excel模板中抽取出相应的模板内容
    @staticmethod
    def _extract_from_excel(template_code, busi_entity, template_path):
        '''
        :param template_code: 模板编号
        :param template_path: 模板文件路径
        :return: 抽取dict or None
        '''
        def search_key(search_keys, key_list, val_list):
            search_rst = dict()
            for skey in search_keys:
                for idx, key in enumerate(key_list):
                    if skey in key:
                        search_rst[skey] = val_list[idx]
            return search_rst

        template_dict = None
        if template_code == "HK01" or "HK" in busi_entity:
            try:
                xl = xlrd.open_workbook(template_path)
                table = xl.sheet_by_index(0)
                key_list = table.col_values(1)
                val_list = table.col_values(2)

                template_dict = search_key(list([
                    "Tax",
                    "Warranty",
                    "Claim",
                    "Export Compliance",
                    "Force Majeure",
                    "Applicable Laws and Arbitration",
                    "Special Conditions",
                    "Counterparts",
                    "Export Clearance"
                ]), [str(each).strip() for each in key_list],
                    [str(each).strip() for each in val_list])
            except Exception as e:
                dhlog.error("转换失败:%s" % e)

        dhlog.info("返回抽取模板结果: {}".format(template_dict))
        return template_dict

    # 调用idps审核接口（抽取审核均放到审核接口流程中完成）
    @time_func
    def _extract_review_file(self, template_code, template_dict, post_json_data_list, file_path):
        '''
        :param template_code: 模板编号
        :param file_path: 扫描件保存路径
        :return: 抽取结果，及审核结果列表
        '''
        tag_dict = conf.TAG_TYPE_ABOARD_DICT.get(template_code) or conf.TAG_TYPE_ABOARD_DICT.get("DEFAULT")
        extract_info, review_info_list = None, list()
        try:
            # post_json_data列表为空
            if len(post_json_data_list) == 0:
                """将获取到的扫描件进行idps识别并返回数据"""
                scan_rst = idps_utils.check_saomiao(tag_dict["type_id"], tag_dict["check_id_list"], file_path,
                                                    extra_conf=dict(
                                                        template_dict=template_dict,
                                                        post_data=None,
                                                        file_uuid=os.path.basename(file_path)
                                                    ))
                '''识别结果赋值'''
                _, task_id = scan_rst.get("extract_info"), scan_rst.get("task_id")
                if task_id:
                    """请求IDPS接口，获取扫描件抽取结果，并将结果放入review_info_list中"""
                    check_result = idps_utils.check_info(task_id)["items"]
                    extract_info = json.loads(check_result[0]["related_law"])
                    review_info_list.append(
                        (task_id, check_result)
                    )

            for post_data in post_json_data_list:
                try:
                    # 将获取到的数据，
                    scan_rst = idps_utils.check_saomiao(tag_dict["type_id"], tag_dict["check_id_list"], file_path,
                                                        extra_conf=dict(
                                                            template_dict=template_dict,
                                                            post_data=post_data,
                                                            file_uuid=os.path.basename(file_path)
                                                        ))
                    _, task_id = scan_rst.get("extract_info"), scan_rst.get("task_id")
                    # task_id = "887"
                    if task_id:
                        check_result = idps_utils.check_info(task_id)["items"]
                        extract_info = json.loads(check_result[0]["related_law"])
                        review_info_list.append(
                            (task_id, check_result)
                        )
                except Exception as e:
                    # 单个任务失败情况
                    review_info_list.append(
                        (-1, str(e))
                    )

            self.record_abroad_status(
                process_status="抽取审核关键信息成功",
                extract_info=json.dumps(extract_info, ensure_ascii=False, indent=2),
                review_info=json.dumps(review_info_list, ensure_ascii=False, indent=2)
            )

        except Exception as e:
            dhlog.error("扫描件中抽取审核关键信息失败, error:{}".format(e))
            self.record_abroad_status(
                process_status="抽取审核关键信息失败",
                error_info=str(e) + "\n" + traceback.format_exc()
            )

        dhlog.info("返回抽取结果: {}".format(extract_info))
        dhlog.info("返回审核结果: {}".format(review_info_list))
        return extract_info, review_info_list

    @time_func
    def _oem_login(self):
        # 登录
        headers = {'Content-Type': "application/json"}
        data_json = json.dumps(dict(
            loginId="2",
            password="1"
        ))
        try:
            response = requests.post(conf.DH_OEM_LOGIN_URL,
                                     data=data_json,
                                     headers=headers)
            # response = requests.post(conf.DH_OEM_LOGIN_URL, data=dict(
            #     loginId="2",
            #     password="1"
            # ))
            token = json.loads(response.text).get("result").get("token")
            return token
        except Exception as e:
            dhlog.error("登录oem失败: {}".format(e))
            self.record_abroad_status(
                process_status="登录oem失败",
                error_info=str(e) + "\n" + traceback.format_exc()
            )
            return None

    # 大华接口2：上报审核结果
    @time_func
    def _report_review_info(self, review_info_list, uuid="", origin=0, no=""):
        # 对需要上报对结果进行结构改造，同时校验结果是否通过
        report_info_list = aboard_utils.gen_report_review_info(review_info_list, uuid, origin, no, self._addition_data)
        # 获取改造后的结果数组
        report_result_list = [each["result"] for each in report_info_list]

        data = dict(
            result=json.dumps(report_info_list, ensure_ascii=False)
        )
        # 结果写入数据库
        self.record_abroad_status(
            process_status="上报审核结果",
            report_review_info=json.dumps(report_info_list, ensure_ascii=False, indent=2)
        )
        try:
            # token = self._oem_login()
            # if not token:
            #     return None
            # headers = {'Content-Type': "application/x-www-form-urlencoded", "accessToken": token}
            response = requests.request("POST", conf.DH_ABOARD_REPORT_CHECK_RESULT_URL, data=data)
            if response.status_code != 200:
                raise Exception("返回状态码:%s" % response.status_code)
            id_list = json.loads(response.text)
            dhlog.info("上报审核结果成功: {}".format(id_list))
            if isinstance(id_list, list):
                self.record_abroad_status(
                    process_status="上报审核结果成功",
                    addition_info="审核接口返回：{}".format(id_list)
                )
                return list(zip(id_list, report_result_list))
            else:
                self.record_abroad_status(
                    process_status="上报审核结果失败",
                    error_info="审核接口返回：{}".format(response.text)
                )
        except Exception as e:
            dhlog.error("上报审核结果失败: {}".format(e))
            self.record_abroad_status(
                process_status="上报审核结果失败",
                error_info=str(e) + "\n" + traceback.format_exc()
            )
            return None

    # 大华接口3：上报抽取结果
    @time_func
    def _report_extract_info(self, extract_key_info, template_code, userid=None, mail=None, jsession_id=None,
                             crm_id_list=list(), check_contract_info_list=list(),
                             attach_file_data=None):
        # 上报抽取结果的结构体改造
        report_info = aboard_utils.gen_extract_info(extract_key_info, template_code)
        self._report_info = report_info
        report_info["resultList"] = list()
        # 处理上报数据的编号和上报处理结果，将之对应合并
        for crm_id, (cmp_id, cmp_rst) in zip(crm_id_list, check_contract_info_list):
            report_info["resultList"].append(dict(
                integrationId=crm_id,
                compareFileURL=cmp_id,
                # 考虑到异常情况，比对没有结果的情况
                compareResult="passed" if isinstance(cmp_rst, dict) and "result" in cmp_rst and
                                          (cmp_rst["result"] == "通过" or cmp_rst["result"] == u"通过") else "failed",
            ))

        if userid:
            report_info["uploadeLogin"] = userid
        if mail:
            report_info["postEmail"] = mail
        # 对合并后对数据转换成json字符串，并写入数据库
        json_report_info = json.dumps(report_info, ensure_ascii=False, indent=2)
        self.record_abroad_status(
            process_status="上报抽取结果",
            report_extract_info=json_report_info
        )
        try:
            # headers = {'Content-Type': "application/x-www-form-urlencoded"}
            response = requests.post(conf.DH_ABOARD_REPORT_EXTRACT_RESULT_URL,
                                     data=dict(data=json_report_info),
                                     cookies=dict(JSESSIONID=jsession_id),
                                     files=dict(uploadFile=attach_file_data)
                                     )
            response_data = json.loads(response.text)
            dhlog.info(json_report_info)
            if 'data' not in response_data or response_data['data'] == "0000" or u"未登录" in response_data['data']\
                    or response_data.get("code") == "error":
                raise Exception("上报抽取结果异常，返回数据: {}".format(response.text))
            dhlog.info("上报抽取结果成功: {}".format(response_data['data']))
            self.record_abroad_status(
                process_status="上报抽取结果成功",
                addition_info="抽取接口返回：{}".format(response_data['data'])
            )
            return response_data['data']
        except Exception as e:
            dhlog.error("上报抽取结果数据失败: {}".format(e))
            self.record_abroad_status(
                process_status="上报抽取结果数据失败",
                error_info=str(e) + "\n" + traceback.format_exc()
            )
            return False

    # 大华接口7：登录大华
    @time_func
    def _dh_login(self):
        '''
        :return: JSESSIONID
        '''
        try:
            response = requests.get(conf.DH_REPORT_LOGIN_URL, params=dict(
                userId=conf.DH_REPORT_LOGIN_UID,
                userKey=Prpcrypt().encrypt(conf.DH_REPORT_LOGIN_UID, base64.b64decode(conf.des3_key)),
            ))
            dhlog.info("登录获取到JSEESIONID:{}".format(response.cookies["JSESSIONID"]))
            self.record_abroad_status(
                process_status="登录获取JSEESIONID成功"
            )
            return response.cookies["JSESSIONID"]
        except Exception as e:
            dhlog.error("通过接口调用返回json数据失败: {}".format(e))
            self.record_abroad_status(
                process_status="登录获取JSEESIONID失败",
                error_info=str(e) + "\n" + traceback.format_exc()
            )
            return None

    # 大华接口4：使用no去获取json数据
    @time_func
    def _request_json_by_no(self, no):
        try:
            response = requests.get(conf.DH_ABOARD_GET_CONTRACT_DETAIL_URL, params=dict(agreeNum=no))
            response_data = json.loads(response.text)
            if response_data["code"] != "success":
                raise Exception(response_data["data"])
            dhlog.info("使用no:{0}获取到json数据为:{1}".format(no, response_data["data"]))
            self.record_abroad_status(
                process_status="使用no获取到crm数据",
                crm_data=json.dumps(response_data["data"], ensure_ascii=False, indent=2)
            )
            return response_data["data"]
        except Exception as e:
            dhlog.error("通过接口调用返回json数据失败: {}".format(e))
            self.record_abroad_status(
                process_status="使用no获取crm数据失败",
                error_info=str(e) + "\n" + traceback.format_exc()
            )
            return dict()

    @staticmethod
    @time_func
    def async_review_report(self, **kwargs):  # 异步处理服务 （staticmethod是必须的）
        from app import db
        from route.dahua.abroad_status_model import AbroadStatusModel
        # update_abroad_status_model error, error info:Instance <AbroadStatusModel at 0x7fca987619e8>
        # is not bound to a Session; attribute refresh operation cannot proceed
        # (Background on this error at: http://sqlalche.me/e/bhk3)
        # 错误处理： 更新query对象
        self._query = db.session.query(AbroadStatusModel).filter(AbroadStatusModel.uuid == self._uuid).first()
        self.record_abroad_status(
            process_status="异步执行任务",
        )
        template_code = kwargs.get("template_code")
        template_dict = kwargs.get("template_dict")
        r_json_list = kwargs.get("r_json_list")
        save_file_path = kwargs.get("save_file_path")
        user_id = kwargs.get("user_id")
        no = kwargs.get("no")
        extract_key_info, review_info_list = self._extract_review_file(template_code, template_dict, r_json_list,
                                                                      save_file_path)
        flt_review_info_list = [(task_id, check_result) for task_id, check_result in review_info_list if task_id != -1]
        if not extract_key_info:
            return self.async_response_fail("抽取关键信息失败", status=400)
        elif not flt_review_info_list:
            return self.async_response_fail("审核信息失败", status=400)

        report_info = aboard_utils.gen_extract_info(extract_key_info, template_code)
        self._addition_data.update(report_info)

        self._check_contract_info_list = self._report_review_info(review_info_list, uuid=self._uuid, origin=0, no=no)
        if not self._check_contract_info_list:
            return self.async_response_fail("上报审核信息失败", status=403)

        jsession_id = self._dh_login()
        if not jsession_id:
            return self.async_response_fail("登录失败", status=405)

        row_id = self._report_extract_info(extract_key_info, template_code, userid=user_id, jsession_id=jsession_id,
                                           crm_id_list=self._crm_id_list,
                                           check_contract_info_list=self._check_contract_info_list,
                                           attach_file_data=open(save_file_path, "rb"))
        if not row_id:
            return self.async_response_fail("上报抽取信息失败", status=406)
        # 成功返回处理成功信息（不需要调用审核接口）
        return self.async_response_success("返回成功", status=200)

    @time_func
    def post(self):
        '''
        file: 上传pdf文件
        no: agreementNum， 合同编号， 必传
        userid: 用户工号
        :return:
        '''
        self.init_request()
        post_file = request.files['file']
        no = request.form.get("no", None)
        user_id = request.form.get("userid", None)
        if not post_file or not no or not user_id:
            return self.response_fail("入参错误", status=500)

        self.record_abroad_status(
            userid=user_id,
            param_no=no
        )

        post_json_data_list = self._request_json_by_no(no)
        if not post_json_data_list:
            return self.response_fail("请求合同信息数据失败", status=301)

        # 获取crm_id_list
        self._crm_id_list = [each["Id"] for each in post_json_data_list if "Id" in each and each["Id"]]
        save_file_path = self._save_upload_file(post_file)
        """识别图片中的数据，返回模版名字和文件名标题"""
        template_code, busi_entity = self._extract_template_code(save_file_path)
        dhlog.info("从模板文件中抽取出template_code:{}".format(template_code))
        if not template_code and not busi_entity:
            return self.response_fail("未抽取到合同模板编号", status=401)
        """根据模版名字和文件名去服务器中获取合同数据文件，保存到指定位置并返回路径"""
        template_excel = self._request_dh_template_info(template_code, busi_entity)
        if not template_excel:
            return self.response_fail("获取合同模板信息失败", status=401)
        """以字典形式返回获取到的excel数据中的数字"""
        template_dict = self._extract_from_excel(template_code, busi_entity, template_excel)
        if not template_excel:
            return self.response_fail("从合同模板中抽取json信息失败", status=401)

        self._addition_data.update(dict(
            template_code=template_code,
            busi_entity=busi_entity,
            scene_type=1
        ))

        executor.submit(self.async_review_report, self, template_code=template_code,
                        template_dict=template_dict, r_json_list=post_json_data_list,
                        save_file_path=save_file_path, user_id=user_id,
                        no=no)  # 异步处理抽取审核结果并上报)
        return self.response_success()

    # 用作展示日志
    @time_func
    def get(self):
        uuid = request.args.get("uuid", "")
        origin = request.args.get("origin", "")
        userid = request.args.get("userid", "")
        mail = request.args.get("mail", "")
        param_no = request.args.get("param_no", "")
        username = request.args.get("username", "")
        if username not in ["hugaofeng"]:
            return "请联系相关负责人获取权限"
        num = request.args.get("num", 20)
        num = int(num)

        from app import db
        from route.dahua.abroad_status_model import AbroadStatusModel

        db.session.commit()
        query = db.session.query(AbroadStatusModel)
        if uuid:
            query = query.filter(AbroadStatusModel.uuid.like("%" + uuid + "%"))
        if origin:
            query = query.filter(AbroadStatusModel.origin.like("%" + origin + "%"))
        if userid:
            query = query.filter(AbroadStatusModel.userid.like("%" + userid + "%"))
        if mail:
            query = query.filter(AbroadStatusModel.mail.like("%" + mail + "%"))
        if param_no:
            query = query.filter(AbroadStatusModel.param_no.like("%" + param_no + "%"))

        from sqlalchemy import desc
        query_rst = query.order_by(desc(AbroadStatusModel.request_time)).limit(num).all()

        return render_template('abroad_status.html',
                               query_rst=query_rst,
                               uuid=uuid,
                               userid=userid,
                               mail=mail,
                               param_no=param_no,
                               username=username)


class CompareOutMail(CompareOut):

    # 大华接口5：使用po去获取json数据
    @time_func
    def _request_json_by_po(self, po):
        try:
            response = requests.get(conf.DH_ABOARD_GET_CONTRACT_DETAIL_URL, params=dict(customerPO=po))
            response_data = json.loads(response.text)
            if response_data["code"] != "success":
                raise Exception(response_data["data"])
            dhlog.info("使用po:{0}获取到json数据为:{1}".format(po, response_data["data"]))
            self.record_abroad_status(
                process_status="使用po获取到crm数据",
                crm_data=response_data["data"]
            )
            return response_data["data"]
        except Exception as e:
            dhlog.error("通过接口调用返回json数据失败: {}".format(e))
            self.record_abroad_status(
                process_status="使用po获取crm数据失败",
                error_info=str(e) + "\n" + traceback.format_exc()
            )
            return list()

    # 大华接口6：上报合同附件 # 该接口弃用，deprecated，附件都放在上报抽取数据接口中
    @time_func
    def _upload_contract_attach(self, row_id, file_data, jsession_id=None):
        try:
            response = requests.post(conf.DH_ABOARD_UPLOAD_ATTACH_URL,
                                     data=dict(rowId=row_id),
                                     files=dict(uploadFile=file_data),
                                     cookies=dict(JSESSIONID=jsession_id))
            response_data = json.loads(response.text)
            if response_data["code"] != "success":
                raise Exception(response_data["data"])
            dhlog.info("上传附件成功")
            self.record_abroad_status(
                process_status="上传附件成功",
                crm_data=response_data["data"]
            )
            return True
        except Exception as e:
            dhlog.error("上传附件信息失败: {}".format(e))
            self.record_abroad_status(
                process_status="上传附件信息失败",
                error_info=str(e) + "\n" + traceback.format_exc()
            )
            return False

    @time_func
    def post(self):
        # 初始化
        self.init_request()
        post_file = request.files['file']
        mail = request.form.get("mail", None)
        if not post_file or not mail:
            return self.response_fail("入参错误", status=500)

        self.record_abroad_status(
            mail=mail
        )
        # 保存上传的文件
        save_file_path = self._save_upload_file(post_file)
        # 获取上传文件中的标号、模版类型等信息
        template_code, busi_entity, no, po = self._extract_template_code(save_file_path, with_no_and_po=True)
        dhlog.info("从模板文件中抽取出template_code:{0}, no: {1}, po: {2}".format(template_code, no, po))
        if not template_code and not busi_entity:
            return self.response_fail("未抽取到合同模板编号", status=401)
        # 根据模版编号或po来请求接口获取模版对应的excel文件并返回文件路径
        template_excel = self._request_dh_template_info(template_code, busi_entity)
        if not template_excel:
            return self.response_fail("获取合同模板信息失败", status=401)
        # 记录状态信息
        self._addition_data.update(dict(
            template_code=template_code,
            busi_entity=busi_entity
        ))
        # 读取excel文件，获取BC列的数据并组成key:value形式的字典返回
        template_dict = self._extract_from_excel(template_code, busi_entity, template_excel)
        if not template_excel:
            return self.response_fail("从合同模板中抽取json信息失败", status=401)

        r_json_list = list()
        if no:
            # 使用文件NO请求大华接口，获取相对应的数据
            r_json_list = self._request_json_by_no(no)
            # if not r_json_list:
            #     return self.response_fail("使用合同编号请求合同信息数据失败", status=301)
        elif po:
            # 使用文件PO请求大华接口，获取相对应的数据
            r_json_list = self._request_json_by_po(po)
            # if not r_json_list:
            #     return self.response_fail("使用Custom PO请求合同信息数据失败", status=301)

        if r_json_list:
            # 若请求成功，则在_addition_data中更新状态为1
            self._addition_data.update(dict(
                scene_type=1
            ))
        else:
            # 否则，则在_addition_data中更新状态为2
            self._addition_data.update(dict(
                scene_type=2
            ))
        # 获取请求到的数据中的相关数据的编号
        self._crm_id_list = [each["Id"] for each in r_json_list if "Id" in each and each["Id"]]
        # 用请求大华接口获取到的数据，请求IDPS接口，将数据写入数据库并返回
        extract_key_info, review_info_list = self._extract_review_file(template_code, template_dict, r_json_list,
                                                                  save_file_path)
        # 在请求到的审核结果中获取task_id和check_result
        flt_review_info_list = [(task_id, check_result) for task_id, check_result in review_info_list if task_id != -1]# A, B, C, D
        if not extract_key_info:
            return self.response_fail("抽取关键信息失败", status=400)
        elif not flt_review_info_list:
            return self.response_fail("审核信息失败", status=400)
        # 格式化处理idps接口获取到的数据，并更新到相对应到类属性中
        report_info = aboard_utils.gen_extract_info(extract_key_info, template_code)
        self._addition_data.update(report_info)
        # 调用上报审核接口，
        self._check_contract_info_list = self._report_review_info(review_info_list, uuid=self._uuid, origin=2, no=no)
        if not self._check_contract_info_list:
            return self.response_fail("上报审核信息失败", status=403)

        jsession_id = self._dh_login()
        if not jsession_id:
            return self.response_fail("登录失败", status=405)

        # 将获取到的文件数据以及抽取结果调用大华的接口，将数据上报，并返回上报结果
        fr = open(save_file_path, "rb")
        row_id = self._report_extract_info(extract_key_info, template_code, mail=mail, jsession_id=jsession_id,
                                           crm_id_list=self._crm_id_list,
                                           check_contract_info_list=self._check_contract_info_list,
                                           attach_file_data=fr)
        fr.close()

        if not row_id:
            return self.response_fail("上报抽取信息失败", status=406)

        return self.response_success()


if __name__ == "__main__":
    print("main")
