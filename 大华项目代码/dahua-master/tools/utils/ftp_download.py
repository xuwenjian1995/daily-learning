#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/5/6 上午11:21
import os, sys, re, json, traceback
import tools.utils.simple_utils as su
import ftplib
from conf import conf
host = conf.ftp_host    #'123.56.120.196'
username = conf.ftp_username#'datagrand1'
password = conf.ftp_password#'VNx1gH7w'
port = conf.ftp_port
file = 'crm/contract/F9vS907wNraM87dwC3c1-15QI0OH.pdf'


class MyFTP(ftplib.FTP):
    encoding = "utf-8"
    def __init__(self, host, user, passwd, port):
        ftplib.FTP.__init__(self)
        self.connect(host, port)
        self.login(user, passwd)


    def xxx(self, mulu=''):
        data = list()
        print(mulu)
        next_mulu = self.nlst(mulu)
        for each in next_mulu:
            each_mulu = self.nlst(each)
            if len(each_mulu)==1 and str(each_mulu[0]).endswith(each):
                data.append(su.get_file_name_from_path(each))
            else:
                data.append({su.get_file_name_from_path(each): self.xxx(mulu=each)})
        return data



    def download_file(self, LocalFile, RemoteFile):  # 下载当个文件
        file_handler = open(LocalFile, 'wb')
        print(file_handler)
        # self.ftp.retrbinary("RETR %s" % (RemoteFile), file_handler.write)#接收服务器上文件并写入本地文件
        self.retrbinary('RETR ' + RemoteFile, file_handler.write)
        file_handler.close()
        return True
    #
    # def DownLoadFileTree(self, LocalDir, RemoteDir):  # 下载整个目录下的文件
    #     print("remoteDir:", RemoteDir)
    #     if not os.path.exists(LocalDir):
    #         os.makedirs(LocalDir)
    #     self.ftp.cwd(RemoteDir)
    #     RemoteNames = self.ftp.nlst()
    #     print("RemoteNames", RemoteNames)
    #     for file in RemoteNames:
    #         Local = os.path.join(LocalDir, file)
    #         print(self.ftp.nlst(file))
    #         if file.find(".") == -1:
    #             if not os.path.exists(Local):
    #                 os.makedirs(Local)
    #             self.DownLoadFileTree(Local, file)
    #         else:
    #             self.DownLoadFile(Local, file)
    #     self.ftp.cwd("..")
    #     return
    # def close(self):
    #     self.close()






# f = ftplib.FTP()
# f.connect(host=host, port=port)
# f.login(user=username, passwd=password)
# print(f.dir())
#
# f.quit()


if __name__ == "__main__":
    ftp = MyFTP(host=host,user=username, passwd=password,port=port)
    # ftp.login(user=username, passwd=password)
    # a=ftp.xxx('rensheju')
    ftp.download_file("/tmp/test001.pdf",'crm/contract/F9vS907wNraM87dwC3c1-15QI0OH.pdf')
    ftp.quit()
