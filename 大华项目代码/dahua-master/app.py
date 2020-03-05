#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/4/23 下午2:20
import os, sys, re, json, traceback, logging
from flask import Flask, request, send_file, render_template, send_from_directory,redirect,url_for
from tools.utils import simple_utils as utils
from flask_restful import Resource,Api
from flask import make_response
import _locale
_locale._getdefaultlocale = (lambda *args:['en_US', 'utf8'])
from dahua_log import dhlog
from flask_sqlalchemy import SQLAlchemy as flask_orm
from conf.conf import SQLALCHEMY_DATABASE_URI

app = Flask(__name__, template_folder="template/", static_folder="conf/")

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = flask_orm(app)

@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
api = Api(app)
@api.representation("text/html")
def out_html(data,code, headers=None):
    resp = make_response(data, code)
    resp.headers.extend(headers or {})
    return resp

# from route.file_type_transform.word2html import Word2Html
from route.dahua.compareIn import CompareIn,DocInShowCheckRedirect,PdfShow, DocInShowDiffRedirect
from route.dahua.compareOut import CompareOut, CompareOutMail
from route.dahua.pdfDealIn import PDFDeal
from route.dahua.docObjectIn import DocInfoIn
from route.dahua.fapiao import Fapiao


# 首页
# @app.route('/', methods=['GET'])
# def extract_html():
#     # dhlog.info("index")
#     conf_file = open("conf/menu.txt", "r")
#     menu_data = conf_file.read().split("\n")
#     conf_file.close()
#     menu_info = []
#     for each in menu_data:
#         # dahua_log.info(each)
#         if not each.startswith("#"):
#             each_menu = each.split(",")
#             if len(each_menu)==4:
#                 menu_info.append(each_menu)
#             elif len(each_menu)==3:
#                 each_menu.append("show_iframe")
#                 menu_info.append(each_menu)
#
#     return render_template("index.html", menu_info = menu_info)

@app.route('/1', methods=['GET'])
def extract_html2():
    return  redirect("http://idps2-zszq.test.datagrand.cn/")

# 资源获取
@app.route('/static/<tool_name>/<file_type>/<file_name>', methods=['GET'])
def static_file(tool_name, file_type, file_name):
    return send_file('template/{0}/{1}/{2}'.format(tool_name, file_type, file_name))

@app.route('/static/js/<path:path>', methods=['GET'])
def js_file(path):
    return send_file('template/js/{0}'.format(path))

@app.route('/static/css/<path:path>', methods=['GET'])
def css_file(path):
    return send_file('template/css/{0}'.format(path))

@app.route('/static/img/<path:path>', methods=['GET'])
def img_file(path):
    return send_file('template/img/{0}'.format(path))

@app.route('/static/images/<path:path>', methods=['GET'])
def images_file(path):
    return send_file('template/img/{0}'.format(path))

@app.route('/static/img_server/<path:path>', methods=['GET'])
def imgserver_file(path):
    if os.path.isfile('template/img_server/{0}'.format(path)):
        return send_file('template/img_server/{0}'.format(path))
    else:
        return "该路径为文件夹路径"

@app.route('/static/fonts/<path:path>', methods=['GET'])
def fonts_file(path):
    return send_file('template/fonts/{0}'.format(path))

@app.route('/static/md/<path:path>', methods=['GET'])
def md_file(path):
    return send_file('template/idps/markdown/{0}'.format(path))

@app.route('/staticfile/<path:path>', methods=['GET'])
def staticfile(path):
    return send_file('template/{0}'.format(path))


@app.route('/markdown/<path:path>', methods=['GET'])
def markdown_show(path):
    # /markdown/idps/markdown/readme.md
    return render_template('markdown_show.html',markdown_file_path = path)

@app.route('/pdf/<path:filename>', methods=['GET'])
def pdf_file(filename):
    # /markdown/idps/markdown/readme.md
    return send_file('files/{0}'.format(filename))


@app.route('/test/markdown', methods=['GET'])
def images_file222():
    return render_template('idps/datahtml/markdown_show.html')


# api.add_resource(Word2Html, '/tools/word2html')
# api.add_resource(CompareInTest, '/dahua/testcomparein')
# api.add_resource(CompareInTest, '/dahua/comporein','/dahua/testcomparein')
api.add_resource(CompareIn, '/dahua/comporein','/dahua/comparein', '/')
api.add_resource(DocInfoIn, '/docinfo')
api.add_resource(DocInShowCheckRedirect, '/dahua/checkin')
api.add_resource(DocInShowDiffRedirect, '/dahua/diffin')
api.add_resource(PdfShow, '/dahua/pdfshow')
api.add_resource(Fapiao, '/dahua/fapiao')
# api.add_resource(ModelIn, '/dahua/modelin')
# api.add_resource(DataRevice, '/dahua/datarevice')




api.add_resource(CompareOut, '/dahua/compareout')
api.add_resource(CompareOutMail, '/dahua/compareoutmail')

api.add_resource(PDFDeal,'/dahua/pdfdeal')



from route.dahua.Test import TestExtract
api.add_resource(TestExtract,'/test/extract')



from tools.utils.template_utils import get_length,length_is_zero

app.add_template_filter(get_length,'length')
app.add_template_filter(length_is_zero,'length_is_zero')








if __name__ == "__main__":
    app.config['JSON_AS_ASCII'] = False
    app.run(port=9999, host="0.0.0.0")
