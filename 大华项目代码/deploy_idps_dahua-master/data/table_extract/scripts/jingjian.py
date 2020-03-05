#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/12/5 17:01
from __future__ import unicode_literals
import os, sys, re, json, traceback, time
from field_conf import guonei
import extract_utils_new as extract_utils
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
    result = context["result"]
    global pdf2txt_decoder
    pdf2txt_decoder = context['pdf2txt_decoder']
    # pdf2txt_decoder = Pdf2TxtDecoder("a")
    meta_data_list = pdf2txt_decoder.get_meta_data_list()
    # 过滤掉可能存在的有问题的部分
    meta_data_list_due = extract_utils.paragraph_delete(meta_data_list)
    # 得到有问题的部分并将其定义为页眉页脚
    delete_mapper_list = extract_utils.get_paragraph_delete(meta_data_list)
    # 输出其他部分作为参考
    context.pop("pdf2txt_decoder")
    logger_online.info(json.dumps(context, ensure_ascii=False, indent=2))
    '''
    抽取处理逻辑
    起始:  Paragraph   设备购销合同
    '''
    try:
        result1 = extract_utils.extract_1(meta_data_list_due[:20])
        result.update(result1)
    except:
        result[guonei["xufang"][0]] = []
        result[guonei["gongfang"][0]] = []
        result[guonei["lianxiren1"][0]] = []
        result[guonei["lianxiren2"][0]] = []
        result[guonei["lianxidizhi1"][0]] = []
        result[guonei["lianxidizhi2"][0]] = []
        logger_online.error(u"第一部分抽取出现问题:{0}".format(traceback.format_exc()))

    try:
        result4 = extract_utils.extract_2(meta_data_list_due[:20])
        result.update(result4)
    except:
        result[guonei["sheng"][0]] = []
        result[guonei["xiangmuming"][0]] = []
        result[guonei["hetongpingshenbianhao"][0]] = []
        logger_online.error(u"第二部分抽取出现问题:{0}".format(traceback.format_exc()))

    try:
        result2 = extract_utils.extract_3(meta_data_list_due[:20])
        result.update(result2)
    except:
        result[guonei["xuhao"][0]] = []
        result[guonei["mingcheng"][0]] = []
        result[guonei["xinghao"][0]] = []
        result[guonei["shuliang"][0]] = []
        result[guonei["danjia"][0]] = []
        result[guonei["xiaojijine"][0]] = []
        result[guonei["zongji"][0]] = []
        logger_online.error(u"第三部分抽取出现问题:{0}".format(traceback.format_exc()))


    try:
        result3 = extract_utils.extract_9(meta_data_list_due[len(meta_data_list_due)-20:])
        result.update(result3)
    except:
        result[guonei["xufanggaizhang"][0]] = []
        result[guonei["gongfanggaizhang"][0]] = []
        result[guonei["lianxiren3"][0]] = []
        result[guonei["lianxirengongfang"][0]] = []
        result[guonei["hetongqiandingriqi1"][0]] = []
        result[guonei["hetongqiandingriqi2"][0]] = []
        result[guonei["zhanghumingcheng1"][0]] = []
        result[guonei["zhanghumingcheng2"][0]] = []
        result[guonei["kaihuyinhang1"][0]] = []
        result[guonei["kaihuyinhang2"][0]] = []
        result[guonei["yinhangzhanghu1"][0]] = []
        result[guonei["yinhangzhanghu2"][0]] = []
        result[guonei["shuihao1"][0]] = []
        result[guonei["shuihao2"][0]] = []
        result[guonei["dizhidianhua1"][0]] = []
        result[guonei["dizhidianhua2"][0]] = []
        logger_online.error(u"第九部分抽取出现问题:{0}".format(traceback.format_exc()))


    context.update({"result":result})
    return result






if __name__ == "__main__":
    for i in range(12):
        print("======================{0}======================".format(i+1))
        rich_content = ""
        with open("files/{0}.json".format("e5480f2827104feea261a27514a869ac"), "r", encoding='utf8') as f:
            rich_content = json.loads(f.read())

        pdf2txt_decoder = Pdf2TxtDecoder(rich_content)
        for each in extract_utils.paragraph_delete(pdf2txt_decoder.get_meta_data_list()):
            print(each)
        print("页眉页脚判定")
        extract_utils.get_paragraph_delete(pdf2txt_decoder.get_meta_data_list())


            # if isinstance(each, Table):
            #     for line in each.cells:
            #         for cell in line:
            #             print(cell.text, end="|")
            #         print()
        # result = run({"pdf2txt_decoder": pdf2txt_decoder, "result": {},"doctype":"35"})
        # # print("123")
        # for each in result:
        #
        #     # if each not in [guonei["zongji"][0]]:
        #     #     continue
        #     for key in guonei:
        #         if each == guonei[key][0]:
        #             print(guonei[key][1], end=":")
        #             break
        #     for a in result[each]:
        #         print(a[0], end="||")
        #     print()
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

