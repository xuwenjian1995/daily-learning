#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/4/23 下午3:50
import os, sys, re, json, traceback

# 大华文档详细信息获取
# dahua_host = "http://10.1.1.191:8080/dahuacrm/crm/appInterface/queryContractInfoSecure.do"
dahua_host = "http://appservicetest.dahuatech.com/crm/api/ocr/contract/queryContractInfoSecure"

# 大华接口URL:
# 使用文件模板代码去获取模板信息（海外1）
# DH_GET_TEMPLATE_XLS_URL = "http://oemsc.dahua-salescloud.testms.com/contractTemplate/getDownloadFile"
DH_GET_TEMPLATE_XLS_URL = "http://apioemsc.dahuatech.com/oem/contractTemplate/getDownloadFile"

# 海外接口URL:
# 校对结果保存接口（保存审核结果，海外2）
# DH_ABOARD_REPORT_CHECK_RESULT_URL = "http://oemsc.dahua-salescloud.testms.com/contractocr/saveOCRResult"
DH_ABOARD_REPORT_CHECK_RESULT_URL = "http://oem.dahua-salescloud-dahua-salescloud.testms.com/oem/contractocr/saveOCRResult"


# 海外接口URL:
# 登录用户名
# 登录URL
DH_REPORT_LOGIN_URL = "http://10.1.1.191:8080/dahuacrm/sso/slogin.do"
DH_REPORT_LOGIN_UID = "17656"  # todo 修改登录uid

DH_OEM_LOGIN_URL = "http://10.1.248.198:8001/oem/dologin"

# 海外接口URL:
# 新建AI草稿合同（海外3）
DH_ABOARD_REPORT_EXTRACT_RESULT_URL = "http://10.1.1.191:8080/dahuacrm/contract/ocr/createAiDraftContract.do"

# 海外接口URL:
# 合同查询接口（海外4）
DH_ABOARD_GET_CONTRACT_DETAIL_URL = "http://10.1.1.191:8080/dahuacrm/contract/ocr/queryOverSeaContract.do"

# 海外接口URL:
# 上传草稿合同附件（海外5）
DH_ABOARD_UPLOAD_ATTACH_URL = "http://10.1.1.191:8080/dahuacrm/contract/ocr/uploadAiDraftContractAttachment.do"

# 国内异步 数据提交接口地址
# dahua_in_dataupload = "http://10.1.253.53:9999/dahua/datarevice"
dahua_in_dataupload = "http://appservicetest.dahuatech.com/crm/api/ocr/contract/ocrAgreeUpdate"

# 从大华ftp下载文件
ftp_host = '10.1.1.191'
ftp_username = 'ftpuser'
ftp_password = 'Uiop&890'
ftp_port = 21
ftp_path = "/home/ftpuser"

# 大华模块使用的mysql
MYSQL_HOST = "mysql"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_DATABASE = "dahua"
MYSQL_PORT = 3306
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@mysql:3306/dahua'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@10.1.253.53:16000/dahua'  # todo for test container

# 调用idps接口
idps_host = "http://10.1.253.53:15000/api/"
idps_username = "admin123"
idps_password = "abcd@123!"
idps_show_host = "http://10.1.253.53:15555"

DAHUA_SHOW_CHECK_IN_URL = "http://10.1.253.53:9999/dahua/checkin?{0}"
DAHUA_SHOW_DIFF_IN_URL = "http://10.1.253.53:9999/dahua/diffin?{0}"
IDPS_SHOW_CHECK_IN_URL = "http://10.1.253.53:15555/#/review/show/reviewDetail/{0}?doc_form=2"
IDPS_SHOW_DIFF_IN_URL = "http://10.1.253.53:15555/#/diff/ocr/show/diffDetail/{0}"

# 二维码截图位置
location_foot = {"left":0.7,"right":0.95,"up":0.85,"down":1}
# 页眉文档编号截图位置
location_head = {"left":0.5,"right":1,"up":0.05,"down":0.2}
# 正文文档编号截图位置
location_middle = {"left":0,"right":1,"up":0.25,"down":0.45}
# logo截图位置
location_logo = {"left":0,"right":0.5,"up":0,"down":0.2}

# 海外文档编码地址
LOCATION_ABOARD_JUDGE = dict(left=0, right=1, up=0, down=0.2)
LOCATION_ABOARD_HEAD = dict(left=0, right=1, up=0, down=0.2)
LOCATION_ABOARD_TOP_RIGHT = dict(left=0, right=1, up=0, down=0.3)

# ocr地址
# ocr_host = "http://10.1.40.13:51401"
ocr_host = "https://ocr.dahuatech.com"

# selenium地址   基于idps进行访问
selenium_host = "http://10.1.253.53:4444"

# 访问pdf的地址   基于selenium进行访问
pdf_show_host = "http://10.1.253.53:9999"

# 审核配置
TAG_TYPE_IN_DICT = {
    "1":{
        "type_id":"35",
        "check_id_list":[4]
    },
    "other":{
        "type_id":"30",
        "check_id_list":[2]
    }
}

# 审核地址重定向加密用
DOC_IN_CHECK_REDIECT_KEY = "klnuoih&YyvJBh8ggKHJbigk"

TAG_TYPE_ABOARD_DICT = dict(
    HK01=dict(
        type_id=33,
        check_id_list=[3]
    ),
    DEFAULT=dict(
        type_id=33,
        check_id_list=[3]
    )
)

CMP_TERM_ITEM_TEMPLATE = dict(
                        title="",
                        result="",
                        tip="",
                        suggestion="",
                        content=list(),
                        diff="",
                    )


doc_guonei_tag_type_id = ""
doc_guonei_checkpoint_list = []

latest_model_name = "test_model"

# 加密密钥
des3_key = "XB5DZaVmZ1HpSUtsAJ1vTH6yE1c1dHd0"

FILES_DIR = os.path.dirname(__file__) + "/../files/"

if __name__ == "__main__":
    pass
