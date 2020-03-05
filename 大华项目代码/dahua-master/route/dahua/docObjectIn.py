#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/12/23 11:34
import os, sys, re, json, traceback, time
import pymysql, datetime
from tools.utils.simple_utils import get_uuid
from flask_restful import Resource
from flask import request, jsonify, render_template
from conf.conf import MYSQL_DATABASE,MYSQL_HOST,MYSQL_PASSWORD,MYSQL_USER,MYSQL_PORT
from dahua_log import dhlog

class DocIn(object):
    # from_where
    FROM_APP = "1"
    FROM_WEB = "0"
    FROM_MAIL = "2"
    FROM_RECHECK = "3"
    # 标准非标的判定
    DOC_TYPE_STANDARD = "1"
    DOC_TYPE_NOT_STANDARD_1 = "2"
    DOC_TYPE_NOT_STANDARD_N = "3"
    # 文档状态
    START = "流程开始"  # 开始
    CANSHU_OVER = "参数确认完毕"  # 参数确认完毕
    SAVE_FILE_OVER = "文件保存完毕"  # 文件保存完毕
    DOC_CODE_OVER = "文档编号抽取完毕"  # 文档编号抽取完毕
    DOC_INFO_OVER = "文档信息获取完毕"  # 文档信息获取完毕
    STANDARD_CHECKING ="标准审核中"  # 标准审核中
    STANDARD_RESULT_UPLOADING ="标准异步结果上传中"  # 标准异步结果上传中
    STANDARD_OVER = "标准流程结束"  # 标准流程结束
    NOTSTANDARD_FILE_DOWNLOAD = "非标文档下载中"  # 非标文档下载中
    NOTSTANDARD_DIFFINIG = "非标比对中"  # 非标比对中
    NOTSTANDARD_RESULT_UPLOADING ="非标异步结果上传中"  # 非标异步结果上传中
    NOTSTANDARD_OVER = "非标流程结束" # 非标流程结束
    OVER = "其他over"  # 其他over



    def __init__(self, rowid, from_where, user_code, ftp_path, doc_code):
        self.id = get_uuid()
        self.rowid = rowid
        self.from_where = from_where
        self.user_code = user_code
        self.ftp_path = ftp_path
        self.file_name = None
        # self.conn = pymysql.connect(host='10.1.253.53', port=16000, user='root', password='root', database='dahua', charset="utf8")
        self.doc_status = None
        self.kehumingcheng = None
        self.zongjine = None
        self.yewuguishuren = None
        self.wrong_info = None
        self.result = None
        self.status = DocIn.START
        self.create_time = datetime.datetime.now()
        self.standard_type = None
        self.idps_doc_type = None
        self.ftp_path_list = None
        self.doc_code = doc_code



    def update(self, file_name=None, doc_status=None, kehumingcheng=None,
               zongjine=None, yewuguishuren=None, wrong_info=None, return_json=None, status=None,
               standard_type=None, idps_doc_type=None, ftp_path=None, ftp_path_list=None, doc_code=None, **kwargs):
        if file_name is not None:
            self.file_name = file_name
        if doc_status is not None:
            self.doc_status = doc_status
        if kehumingcheng is not None:
                self.kehumingcheng = kehumingcheng
        if zongjine is not None:
                self.zongjine = zongjine
        if yewuguishuren is not None:
                self.yewuguishuren = yewuguishuren
        if wrong_info is not None:
                self.wrong_info = wrong_info
        if standard_type is not None:
                self.standard_type = standard_type
        if idps_doc_type is not None:
                self.idps_doc_type = idps_doc_type
        if ftp_path is not None:
                self.ftp_path = ftp_path
        if ftp_path_list is not None:
                self.ftp_path_list = ftp_path_list
        if isinstance(ftp_path_list, list):
            self.ftp_path_list = json.dumps(ftp_path_list)
        self.result = return_json
        if isinstance(return_json, list) or isinstance(return_json, dict):
            self.result = json.dumps(return_json, ensure_ascii=False, indent=2)
        if status is not None:
            self.status = status
        if doc_code is not None:
            self.doc_code = doc_code

        conn = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD,
                               database=MYSQL_DATABASE, charset="utf8")
        cursor = conn.cursor()

        sql = "UPDATE task_info set file_name=%s, doc_status=%s, " \
              "kehumingcheng=%s, zongjine=%s, yewuguishuren=%s, wrong_info=%s, result=%s, status=%s," \
              " standard_type=%s, idps_doc_type=%s, ftp_path_list=%s, ftp_path=%s, doc_code=%s " \
              "where id=%s;"
        field_values = (self.file_name,
            self.doc_status, self.kehumingcheng, self.zongjine, self.yewuguishuren,
            self.wrong_info, self.result, self.status, self.standard_type,
            self.idps_doc_type, self.ftp_path_list, self.ftp_path,self.doc_code, self.id)

        try:
            result = cursor.execute(sql, field_values)
            conn.commit()
        except:
            dhlog.info("sql语句执行失败")
        finally:
            conn.close()

    def save(self):
        conn = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD,
                               database=MYSQL_DATABASE, charset="utf8")
        cursor = conn.cursor()

        sql = "INSERT INTO `task_info` VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"

        field_values = (self.id, self.rowid, self.from_where, self.user_code, self.file_name,
                                 self.doc_status, self.kehumingcheng, self.zongjine, self.yewuguishuren,
                                 self.wrong_info, self.result, self.status, self.create_time, self.standard_type,
                                 self.idps_doc_type, self.ftp_path_list, self.ftp_path, self.doc_code)
        result = cursor.execute(sql, field_values)

        conn.commit()
        conn.close()

    @staticmethod
    def select_all(rowid=None, from_where=None, doc_code=None, standard_type=None, doc_status=None, num=100):
        conn = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD,
                               database=MYSQL_DATABASE, charset="utf8")
        cursor = conn.cursor()


        add_sql = ""
        if rowid is not None and len(rowid) > 0:
            add_sql += " and rowid like '%" + rowid + "%'"
        if from_where is not None and len(from_where) > 0:
            add_sql += " and from_where='" + from_where + "'"
        if doc_code is not None and len(doc_code) > 0:
            add_sql += " and doc_code like '%" + doc_code + "%'"
        if standard_type is not None and len(standard_type) > 0:
            add_sql += " and standard_type='" + standard_type + "'"
        if doc_status is not None and len(doc_status) > 0:
            add_sql += " and doc_status like '%" + doc_status + "%'"
        sql = "select create_time, rowid, from_where, user_code, file_name, doc_code, doc_status, kehumingcheng,  " \
              "zongjine, yewuguishuren, standard_type, idps_doc_type, ftp_path_list, ftp_path, status, result, id,  " \
              "wrong_info from task_info  where 1=1  {0} order by create_time desc limit 0,{1};".format(add_sql, num)
        # dhlog.info(sql)
        '''
        create_time, 0
        rowid, 1
        from_where, 2
        user_code, 3
        file_name, 4
        doc_code, 5
        doc_status, 6
        kehumingcheng, 7
        "zongjine, 8
        yewuguishuren, 9
        standard_type, 10
        idps_doc_type, 11
        ftp_path_list, 12
        ftp_path, 13
        status, 14
        result  15
        id 16
        wrong_info 17
        '''
        cursor.execute(sql)
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        return result

    @staticmethod
    def select_one(uuid):
        conn = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD,
                               database=MYSQL_DATABASE, charset="utf8")
        cursor = conn.cursor()

        sql = "select * from task_info  where id='{0}'   order by create_time desc limit 0,100;".format(uuid)
        '''
        create_time, 0
        rowid, 1
        from_where, 2
        user_code, 3
        file_name, 4
        doc_code, 5
        doc_status, 6
        kehumingcheng, 7
        "zongjine, 8
        yewuguishuren, 9
        standard_type, 10
        idps_doc_type, 11
        ftp_path_list, 12
        ftp_path, 13
        status, 14
        result  15
        '''
        cursor.execute(sql)
        result = cursor.fetchone()
        conn.commit()
        conn.close()
        return result


class DocInfoIn(Resource):
    def get(self):
        id = request.args.get("id",None)
        if id is None:
            return "id不可为空"
        result = DocIn.select_one(id)
        if result is None:
            return "id查无数据"
        return render_template("doc_info.html", result=result)



if __name__ == "__main__":
    # import datetime
    # print(datetime.datetime.now())
    result = DocIn.select_all(num=10)
    return_result = []
    for each in result:
        each_list = list(each)
        try:
            json_data=each_list[15]
            # print(json_data)
            # url = json.loads(json_data)
            # url = url["result"]["page_url2"]
            pat_1 = "reviewDetail/(\d+)\?doc_"
            a = re.findall(pat_1, json_data)
            each_list.append(re.findall(pat_1, json_data)[0])
            print(each_list[-1])
        except:
            each_list.append("")
            print(traceback.format_exc())
        return_result.append(each_list)
    # return_json = dict(ftp_path="ftp_path", from_where="from_where", rowid="rowid")
    # doc_obj = DocIn(user_code="user_code", doc_code="doc_code",
    #                 **return_json)  # rowid, from_where, user_code, ftp_path, file_name
    # doc_obj.save()

    # from tools.utils.simple_utils import get_uuid
    # a = DocIn("rowid", "from_where", "user_code", "ftp_path")
    # a.save()
    # data = dict(
    #     doc_status="doc_status",
    #     kehumingcheng="kehumingcheng",
    #     zongjine="zongjine",
    #     yewuguishuren="yewuguishuren",
    #     wrong_info="wrong_info",
    #     result={"a":1},
    #     status="status",
    #     standard_type="standard_type",
    #     idps_doc_type="idps_doc_type",
    #     ftp_path="ftp_path",
    #     ftp_path_list=["1", "2"]
    # )
    # a.update(**data)


    pass
