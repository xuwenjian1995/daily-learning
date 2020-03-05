#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/12/6 21:09
import os, sys, re, json, traceback, time
from pdf2txt_decoder.pdf2txt_decoder import Pdf2TxtDecoder
from jingjian import run
from field_conf import guonei

if __name__ == "__main__":
    # print("======================{0}======================".format(i + 1))
    rich_content = ""
    with open("test/{0}.json".format(9), "r", encoding='utf8') as f:
        rich_content = json.loads(f.read())

    pdf2txt_decoder = Pdf2TxtDecoder(rich_content)
    # --------------------
    for each in pdf2txt_decoder.get_meta_data_list():
        print(each)
        print(each.mapper)
    # --------------------------
    # result = run({"pdf2txt_decoder": pdf2txt_decoder, "result": {}})
    # # print(json.dumps(result,indent=2,ensure_ascii=False))
    # for each in result:
    #     if each in ["index", "due"]:
    #         continue
    #     for key in guonei:
    #         if each == guonei[key][0]:
    #             print(guonei[key][1], end=":")
    #             break
    #     for a in result[each]:
    #         print(a[0], end="||")
    #     print()
