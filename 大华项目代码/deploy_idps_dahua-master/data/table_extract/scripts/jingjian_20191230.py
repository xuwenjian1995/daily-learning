#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/12/5 17:01
from __future__ import unicode_literals
import os, sys, re, json, traceback, time
from field_conf import guonei
import extract_utils
from pdf2txt_decoder.pdf2txt_decoder import Pdf2TxtDecoder
from document_beans.table import Table
from uuid import uuid4 as uuid
try:
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    from table_extract.app.driver import logger_online
except:
    class a(object):
        def __init__(self):
            pass
        def info(self,message):
            # print(message)
            pass
    logger_online = a()


pdf2txt_decoder = None

def extract_common(extract_func,meta_data_list,result,due_list,add_flag):
    '''

    :param extract_func: 进行抽取使用的方法
    :param meta_data_list:  从这个目标中进行抽取
    :param result:  用于存放所有东西的结果
    :param due_list:  被处理过的段落的位置
    :param add_flag:  标记当前处理到的位置
    :return:
    '''
    extract_result = extract_func(meta_data_list)
    for each in extract_result:
        result[each] = extract_result[each]
    if "due" in result:
        for each_index in result["due"]:
            due_list.append(add_flag + each_index)
    # add_flag = add_flag + result["index"]


def run(context):
    if context["doctype"] not in ["35"]:
        return None
    logger_online.info("进入jingjian抽取方法")
    # 测试一下参数
    '''
    doctype:<type 'str'>
    pdf2txt_decoder:<class 'pdf2txt_decoder.pdf2txt_decoder.Pdf2TxtDecoder'>
    result:<type 'dict'>
    '''
    # logger_online.info("==================================")
    result = context["result"]
    global pdf2txt_decoder
    pdf2txt_decoder = context['pdf2txt_decoder']
    # pdf2txt_decoder = Pdf2TxtDecoder("a")
    meta_data_list = pdf2txt_decoder.get_meta_data_list()
    # 过滤掉可能存在的有问题的部分
    meta_data_list_due = extract_utils.paragraph_delete(meta_data_list)
    # print(meta_data_list_due)
    # -------日志查看用----
    # try:
    #     file_name = "{0}.txt".format(uuid())
    #     with open("/table_extract/table_extract/app/scripts/files/{0}".format(file_name),"a") as f:
    #         for each in meta_data_list_due:
    #             if isinstance(each,Table):
    #                 f.write("{0}\n".format("Table"))
    #                 for line in each.cells:
    #                     sentences = u""
    #                     for cell in line:
    #                         sentences += "{0}||".format(cell.text)
    #                     f.write("{0}\n".format(sentences))
    #                 f.write("{0}\n".format('---------'))
    #             else:
    #                 f.write("{0}\n".format(each.text))
    #     logger_online.info(file_name)
    # except:
    #     logger_online.info("文件创建失败")
    # --------
    '''
    抽取处理逻辑
    起始:  Paragraph   设备购销合同
    '''
    # 获取到 设备购销合同 所在位置
    sbgxht_flag = -1
    # print(meta_data_list)
    for index,each in enumerate(meta_data_list_due):
        # print(each)
        if u"设备购销合同" in each.text:
            sbgxht_flag = index
            break
    if sbgxht_flag == 0:
        for index, each in enumerate(meta_data_list_due):
            if u"供方合同编号" in each.text:
                sbgxht_flag = index + 1
                break
    # print(sbgxht_flag)
    if sbgxht_flag ==-1:
        pass
    else:
        # for each in meta_data_list_due:
        #     logger_online.info(each)
        due_list = []
        # print(meta_data_list_due)
        add_flag = sbgxht_flag
        # 需方和供方
        extract_common(extract_utils.extract_1, meta_data_list_due[add_flag:add_flag+15], result, due_list,add_flag)
        due_list += [each+add_flag for each in result["due"]]
        add_flag = add_flag + result["index"]
        logger_online.info("完成了{0}的抽取".format("需方和供方"))
        # print(meta_data_list_due[add_flag])
        # # 电话 两个
        # extract_common(extract_utils.extract_2, meta_data_list_due[add_flag-1:add_flag + 15], result, due_list, add_flag)
        # due_list += [each + add_flag for each in result["due"]]
        # add_flag = add_flag + result["index"]
        # logger_online.info("完成了{0}的抽取".format("电话"))
        # # 传真 两个
        # extract_common(extract_utils.extract_3, meta_data_list_due[add_flag-1:add_flag + 15], result, due_list, add_flag)
        # due_list += [each+add_flag for each in result["due"]]
        # add_flag = add_flag + result["index"]
        # logger_online.info("完成了{0}的抽取".format("传真"))
        # 联系人 两个
        extract_common(extract_utils.extract_4, meta_data_list_due[add_flag-1:add_flag + 15], result, due_list, add_flag)
        due_list += [each+add_flag for each in result["due"]]
        add_flag = add_flag + result["index"]
        logger_online.info("完成了{0}的抽取".format("联系人"))
        # 联系地址 两个
        extract_common(extract_utils.extract_5, meta_data_list_due[add_flag-1:add_flag + 15], result, due_list, add_flag)
        due_list += [each+add_flag for each in result["due"]]
        add_flag = add_flag + result["index"]
        logger_online.info("完成了{0}的抽取".format("联系地址"))
        # # 一段话 含关键信息     供需双方本着。。。。。
        # extract_common(extract_utils.extract_6, meta_data_list_due[add_flag-1:add_flag + 15], result, due_list, add_flag)
        # due_list += [each+add_flag for each in result["due"]]
        # add_flag = add_flag + result["index"]
        # logger_online.info("完成了{0}的抽取".format("关键信息一段话"))
        # 表格1    货物信息
        extract_common(extract_utils.extract_7, meta_data_list_due[add_flag:add_flag + 13], result, due_list, add_flag)
        due_list += [each+add_flag for each in result["due"]]
        add_flag = add_flag + result["index"]
        logger_online.info("完成了{0}的抽取".format("货物"))
        # # 产品验收条款
        # extract_common(extract_utils.extract_8, meta_data_list_due[add_flag:add_flag + 14], result, due_list, add_flag)
        # due_list += [each+add_flag for each in result["due"]]
        # add_flag = add_flag + result["index"]
        # logger_online.info("完成了{0}的抽取".format("产品验收"))
        # # 包装方式条款
        # extract_common(extract_utils.extract_9, meta_data_list_due[add_flag:add_flag + 14], result, due_list, add_flag)
        # due_list += [each+add_flag for each in result["due"]]
        # add_flag = add_flag + result["index"]
        # logger_online.info("完成了{0}的抽取".format("包装方式"))
        # # 到货签收条款
        # extract_common(extract_utils.extract_10, meta_data_list_due[add_flag:add_flag + 14], result, due_list, add_flag)
        # due_list += [each+add_flag for each in result["due"]]
        # add_flag = add_flag + result["index"]
        # logger_online.info("完成了{0}的抽取".format("到货签收"))
        # # 交货方式条款
        # extract_common(extract_utils.extract_11, meta_data_list_due[add_flag:add_flag + 18], result, due_list, add_flag)
        # due_list += [each+add_flag for each in result["due"]]
        # add_flag = add_flag + result["index"]
        # logger_online.info("完成了{0}的抽取".format("交货方式"))
        # # 供方发货时间条款
        # extract_common(extract_utils.extract_12, meta_data_list_due[add_flag:add_flag + 13], result, due_list, add_flag)
        # due_list += [each+add_flag for each in result["due"]]
        # add_flag = add_flag + result["index"]
        # logger_online.info("完成了{0}的抽取".format("供方发货时间"))
        # # 运输费用承担方条款
        # extract_common(extract_utils.extract_13, meta_data_list_due[add_flag:add_flag + 13], result, due_list, add_flag)
        # due_list += [each+add_flag for each in result["due"]]
        # add_flag = add_flag + result["index"]
        # logger_online.info("完成了{0}的抽取".format("供方发货时间"))
        # # 质量保证条款
        # extract_common(extract_utils.extract_14, meta_data_list_due[add_flag:add_flag + 15], result, due_list, add_flag)
        # due_list += [each+add_flag for each in result["due"]]
        # add_flag = add_flag + result["index"]
        # logger_online.info("完成了{0}的抽取".format("供方发货时间"))
        # # 安装与服务支持条款
        # extract_common(extract_utils.extract_15, meta_data_list_due[add_flag:add_flag + 17], result, due_list, add_flag)
        # due_list += [each+add_flag for each in result["due"]]
        # add_flag = add_flag + result["index"]
        # logger_online.info("完成了{0}的抽取".format("安装与服务支持"))
        # # 发票开具时间
        # extract_common(extract_utils.extract_16, meta_data_list_due[add_flag:add_flag + 13], result, due_list, add_flag)
        # due_list += [each+add_flag for each in result["due"]]
        # add_flag = add_flag + result["index"]
        # logger_online.info("完成了{0}的抽取".format("发票开具时间"))
        # # 发票类型
        # extract_common(extract_utils.extract_17, meta_data_list_due[add_flag:add_flag + 13], result, due_list, add_flag)
        # due_list += [each+add_flag for each in result["due"]]
        # add_flag = add_flag + result["index"]
        # logger_online.info("完成了{0}的抽取".format("发票类型"))
        # # 结款日期与结算方式
        # extract_common(extract_utils.extract_18, meta_data_list_due[add_flag:add_flag + 20], result, due_list, add_flag)
        # due_list += [each+add_flag for each in result["due"]]
        # add_flag = add_flag + result["index"]
        # logger_online.info("完成了{0}的抽取".format("结款日期与结算方式"))
        # #  以下暂未抽取
        # # 支付方式
        # extract_common(extract_utils.extract_19, meta_data_list_due[add_flag:add_flag + 20], result, due_list, add_flag)
        # due_list += [each+add_flag for each in result["due"]]
        # add_flag = add_flag + result["index"]
        # logger_online.info("完成了{0}的抽取".format("支付方式"))
        # # 退货约定
        # extract_common(extract_utils.extract_20, meta_data_list_due[add_flag:add_flag + 20], result, due_list, add_flag)
        # due_list += [each+add_flag for each in result["due"]]
        # add_flag = add_flag + result["index"]
        # logger_online.info("完成了{0}的抽取".format("退货约定"))
        # # 违约责任
        # extract_common(extract_utils.extract_21, meta_data_list_due[add_flag:add_flag + 20], result, due_list, add_flag)
        # due_list += [each+add_flag for each in result["due"]]
        # add_flag = add_flag + result["index"]
        # logger_online.info("完成了{0}的抽取".format("违约责任"))
        # # 不可抗力
        # extract_common(extract_utils.extract_22, meta_data_list_due[add_flag:add_flag + 20], result, due_list, add_flag)
        # due_list += [each+add_flag for each in result["due"]]
        # add_flag = add_flag + result["index"]
        # logger_online.info("完成了{0}的抽取".format("不可抗力"))
        # # 解决合同纠纷
        # extract_common(extract_utils.extract_23, meta_data_list_due[add_flag:add_flag + 20], result, due_list, add_flag)
        # due_list += [each+add_flag for each in result["due"]]
        # add_flag = add_flag + result["index"]
        # logger_online.info("完成了{0}的抽取".format("解决合同纠纷"))
        # # 合同修订
        # extract_common(extract_utils.extract_24, meta_data_list_due[add_flag:add_flag + 22], result, due_list, add_flag)
        # due_list += [each + add_flag for each in result["due"]]
        # add_flag = add_flag + result["index"]
        # logger_online.info("完成了{0}的抽取".format("合同修订"))
        # # 合同份数
        # extract_common(extract_utils.extract_25, meta_data_list_due[add_flag:add_flag + 22], result, due_list, add_flag)
        # due_list += [each + add_flag for each in result["due"]]
        # add_flag = add_flag + result["index"]
        # logger_online.info("完成了{0}的抽取".format("合同份数"))
        # # 特别约定
        # extract_common(extract_utils.extract_26, meta_data_list_due[add_flag:add_flag + 22], result, due_list, add_flag)
        # due_list += [each + add_flag for each in result["due"]]
        # add_flag = add_flag + result["index"]
        # logger_online.info("完成了{0}的抽取".format("特别约定"))
        # 表格2
        extract_common(extract_utils.extract_27, meta_data_list_due[add_flag:add_flag + 22], result, due_list, add_flag)
        due_list += [each + add_flag for each in result["due"]]
        add_flag = add_flag + result["index"]
        logger_online.info("完成了{0}的抽取".format("表格2"))
        #供方收款账号信息
        # extract_common(extract_utils.extract_28, meta_data_list_due[add_flag:add_flag + 22], result, due_list, add_flag)
        # due_list += [each + add_flag for each in result["due"]]
        # add_flag = add_flag + result["index"]
        # logger_online.info("完成了{0}的抽取".format("供方收款账号信息"))
        # 额外判定 当对方在条款后面新增文字内容的时候如何进行判定确保相关内容也被选中
        # print(list(set(due_list)))
        # for index,each in enumerate(meta_data_list_due):
        #     if index not in due_list:
        #         print(each)





        # for each in meta_data_list[sbgxht_flag:sbgxht_flag+3]:
        #     if u"需方" in each.text[:5] and u"供方" in each.text:
        #         content = (each.text).replace(u"：", u":").replace(u"；", u";").replace(u";", u":")
        #         contents = content.split("供方")
        #         xf = u""
        #         gf = u""
        #         if len(contents) == 2:
        #             xf_contents = contents[0].split(u":")
        #             if len(xf_contents) == 2:
        #                 xf = xf_contents[1]
        #             gf_contents = contents[1].split(u":")
        #             if len(gf_contents) == 2:
        #                 gf = gf_contents[1]
        # print("未处理文本:")
        # for i in range(add_flag):
        #     if i not in due_list:
        #         if not isinstance(meta_data_list_due[i],Table):
        #             print(meta_data_list_due[i].text)
        # print("----------------")




        # for each in meta_data_list:
        #     print("{0}:{1}".format(type(each),each))

    if "due" in result:
        result.pop("due")
    if "index" in result:
        result.pop("index")
    context.update({"result":result})
    return result






if __name__ == "__main__":
    for i in range(12):
        print("======================{0}======================".format(i+1))
        rich_content = ""
        with open("files/{0}.json".format("c1f4431532464e6daba747ab738238ca"), "r", encoding='utf8') as f:
            rich_content = json.loads(f.read())

        pdf2txt_decoder =   Pdf2TxtDecoder(rich_content)
        # for each in extract_utils.paragraph_delete(pdf2txt_decoder.get_meta_data_list()):
        #     print(each)
        result = run({"pdf2txt_decoder": pdf2txt_decoder, "result": {},"doctype":"30"})
        # print(json.dumps(result))
        for each in result:
            if each in ["index", "due"]:
                continue
            # if each not in [guonei["zongji"][0]]:
            #     continue
            # for key in guonei:
            #     if each == guonei[key][0]:
            #         print(guonei[key][1], end=":")
            #         break
            # for a in result[each]:
            #     print(a[0], end="||")
            # print()
        break

    # for i in range(12):
    # print("======================{0}======================".format(i+1))
    # rich_content = ""
    # with open("files/{0}.json".format("4be70ec5bef2468aa8c8c959a46bd98a"), "r", encoding='utf8') as f:
    #     rich_content = json.loads(f.read())
    #
    # pdf2txt_decoder = Pdf2TxtDecoder(rich_content)
    #
    # result = run({"pdf2txt_decoder": pdf2txt_decoder, "result": {}})
    # # print(json.dumps(result,indent=2,ensure_ascii=False))
    # for each in result:
    #     if each in ["index", "due"]:
    #         continue
    #     # if each not in [guonei["yunshufangshi"][0]]:
    #     #     continue
    #     for key in guonei:
    #         if each == guonei[key][0]:
    #             print(guonei[key][1], end=":")
    #             break
    #     for a in result[each]:
    #         print(a[0], end="||")
    #     print()
    pass

