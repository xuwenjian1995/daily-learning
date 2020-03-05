#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/12/7 10:52
import os, sys, re, json, traceback, time
from pdf2txt_decoder.pdf2txt_decoder import Pdf2TxtDecoder
from jingjian import run
from field_conf import guonei
from document_beans.table import Table
import extract_utils

if __name__ == "__main__":
    for i in range(12):
        # i = 6
        print('--------{0}---------'.format(i+1))
        rich_content = ""
        with open("test_pdf_new_pdf2txt/{0}.json".format(i+1), "r", encoding='utf8') as f:
            rich_content = json.loads(f.read())

        pdf2txt_decoder = Pdf2TxtDecoder(rich_content)
        for each in extract_utils.paragraph_delete(pdf2txt_decoder.get_meta_data_list()):
            if isinstance(each,Table):
                for line in each.cells:
                    print("||".join([cell.text for cell in line]))
            else:
                print(each)


        # break
        # extract_utils.paragraph_merge(pdf2txt_decoder.get_meta_data_list())
    # for each in pdf2txt_decoder.get_meta_data_list():
    #     if isinstance(each,Table):
    #         continue
    #     print(each)
    #     print(len(each.text))
    #     print(each.chars)
    #     print(len(each.chars))
