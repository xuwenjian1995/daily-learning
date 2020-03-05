#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/5/16 上午10:15
import os, sys, re, json, traceback, time
import pdfkit
import threading
from tools.html_parser.my_parser import MyParser
from tools.utils.simple_utils import get_file_name_from_path,get_file_names,get_uuid

def create_pdf(html_path,pdf_path):
    pdfkit.from_file(html_path, pdf_path)

threading_list = []
threading_list_num = 0
wrong_list = []

def jhtml_to_pdf(file_path, uuid, my_lock):
    try:
        # file_name = get_file_name_from_path(file_path).split(".")[0]
        html_path = file_path.replace(".jhtml", ".html")
        pdf_path = file_path.replace(".jhtml", ".pdf")
        if not os.path.exists(html_path):
            my_parser = MyParser()
            file_data = open(file_path, 'r').read().replace("\n", " ").replace("\t", " ").replace("!DOCTYPE ", "")
            my_parser.feed(file_data)
            data = my_parser.body
            my_parser.merge_body(data)
            my_parser.close()

            my_parser.body.find_html_by_location(
                start_location="html[1]-body[2]-div[2]-div[2]-div[1]-div[1]-div[1]-div[1]-div[1]-h2[1]",
                end_location="html[1]-body[2]-div[2]-div[2]-div[1]-div[1]-div[1]-div[1]-div[3]")
            f = open(html_path, "w")
            f.write(my_parser.body.children[0].get_node_print())
            f.close()
        else:
            print("html文件已存在，无需转换[{0}]".format(uuid))

        if not os.path.exists(pdf_path):
            create_pdf(html_path, pdf_path)
            print("【{0}】转换成功[{1}]".format(file_path,uuid))
        else:
            print("pdf文件已存在，无需转换[{0}]".format(uuid))

    except:
        print("【{0}】转换失败，失败原因:{1}[{0}]".format(file_path, traceback.format_exc(),uuid))
        os.system("rm -rf {0}".format(html_path))
        os.system("rm -rf {0}".format(pdf_path))
        global wrong_list
        wrong_list.append(file_path)


    my_lock.acquire()
    global threading_list_num
    threading_list_num -= 1
    global threading_list
    threading_list.remove(uuid)
    my_lock.release()


class MyThread(threading.Thread):
    def __init__(self, file_path,uuid,my_lock):
        threading.Thread.__init__(self)
        self.file_path = file_path
        self.uuid = uuid
        self.my_lock = my_lock
    def run(self):
        jhtml_to_pdf(self.file_path,self.uuid,self.my_lock)



if __name__ == "__main__":
    # file_path = '/Users/jingjian/datagrand/2019_2/guojianengyuanshenhua/20190515/国电/gggc/1089.jhtml'
    # file_name = get_file_name_from_path(file_path).split(".")[0]
    # my_parser = MyParser()
    # file_data = open(file_path,'r').read().replace("\n", " ").replace("\t", " ").replace("!DOCTYPE ", "")
    # print(file_data)
    # my_parser.feed(file_data)
    # data = my_parser.body
    # my_parser.merge_body(data)
    # my_parser.close()
    # my_parser.body.find_html_by_location(
    #     start_location="html[1]-body[2]-div[2]-div[2]-div[1]-div[1]-div[1]-div[1]-div[1]-h2[1]",
    #     end_location="html[1]-body[2]-div[2]-div[2]-div[1]-div[1]-div[1]-div[1]-div[3]")
    #
    # # print(data.children[0].get_node_print())
    # html_path = "files/{0}_content.html".format(file_name)
    # pdf_path = "files/{0}.pdf".format(file_name)
    # f = open(html_path, "w")
    # f.write(my_parser.body.children[0].get_node_print())
    # f.close()
    # create_pdf(html_path,pdf_path)
    folders = ["/Users/jingjian/datagrand/2019_2/guojianengyuanshenhua/20190515/国电/gggc",
               "/Users/jingjian/datagrand/2019_2/guojianengyuanshenhua/20190515/国电/ggjg",
               "/Users/jingjian/datagrand/2019_2/guojianengyuanshenhua/20190515/国电/ggsb"]

    # jhtml_to_pdf("/Users/jingjian/datagrand/2019_2/guojianengyuanshenhua/20190515/国电/ggjg/1529.jhtml")

    my_lock = threading.Lock()

    for folder_index, each_folder in enumerate(folders):
        file_list = get_file_names(each_folder,"jhtml")
        for file_index, each_file in enumerate(file_list):

            while (threading_list_num>=20):
                time.sleep(1)

            uuid = get_uuid()
            my_lock.acquire()
            threading_list_num += 1
            threading_list.append(uuid)
            my_lock.release()

            # print("{0}/{1}".format(each_folder, each_file))
            print("{0}文件夹,index={1},total={2}".format(each_folder[len(each_folder)-4:], file_index+1, len(file_list)))
            file_path = "{0}/{1}".format(each_folder, each_file)
            # jhtml_to_pdf(file_path)

            t = MyThread(file_path,uuid,my_lock)
            t.start()

    print(end="\n\n\n\n\n")
    print(wrong_list)



# if __name__ == "__main__":
#     jhtml_to_pdf("/Users/jingjian/datagrand/2019_2/guojianengyuanshenhua/20190515/国电/gggc/23177.jhtml", "1",threading.Lock())







