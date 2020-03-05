#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/12/21 15:44
import os, sys, re, json, traceback, time
import base64, requests
from conf.conf import des3_key
from conf.conf import dahua_host, idps_show_host, DOC_IN_CHECK_REDIECT_KEY, DAHUA_SHOW_CHECK_IN_URL, DAHUA_SHOW_DIFF_IN_URL
from tools.utils.des3_utils import Prpcrypt
from tools.idps.idps_utils import check_info
from dahua_log import dhlog as logger
from route.dahua.docObjectIn import DocIn
from urllib.parse import urlencode
#
class dhlog():
    @staticmethod
    def info(message):
        try:
            logger.info(message)
        except:
            print(message)

    @staticmethod
    def error(message):
        try:
            logger.error(message)
        except:
            print(message)


def doc_code_check(doc_code):
    if (not doc_code) or len(doc_code) <= 8:
        return False
    else:
        doc_code = doc_code.replace("\n", "")
        doc_code = doc_code.strip()
        return doc_code


class DataDealIn(object):
    """
    国内文档数据处理
    """
    des3_key = des3_key
    # 标准非标的判定
    DOC_TYPE_STANDARD = DocIn.DOC_TYPE_STANDARD
    DOC_TYPE_NOT_STANDARD_1 = DocIn.DOC_TYPE_NOT_STANDARD_1
    DOC_TYPE_NOT_STANDARD_N = DocIn.DOC_TYPE_NOT_STANDARD_N

    def __init__(self, doc_code, *args, **kwargs):
        self.doc_code = doc_code
        self.args = args
        self.kwargs = kwargs

    @staticmethod
    def get_doc_info(doc_code, *args, **kwargs):
        rowid = kwargs.get("rowid", None)
        data_1_mi = None
        # noinspection PyBroadException
        try:
            key_64 = base64.b64decode(DataDealIn.des3_key)
            prp_des3 = Prpcrypt()
            data_1 = '{"agreeNum":"' + doc_code + '"}'
            data_1_mi = prp_des3.encrypt(data_1, key_64)
        except Exception as e:
            return None, "【{0}】数据加密异常:{1}".format(rowid, traceback.format_exc())
        # 调用接口
        response_text = None
        # noinspection PyBroadException
        try:
            headers = {
                'Content-Type': "application/json",
                'ftoken': "",
                'fapptype': ""
            }
            response = requests.request("POST", dahua_host, data=json.dumps({"agreeNum": data_1_mi}), headers=headers)
            response_text = json.loads(response.text)
        except:
            return None, "【{0}】大华文档信息获取接口调用异常:{1}".format(rowid, traceback.format_exc())
        # 结果解密
        doc_info = None
        # noinspection PyBroadException
        try:
            # 结果解密
            response_text_jiemi = prp_des3.decrypt(response_text["result"], key_64).strip().replace(chr(6), "")
            doc_info = json.loads(response_text_jiemi)
        except Exception as e:
            return None, "【{0}】数据解密异常:{1}".format(rowid, traceback.format_exc())
        dhlog.info(u"【{0}】文档数据获取成功".format(rowid))
        return True, doc_info

    @staticmethod
    def format_doc_info(doc_info, *args, **kwargs):
        def format_standard_doc_info(doc_info, *args, **kwargs):
            rowid = kwargs.get("rowid", None)
            result = None
            try:
                contract = doc_info.get("contract", dict())  # 合同具体信息
                product_list = contract.get("productBillInfoList", list())  # 货物信息列表
                # 承兑信息处理及电汇信息处理
                dianhuikaihuhang = ""
                dianhuizhanghao = ""
                dianhui = contract.get("GF_DH_ACCNT", "").replace(u"：", u":")
                dianhui = dianhui.split(u":")[-1]
                # if len(dianhui.split(":"))>1:
                #     dianhui = dianhui.split(":")[1]
                #     dianhuikaihuhang = re.sub(u"[\d\s]+", "", dianhui).strip()
                #     tmp1 = re.findall(u"[\d\s]{4,}", dianhui)
                #     dianhuizhanghao = ""
                #     if len(tmp1) > 0:
                #         dianhuizhanghao = re.findall(u"[\d\s]{4,}", dianhui)[0].strip()
                dianhuihanghao = contract.get("GF_DH_NO", "")

                chengduikaihuhang = ""
                chengduizhanghao = ""
                chengdui = contract.get("GF_CD_ACCNT", "").replace(u"：", u":")
                chengdui = chengdui.split(u":")[-1]
                # if len(chengdui.split(":"))>1:
                #     chengdui = chengdui.split(":")[1]
                #     chengduikaihuhang = re.sub(u"[\d\s]+", "", chengdui).strip()
                #     tmp1 = re.findall(u"[\d\s]{4,}", chengdui)
                #     chengduizhanghao = ""
                #     if len(tmp1) > 0:
                #         chengduizhanghao = re.findall(u"[\d\s]{4,}", chengdui)[0].strip()
                chengduihanghao = contract.get("GF_CD_NO", "")
                result = dict(
                    status=doc_info.get("STAT_CD", ""),  # 文档状态
                    standard_type=doc_info.get("OCR_TYPE", ""),  # 是否是标准文档   1标准   其他非标
                    doc_type=doc_info.get("OCR_DOC_TYPE", ""),  # 文档模板类型
                    # ftp_b_path=doc_info["FILE_PATH"],  # B文件ftp地址
                    kehumingcheng=contract.get("XDKH_NAME", ""),  # 客户名称
                    zongjine=contract.get("AGREE_AMOUNT", ""),  # 总金额
                    yewuguishuren=contract.get("BUS_OWNER", "")  # 业务归属人
                )
                ht_info = dict(
                    xufang=contract.get("XDKH_NAME", ""),  # 需方  合同头左侧   XDKH_NAME
                    gongfang=contract.get("GF_BUS_ENTITY", ""),  # 供方  合同头右侧  GF_BUS_ENTITY
                    sheng=contract.get("BUS_OWNER_PROV", ""),  # 省    商品表格上面那段话中的             BUS_OWNER_PROV
                    jkrqjjsfs=contract.get("PRODUCT_PAYMENT", ""),  # 结款日期及结算方式   PRODUCT_PAYMENT
                    xufanggaizhang=contract.get("XDKH_NAME", ""),  # 需方(盖章)   XDKH_NAME
                    gongfanggaizhang=contract.get("GF_BUS_ENTITY", ""),  # 供方(盖章)   BUS_OGF_BUS_ENTITYWNER
                    lianxirengongfang=contract.get("BUS_OWNER", ""),  # 联系人 供方    BUS_OWNER
                    zongji=contract["AGREE_AMOUNT"],  # 总计    AGREE_AMOUNT
                    daxiejine="",  # 大写金额      无需字段对应
                    xiaoxiejine="",  # 小写金额     无需字段对应
                    dianhua1=contract.get("XDKH_CONPHONE", ""),  # 电话1  合同头左侧电话  XDKH_CONPHONE
                    dianhua2=contract.get("DH_CON_PHONE", ""),  # 电话2  合同头右侧电话  DH_CON_PHONE
                    lianxiren1=contract.get("XDKH_CON", ""),  # 联系人1 合同头左侧联系人  XDKH_CON
                    lianxiren2=contract.get("DH_CONTACT", ""),  # 联系人2 合同头右侧联系人  DH_CONTACT
                    lianxidizhi1=contract.get("XDKH_ADDR", ""),  # 联系地址1  合同头左侧联系地址  XDKH_ADDR
                    lianxidizhi2=contract.get("GF_ADDR", ""),  # 联系地址2  合同头右侧联系地址  GF_ADDR
                    xiangmuming=contract.get("OPTY_NAME", ""),  # 项目名    商品表格上面那段话中的        OPTY_NAME
                    hetongpingshenbianhao=contract.get("AGREE_NUM", ""),  # 合同评审编号  商品表格上面那段话中的  AGREE_NUM
                    fahuoxuqiushijian="",  # 交货方式-发货需求时间    SHIP_DATE 和 SHIP_DAYS  结合
                    jiaohuodidiansheng=contract.get("CONSIGNEE_STATE", ""),  # 交货方式-发货地点省    CONSIGNEE_STATE
                    jiaohuodidianshi=contract.get("CONSIGNEE_CITY", ""),  # 交货方式-发货地点市   CONSIGNEE_CITY
                    jiaohuodidianqu=contract.get("CONSIGNEE_COUNTY", ""),  # 交货方式-发货地点区    CONSIGNEE_COUNTY
                    jiaohuodidianxiangqing=contract.get("CONSIGNEE_ADDR", ""),  # 交货方式-发货地点详情   CONSIGNEE_ADDR
                    shouhuoren=contract.get("CONSIGNEE", ""),  # 交货方式-收货人   CONSIGNEE
                    shouhuolianxidianhua=contract.get("CONSIGNEE_PHONE", ""),  # 交货方式-收货联系电话    CONSIGNEE_PHONE 多个电话的情况下怎么表示的
                    yunshufangshi=contract.get("SHIP_WAY", ""),  # 运输方式    SHIP_WAY
                    fapiaokaijushijian=contract.get("INVOICE_DAYS", ""),  # 发票开具时间  INVOICE_DAYS
                    fapiaoleixing="",  # 发票类型     INVOICE_NORMAL 和 INVOICE_SPECIAL 结合    # 必填校验
                    zhifufangshi="",  # 支付方式    PAYMENT_ONE PAYMENT_TWO PAYMENT_THR PAYMENT_FOUR 结合
                    lianxiren3=contract.get("XDKH_CON", ""),  # 联系人3    合同下方盖章部分左侧联系人   XDKH_CON
                    hetongqiandingriqi1=contract.get("AGREE_SIGN_DATE", ""),  # 合同签订日期1   合同下方盖章部分左侧合同签订日期   AGREE_SIGN_DATE
                    hetongqiandingriqi2=contract.get("AGREE_SIGN_DATE", ""),  # 合同签订日期2   合同下方盖章部分右侧合同签订日期   AGREE_SIGN_DATE
                    zhanghumingcheng1=contract.get("XDKH_BANKACCNT", ""),  # 账户名称1  合同下方盖章部分左侧账户名称   XDKH_BANKACCNT
                    zhanghumingcheng2=contract.get("GF_ACCNT_NAME", ""),  # 账号名称2  合同下方盖章部分右侧账户名称  GF_ACCNT_NAME
                    kaihuyinhang1=contract.get("XDKH_BANK", ""),  # 开户银行1   合同下方盖章部分左侧开户银行   XDKH_BANK
                    kaihuyinhang2=contract.get("GF_BANK_NAME", ""),  # 开户银行2   合同下方盖章部分右侧开户银行   GF_BANK_NAME
                    yinhangzhanghu1=contract.get("XDKH_BANKNUM", ""),  # 银行账户1  合同下方盖章部分左侧银行账户   XDKH_BANKNUM
                    yinhangzhanghu2=contract.get("GF_BANK_NUM", ""),  # 银行账户2  合同下方盖章部分右侧银行账户   GF_BANK_NUM
                    shuihao1=contract.get("XDKH_TAXNUM", ""),  # 税号1   合同下方盖章部分左侧税号   XDKH_TAXNUM
                    shuihao2=contract.get("GF_TAX_NUM", ""),  # 税号2   合同下方盖章部分右侧税号   GF_TAX_NUM
                    dizhidianhua1=contract.get("XDKH_BILLADDR", "") + contract.get("XDKH_PHONE", ""),
                    # 地址电话1   合同下方盖章部分左侧地址电话    XDKH_BILLADDR 和 XDKH_PHONE
                    dizhidianhua2=contract.get("GF_ADDR", "") + contract.get("GF_TEL", ""),
                    # 地址电话2   合同下方盖章部分右侧地址电话    GF_ADDR 和 GF_TEL
                    gongfangshoukuanzhanghaoxinxi="",  # 供方收款账号信息   GF_DH_ACCNT GF_DH_NO GF_CD_ACCNT GF_CD_NO 结合
                    chuanzhen1="",  # contract["XDKH_CONFAX"], # 传真1   合同头左侧传真    XDKH_CONFAX
                    chuanzhen2="",  # contract["DH_CON_FAX"] # 传真2   合同头右侧传真    DH_CON_FAX
                    dianhuikaihuhang=dianhui,  # 电汇开户行
                    #dianhuizhanghao=dianhuizhanghao,  # 电汇账号
                    dianhuihanghao=dianhuihanghao,  # 电汇行号
                    chengduikaihuhang=chengdui,  # 承兑开户行
                    #chengduizhanghao=chengduizhanghao,  # 承兑账号
                    chengduihanghao=chengduihanghao  # 承兑行号
                )
                result["ht_info"] = ht_info
                transform_product_list = []
                for index, each in enumerate(product_list):
                    each_product = dict(
                        xuhao=str(index),
                        mingcheng=each.get("PROD_NAME", ""),  # 商品名称
                        xinghao=each.get("PROD_MODEL_OUT", u""),  # 商品型号
                        shuliang=str(each.get("QTY", 0)),  # 商品数量
                        danjia=str(each.get("PRICE", 0)),  # 商品单价
                        xiaojijine=str(each.get("AMT", 0)),  # 商品合计金额
                    )
                    transform_product_list.append(each_product)
                ht_info["goods"] = transform_product_list
            except Exception as e:
                return None, "【{0}】标准文档信息格式化出错:{1}".format(rowid, traceback.format_exc())
            return True, result

        def format_not_standard_doc_info(doc_info, *args, **kwargs):
            rowid = kwargs.get("rowid", None)
            result = None
            message_type = kwargs.get("message_type", None)
            try:
                contract = doc_info["contract"]  # 合同具体信息
                result = dict(
                    status=doc_info["STAT_CD"],  # 文档状态
                    standard_type=doc_info["OCR_TYPE"],  # 是否是标准文档   1标准   其他非标
                    ftp_b_path=doc_info["FILE_PATH"],  # B文件ftp地址
                    kehumingcheng=contract["XDKH_NAME"],  # 客户名称
                    zongjine=contract["AGREE_AMOUNT"],  # 总金额
                    yewuguishuren=contract["BUS_OWNER"]  # 业务归属人
                )
            except Exception as e:
                return None, "【{0}】非标{1}文档信息格式化出错:{2}".format(rowid, message_type, traceback.format_exc())
            return True, result

        rowid = kwargs.get("rowid", None)
        standard_type = doc_info.get("OCR_TYPE", None)  # 是否是标准文档   1标准   其他非标
        if not standard_type:
            return None, "【{0}】未获取到对应的文档信息(是否是标准合同):{1}".format(rowid, doc_info)
        if standard_type == DataDealIn.DOC_TYPE_STANDARD:
            return format_standard_doc_info(doc_info, *args, **kwargs)
        elif standard_type == DataDealIn.DOC_TYPE_NOT_STANDARD_1:
            return format_not_standard_doc_info(doc_info, *args, rowid=rowid, message_type="一单一议")
        elif standard_type == DataDealIn.DOC_TYPE_NOT_STANDARD_N:
            return format_not_standard_doc_info(doc_info, *args, rowid=rowid, message_type="框架类")
        else:
            return None, "【{0}】该文档类型无法进行文档审阅/比对操作".format(rowid)

    @staticmethod
    def get_format_doc_info(*args, **kwargs):
        doc_info_result = DataDealIn.get_doc_info(*args, **kwargs)
        if not doc_info_result[0]:
            return doc_info_result
        doc_info = doc_info_result[1]
        return DataDealIn.format_doc_info(doc_info, *args, **kwargs)

    @staticmethod
    def get_format_check_info(task_id, *args, **kwargs):
        rowid = kwargs.get("rowid", None)
        dhlog.info("当前请求rowid:{0}".format(rowid))

        def value_check_util_transform(result_dict, field_name, show_name=None, compare_type=1):
            '''
            单个值校验类型的展示单元转换
            :param result_dict:
            :param field_name:
            :param show_name:
            :param compare_type:1 和一站式数据进行比对    2 不和一站式数据进行比对
            :return:
            '''
            if show_name == None:
                show_name = field_name
            audit_item = result_dict[field_name]
            format_item = dict(title=show_name, compare_type=compare_type, tip=audit_item["audit_tips"],
                               suggestion=audit_item["suggestion"], diff="",
                               content=["".join([each["text"] for each in json.loads(audit_item["context"])])],
                               result="通过" if audit_item["helpfulness"] == 1 else "不通过")
            pass_boo = audit_item["helpfulness"] == 1
            return {"pass_boo": pass_boo, "format_item": format_item}

        def content_check_util_transform(result_dict, field_name, show_name=None):
            """
            条款校验类型的展示单元转换
            :param result_dict: idps审核结果
            :param field_name: 字段名字
            :return:
            """
            if show_name is None:
                show_name = field_name
            audit_item = result_dict[field_name]
            format_item = dict(title=show_name, compare_type=2, tip=audit_item["audit_tips"],
                               suggestion=audit_item["suggestion"], diff=audit_item["audit_sample"],
                               content=["".join([each["text"] for each in json.loads(audit_item["context"])])],
                               result="通过" if audit_item["helpfulness"] == 1 else "不通过")
            pass_boo = audit_item["helpfulness"] == 1
            return {"pass_boo": pass_boo, "format_item": format_item}

        def format_necessary_head(necessaryTermsHeadList):
            necessary_head_dict = {}
            necessary_head_list = []
            for each in necessaryTermsHeadList:
                necessary_head_dict[each["audit_desc"]] = each
            pass_num = 0
            nopass_num = 0
            name_list1 = ["需方", "供方", "省", "总计", "需方(盖章)", "供方(盖章)", "供方联系人", "结款日期及结算方式"]
            for each in name_list1:
                try:
                    format_result = value_check_util_transform(necessary_head_dict, each)
                    if format_result["pass_boo"]:
                        pass_num += 1
                    else:
                        nopass_num += 1
                    necessary_head_list.append(format_result["format_item"])
                except Exception as e:
                    dhlog.error("【{0}】审核结果格式化有误:{1},{2}".format(rowid, each, traceback.format_exc()))

            # 金额大小写
            try:
                for each in necessaryTermsHeadList:
                    if each["audit_desc"] == "扫描件金额大小写校验":
                        format_item = {"title": u"扫描件金额大小写校验", "compare_type": 2}
                        if each["helpfulness"] == 1:
                            format_item["result"] = "通过"
                            pass_num += 1
                        else:
                            format_item["result"] = "不通过"
                            nopass_num += 1
                        format_item["tip"] = each["audit_tips"]
                        format_item["suggestion"] = each["suggestion"]
                        format_item["content"] = [each["text"] for each in json.loads(each["context"])]
                        format_item["diff"] = ""
                        necessary_head_list.append(format_item)
            except Exception as e:
                dhlog.error("【{0}】审核结果格式化有误:{1},{2}".format(rowid, "扫描件金额大小写校验", traceback.format_exc()))
            return {"list": necessary_head_list, "pass": pass_num, "nopass": nopass_num}

        def format_not_necessary(notNecessaryTermsList):
            not_necessary_dict = {}
            not_necessary_list = []
            for each in notNecessaryTermsList:
                not_necessary_dict[each["audit_desc"]] = each
            pass_num = 0
            nopass_num = 0
            name_list1 = ["产品验收条款", "包装方式条款", "到货签收条款", "供方发货时间", "运输费用承担方", "质量保证",
                          "安装与服务", "退货约定", "违约责任", "不可抗力", "合同修订", "合同份数", "特别约定"]
            for each in name_list1:
                try:
                    format_result = content_check_util_transform(not_necessary_dict, each)
                    if format_result["pass_boo"]:
                        pass_num += 1
                    else:
                        nopass_num += 1
                    not_necessary_list.append(format_result["format_item"])
                except Exception as e:
                    dhlog.error("【{0}】审核结果格式化有误:{1},{2}".format(rowid, each, traceback.format_exc()))

            try:
                # 合同纠纷
                title_list = [u"合同纠纷概述", u"合同纠纷-通讯地址", u"合同纠纷-送达日定义"]
                num = 0
                for each in title_list:
                    num += not_necessary_dict[each]["helpfulness"]
                if num == 3:
                    pass_num += 1
                else:
                    nopass_num += 1
                format_result = content_check_util_transform(not_necessary_dict, u"合同纠纷概述", show_name="合同纠纷概述")
                not_necessary_list.append(format_result["format_item"])

                format_result = content_check_util_transform(not_necessary_dict, u"合同纠纷-送达日定义", show_name="合同纠纷-送达日定义")
                not_necessary_list.append(format_result["format_item"])

                audit_item = not_necessary_dict[u"合同纠纷-通讯地址"]
                format_item = dict(title="合同纠纷-通讯地址", compare_type=2, tip=audit_item["audit_tips"],
                                   suggestion=audit_item["suggestion"], diff=audit_item["audit_sample"],
                                   content=["".join([each["text"] for each in json.loads(audit_item["context"])])],
                                   result="通过" if audit_item["helpfulness"] == 1 else "不通过")
                not_necessary_list.append(format_item)
            except Exception as e:
                dhlog.error("【{0}】审核结果格式化有误:{1},{2}".format(rowid, "解决合同纠纷", traceback.format_exc()))

            return {"list": not_necessary_list, "pass": pass_num, "nopass": nopass_num}

        def format_check(checkList):
            check_dict = {}
            check_list = []
            for each in checkList:
                check_dict[each["audit_desc"]] = each
            pass_num = 0
            nopass_num = 0
            name_list1 = [#("电话1", "需方电话"), ("电话2", "供方电话"),
                          ("联系人1", "需方联系人"),
                          ("联系人2", "供方联系人"), ("联系地址1", "需方地址"), ("联系地址2", "供方地址"),
                          ("项目名", "项目名"), ("合同评审编号", "合同评审编号"), ("发票开具时间", "发票开具时间"),
                          ("交货方式-发货需求时间", "发货时间"), ("交货方式-发货地点省", "交货地点-省"),
                          # ("交货方式-发货地点市", "交货地点-市"), ("交货方式-发货地点区", "交货地点-区"),
                          # ("交货方式-发货地点详情", "交货地点-详情"),
                          ("交货方式-收货人", "收货人"),
                          ("交货方式-收货联系电话", "收货联系电话"), ("运输方式", "运输方式"), ("发票类型", "发票类型"),
                          ("支付方式", "支付方式"), ("需方合同签订日期", "需方合同签订日期"),
                          ("需方账户名称", "需方账户名称"), ("需方开户银行", "需方开户银行"),
                          ("需方银行账户", "需方银行账户"), ("需方税号", "需方税号"), ("需方地址电话", "需方地址电话"),
                          ("供方合同签订日期", "供方合同签订日期"), ]
            name_list2 = [("供方账户名称", "供方账户名称"), ("供方开户银行", "供方开户银行"),
                          ("供方银行账户", "供方银行账户"), ("供方税号", "供方税号"), ("供方地址电话", "供方地址电话"),
                          ("电汇开户行", "电汇-开户行"),
                          # ("电汇账号", "电汇-账号"),
                          ("电汇行号", "电汇-行号"),
                          ("承兑开户行", "承兑-开户行"),
                          # ("承兑账号", "承兑-账号"),
                          ("承兑行号", "承兑-行号")]
            for each in name_list1:
                try:
                    format_item = value_check_util_transform(check_dict, each[0], show_name=each[1], compare_type=2)
                    check_list.append(format_item["format_item"])
                except Exception as e:
                    dhlog.error("【{0}】审核结果格式化有误:{1},{2}".format(rowid, each[0], traceback.format_exc()))
            for each in name_list2:
                try:
                    format_item = value_check_util_transform(check_dict, each[0], show_name=each[1], compare_type=1)
                    check_list.append(format_item["format_item"])
                except Exception as e:
                    dhlog.error("【{0}】审核结果格式化有误:{1},{2}".format(rowid, each[0], traceback.format_exc()))
            return {"list": check_list, "pass": pass_num, "nopass": nopass_num}

        def format_necessary_row(necessaryTermsRowList):
            necessary_row_list = []
            pass_num = 0
            nopass_num = 0
            '''
            {
               "index": 0,     //序号
                "title":"货物信息修改",
                "result": "修改",
                "tip": "相较crm数据修改",
                "suggestion": "DH—IPC-HFW8238K-Z-I4$$160$$850$$136000.00",
                "content": ["DH—IPC-HFW8238K-Z-I4","166","840","139440.00"],
                "diff": "型号:<span class='green'>DH—IPC-HFW8238K-Z-I4</span><span class='green'>DH—IPC-HFW8238K-Z-I4</span>;数量:<span class='red'>166</span><span class='green'>160</span>;单价:<span class='red'>840</span><span class='green'>850</span>;小计金额:<span class='red'>139440.00</span><span class='green'>136000.00</span>"
            },
            '''
            for index, each in enumerate(necessaryTermsRowList):
                try:
                    each_item = dict(index=index, title=each["audit_desc"], result=each["audit_desc"][4:],
                                     tip=each["audit_tips"], suggestion=each["suggestion"],
                                     content=each["references"].split("$$"),
                                     diff=each["audit_sample"], compare_type=1)
                    if each["helpfulness"] == 1:
                        pass_num += 1
                    else:
                        nopass_num += 1
                    if each["helpfulness"] == 1:
                        each_item["result"] = "通过"
                    else:
                        if "遗漏" in each["audit_desc"]:
                            each_item["result"] = "遗漏"
                        elif "新增" in each["audit_desc"]:
                            each_item["result"] = "新增"
                        else:
                            each_item["result"] = "修改"

                    necessary_row_list.append(each_item)
                except Exception as e:
                    dhlog.error("【{0}】审核结果格式化有误:{1}".format(rowid, traceback.format_exc()))
            return {"list": necessary_row_list, "pass": pass_num, "nopass": nopass_num}

        p = Prpcrypt()

        audit_result = check_info(task_id)
        audit_info = audit_result["items"]  # idps返回的审核结果列表
        task_id_mi = p.encrypt(str(task_id), DOC_IN_CHECK_REDIECT_KEY)
        result = dict(
            page_url=DAHUA_SHOW_CHECK_IN_URL.format(urlencode({"uuid":task_id_mi})),
            page_url2="http://10.1.253.53:15000/#/review/reviewDetail/{0}?doc_form=2".format(task_id),
            # page_url="{0}/#/review/show/reviewDetail/{1}?doc_form=2".format(idps_show_host, task_id),
            type=DataDealIn.DOC_TYPE_STANDARD
        )
        audit_info_dict = dict(
            necessaryTermsHeadList=[],
            necessaryTermsRowList=[],
            notNecessaryTermsList=[],
            checkList=[]
        )
        # 数据分组
        for each in audit_info:
            if each["audit_rule"] == "necessary_head":
                audit_info_dict["necessaryTermsHeadList"].append(each)
            elif each["audit_rule"] == "not_necessary":
                audit_info_dict["notNecessaryTermsList"].append(each)
            elif each["audit_rule"] == "necessary_row":
                audit_info_dict["necessaryTermsRowList"].append(each)
            elif each["audit_rule"] == "check":
                audit_info_dict["checkList"].append(each)
            else:
                dhlog.info("【{0}】审核结果格式化时未找到该数据类别:{1}".format(rowid, each))
        # necessary_head 处理
        result_necessary_head = format_necessary_head(audit_info_dict["necessaryTermsHeadList"])
        # not_necessary 处理
        result_not_necessary = format_not_necessary(audit_info_dict["notNecessaryTermsList"])
        # necessary_row 处理
        result_necessary_row = format_necessary_row(audit_info_dict["necessaryTermsRowList"])
        # check 处理
        result_check = format_check(audit_info_dict["checkList"])
        # 整合
        num1 = result_necessary_head["pass"] + result_necessary_row["pass"]
        num2 = result_necessary_head["nopass"] + result_necessary_row["nopass"] + num1
        num3 = result_not_necessary["pass"]
        num4 = result_not_necessary["nopass"] + num3
        result["message"] = "必要条款:通过{0}/{1},非必要条款:通过{2}/{3}".format(num1, num2, num3, num4)
        result["num_list"] = [num1, num2, num3, num4]
        if num2 - num1 == 0 and num3 >= 9:
            result["result"] = "通过"
        else:
            result["result"] = "不通过"
        result["detail"] = {
            "necessaryTermsHeadList": result_necessary_head["list"],
            "necessaryTermsRowList": result_necessary_row["list"],
            "notNecessaryTermsList": result_not_necessary["list"],
            "checkList": result_check["list"]
        }
        return result

    @staticmethod
    def get_format_diff_info(diff_result, *args, **kwargs):
        # 相似度位置 each["result"]["diff"]["similar_score"]
        # 比对类型 each["result"]["diff"]["result"][0]["diff_type"]  delete insert replace
        #
        rowid = kwargs.get("rowid", None)
        result = []
        for each in diff_result:
            try:
                p = Prpcrypt()
                task_id_mi = p.encrypt(str(each["id"]), DOC_IN_CHECK_REDIECT_KEY)

                each_result = dict(similar_score=each["similar_score"],
                                   page_url=DAHUA_SHOW_DIFF_IN_URL.format(urlencode({"uuid": task_id_mi})),
                                   result="通过")
                diff_detail = list()
                for each_diff in each["result"]:
                    left = each_diff.get("origin_text", dict()).get("word", "")
                    right = each_diff.get("target_text", dict()).get("word", "")
                    diff_type = "修改"
                    if each_diff["diff_type"] == "delete":
                        diff_type = "新增"
                    elif each_diff["diff_type"] == "insert":
                        diff_type = "删除"
                    diff_detail.append(dict(left=left, right=right, diff_type=diff_type))
                    each_result["detail"] = diff_detail
                if len(diff_detail)>0:
                    each_result["result"] = "不通过"
                each_result["message"] = "差异项合计共{0}个".format(len(diff_detail))

                result.append(each_result)
            except:
                dhlog.error("【{0}】比对数据格式化错误:{1}".format(rowid, traceback.format_exc()))
                # return None, "【{0}】比对数据格式化错误:{1}".format(rowid, traceback.format_exc())
        return result

        # for each in diff_result:
        #     b = each["result"]["diff"]["result"]
        #     for e in b:
        #         # dhlog.info(e["diff_type"], end=":")
        #         left = e.get("origin_text", dict()).get("word", "")
        #         right = e.get("target_text", dict()).get("word", "")
        #         if e["diff_type"] == "delete":
        #
        #             dhlog.info("新增:左【{0}】右【{1}】".format(left, right))
        #         elif e["diff_type"] == "insert":
        #             dhlog.info("删除:左【{0}】右【{1}】".format(left, right))
        #         else:
        #             dhlog.info("修改:左【{0}】右【{1}】".format(left, right))
        # pass


if __name__ == "__main__":
    # a = get_doc_info("1-2507725850")  # 标准
    # a = get_doc_info("1-2484239151")  # 一单一议
    # a = get_doc_info("1011508274250001")  # 框架类
    a = DataDealIn.get_doc_info("1-2322659814", rowid=1)
    print(json.dumps(a[1],ensure_ascii=False,indent=2))
    # dhlog.info(json.dumps(DataDealIn.get_format_doc_info("2071701253630014", rowid=1)[1], ensure_ascii=False, indent=2))
    # dhlog.info(DataDealIn.get_format_check_info(515, rowid=10))

    # dhlog.info(DataDealIn.get_format_check_info(541))
