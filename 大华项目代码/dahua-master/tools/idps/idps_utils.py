#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/11/28 下午3:02
import os, sys, re, json, traceback, time, requests
from tools.idps.idps_login import request_with_jwt,host
from conf.conf import ocr_host
from dahua_log import dhlog

# 电子件抽取
def extract(type_id,file_path):
    response = json.loads(request_with_jwt(
        url=host + 'extracting/instant',
        method='POST',
        data={'docType': type_id},
        files={'file': open(file_path, 'rb')},
    ).content)
    return response["tag_list"]

# 扫描件抽取
def extract_saomiao(type_id,file_path):
    response = json.loads(request_with_jwt(
        url=host + 'extracting/instant',
        method='POST',
        data={'docType': type_id,"ocr":"true"},
        files={'file': open(file_path, 'rb')},
    ).content)
    return response["tag_list"]


# 扫描件审核任务发起
def check_saomiao(type_id,checkt_id_list,file_path,extra_conf={}):
    '''
    将获取到的扫描件进行IDPS识别，并将识别到的结果组装成需要的格式
    {"extract_info":extract_info,"task_id":task_id}
    国内 标准模板   checkt_id_list:[2]  tag_type_id:30
    :param type_id:  文档类型
    :param checkt_id_list:   审核点列表
    :param file_path:
    :param extra_conf:
    :return:
    '''
    fr = open(file_path, 'rb')
    fileList = {'fileList': fr}
    response = json.loads(request_with_jwt(
        url=host + 'review',
        data={"data": json.dumps({"check_point_id_list": checkt_id_list, "tag_type_id": str(type_id), "doc_form": 2,"extra_conf":extra_conf}),
              "async_task": False},
        files=fileList,
        method='POST').content)
    fr.close()
    # 可以获取扫描件的抽取结果   和   审核详情结果
    print(response)
    extract_info = response["abstract_info"]
    task_id = response["id"]
    return {"extract_info":extract_info,"task_id":task_id}

# 扫描件审核结果查看
def check_info(task_id):
    response = json.loads(request_with_jwt(
        url=host + 'review/{0}'.format(task_id),
        method='GET').content)
    return response

# 扫描件表格抽取任务发起
def table_extract_saomiao(file_path):
    fileList = {'file': open(file_path, 'rb')}
    response = json.loads(request_with_jwt(
        url=host + 'extracting/new/table',
        data={"ocr": 0, "async_task": False, "feature_type_id": 133},
        files=fileList,
        method='POST').content)
    return response

# 扫描件表格抽取结果查看
def table_info_saomiao(table_id):
    response = json.loads(request_with_jwt(
        url=host + 'extracting/table/{0}'.format(table_id),
        method='GET').content)
    return response


def diff(file1_path,file2_path):
    fileList = {('file',open(file1_path,'rb')), ('file',open(file2_path,'rb'))}
    data = {
        "ocr": '[1,0]',
        "async_task": False,
        "feature_type_id": 67,
        "diff_type": 2,
        "diff_rules": json.dumps(["filter_blank", "filter_punc", "filter_header_footer", "filter_other_char"])
    }
    response = json.loads(request_with_jwt(
        url=host + 'diff/instant',
        data=data,
        files=fileList,
        method='POST').content)
    return response
    # return ""


def diff_info(history_id):
    response = json.loads(request_with_jwt(
        url=host + 'diff/history/{0}'.format(history_id),
        method='GET').content)
    return response

def ocr_png(file_path, activate_rotate=False):
    dhlog.info("进行识别:{0}".format(file_path))
    content = ""
    try:
        fr = open(file_path, 'rb')
        json_data = {"activate_rotate": activate_rotate}
        json_str = json.dumps(json_data)
        response = requests.post(
            url='{0}/ysocr/ocr'.format(ocr_host),
            files={'file': fr, "data": json_str}
        )
        fr.close()
        print('{0}/ocr'.format(ocr_host))
        # print(response.text)
        print(json.dumps(json.loads(response.text)))
        content = "".join([each["text_string"] for each in json.loads(response.text)["img_data_list"][0]["text_info"]])
        dhlog.info(content)
    except:
        dhlog.error(traceback.format_exc())
        print(traceback.format_exc())
    return content

def ocr_fapiao(file_path):
    result = None
    try:
        url = '{0}/invoice_extract'.format(ocr_host)
        response = requests.post(
            url=url,
            files={'file': open(file_path, 'rb')},
            data=dict(
                detect_category="invoice",
                file_type="invoice"
            )
            # detect_category="invoice",
            # file_type="invoice"
        )
        print(response.content)
        result = json.loads(response.content)
        # content = "".join([each["text_string"] for each in json.loads(response.text)["img_data_list"][0]["text_info"]])
    except:
        dhlog.error(traceback.format_exc())
    return result



if __name__ == "__main__":

    # a = check_saomiao("30", [2], "/tmp/1.pdf", extra_conf={})
    # print(json.dumps(a,ensure_ascii=False,indent=2))
    # b = check_info(109)
    # print(json.dumps(b,ensure_ascii=False,indent=2))

    a = ocr_png("/tmp/1.png", activate_rotate=False)
    print(a)
    # a = ocr_png("/tmp/1.png", activate_rotate=False)
    # print(a)
    # a= check_info(731)
    # # print()
    # # print(a)
    # print(json.dumps(a,ensure_ascii=False,indent=2))

    # a = diff("/tmp/deploy_idps_dahua/data/check/scripts/table_extract_script/test/12_new.pdf","/tmp/deploy_idps_dahua/data/check/scripts/table_extract_script/test/12_new.pdf")

    # a= diff_info(5)
    # print(a)

    # print(diff("/tmp/a.pdf", "/tmp/b.pdf"))
    # a = ocr_fapiao("/tmp/1.jpg")
    # print(a)
