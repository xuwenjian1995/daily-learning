#!/usr/bin/env python
# coding=utf-8
# author:chenxianglong@datagrand.com
# datetime:2020/1/8 下午21.18

from sqlalchemy import text
from sqlalchemy.dialects.mysql import INTEGER, TEXT, MEDIUMTEXT, VARCHAR, DATETIME
from app import db
import datetime


# 海外执行状态对象Orm
class AbroadStatusModel(db.Model):
    __tablename__ = 'abroad_status'
    __tablename_zh__ = '海外执行进程表'

    id = db.Column(INTEGER, primary_key=True, doc="主键ID")
    uuid = db.Column(VARCHAR(256), doc="uuid")
    mail = db.Column(VARCHAR(256), doc="mail")
    userid = db.Column(VARCHAR(256), doc="userid")
    param_no = db.Column(VARCHAR(256), doc="param_no")
    process_status = db.Column(TEXT, doc="流程状态")
    error_info = db.Column(TEXT, doc="错误信息")
    request_time = db.Column(DATETIME, doc="请求时间")
    origin = db.Column(VARCHAR(256), doc="请求来源")
    save_file_name = db.Column(VARCHAR(256), doc="保存文件名")
    screenshot_extract_info = db.Column(TEXT, doc="截图抽取信息")
    crm_data = db.Column(TEXT, doc="crm中获取到的数据")
    extract_info = db.Column(MEDIUMTEXT, doc="抽取获取到的数据")
    review_info = db.Column(MEDIUMTEXT, doc="审核获取到的数据")
    report_review_info = db.Column(MEDIUMTEXT, doc="上报审核的数据")
    report_extract_info = db.Column(MEDIUMTEXT, doc="上报抽取的数据")
    return_info = db.Column(MEDIUMTEXT, doc="接口返回信息数据")
    addition_info = db.Column(MEDIUMTEXT, doc="附加信息")
    create_time = db.Column(
        DATETIME, nullable=False, server_default=text('CURRENT_TIMESTAMP'), doc="创建时间")
    last_update_time = db.Column(
        DATETIME,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), doc="最新更改时间")

    def __init__(self,
                 uuid,
                 mail="",
                 userid="",
                 param_no="",
                 process_status="",
                 error_info="",
                 request_time="",
                 origin="",
                 save_file_name="",
                 screenshot_extract_info="",
                 crm_data="",
                 extract_info="",
                 review_info="",
                 return_info="",
                 addition_info=""):
        self.uuid = uuid
        self.mail = mail
        self.userid = userid
        self.param_no = param_no
        self.process_status = process_status
        self.error_info = error_info
        self.request_time = request_time
        self.origin = origin
        self.save_file_name = save_file_name
        self.screenshot_extract_info = screenshot_extract_info
        self.crm_data = crm_data
        self.extract_info = extract_info
        self.review_info = review_info
        self.return_info = return_info
        self.addition_info = addition_info
        self.create_time = datetime.datetime.now()



