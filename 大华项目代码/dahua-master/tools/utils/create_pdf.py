#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/5/7 上午10:02
'''

不知道怎么用reportlab 暂时废弃

'''
import os, sys, re, json, traceback
from reportlab.pdfgen import canvas
from tools.utils.simple_utils import get_file_names_without_type
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.platypus import SimpleDocTemplate,PageBreak
from reportlab.lib.pagesizes import *

pdfmetrics.registerFont(ttfonts.TTFont('song', 'files/simhei.ttf'))

def create_pdf(text, file_path):
    start_x = 100
    start_y = 800
    print_num = 0
    line_length = 45
    c = canvas.Canvas(file_path)
    c.setFont('song', 10)
    c.setLineWidth(500)
    # c.drawString(100, 800, text)
    data = text.split("\n")
    for each_text in data:
        boo = True
        while boo:
            if len(each_text)>45:
                c.drawString(100, 800 - print_num * 15, each_text[:45])
                each_text = each_text[45:]
                print_num += 1
            else:
                c.drawString(100, 800 - print_num * 15, each_text)
                print_num += 1
                boo = False



    c.showPage()
    c.save()

# def myFirstPage(canvas,doc):
#     canvas.saveState()
#     canvas.setFont('song',16)
#     canvas.drawCentredString(111, 111, "1111")
#     canvas.setFont('song',9)
#     canvas.drawString(222,10,u"2222")
#     canvas.restoreState()
# def myLaterPages(canvas, doc):
#     canvas.saveState()
#     canvas.setFont('song', 9)
#     canvas.drawString(33,10,u"333")
#     canvas.restoreState()
#
#
# doc = SimpleDocTemplate("1.pdf", pagesize=A4)
# Story=[]
# for i in range(10):
#     Story.append(PageBreak())
# doc.build(Story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)

if __name__ == "__main__":
    name_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
    folder_name = "/Users/jingjian/datagrand/2019_2/guojianengyuanshenhua/20190506/download_txt"
    for name1 in name_list:
        for name2 in name_list:
            each_folder_name = "{0}/{1}{2}".format(folder_name, name1, name2)
            file_names = get_file_names_without_type(each_folder_name)
            for each_file in file_names:
                file_path = "{0}/{1}".format(each_folder_name, each_file)
                f = open(file_path, "r")
                file_data = f.read()
                f.close()
                pdf_file_path = file_path[:len(file_path)-3] + "pdf"
                print(file_data)
                print(sys.version_info[0] == 3 and not isinstance(file_data, str))
                print(sys.version_info[0])
                print(type(file_data))
                create_pdf(file_data, "1.pdf")
                break
            break
        break
    pass
