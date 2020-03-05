#!/usr/bin/env python
# coding=utf-8
# import fitz
# import pyzbar.pyzbar as pyzbar
import zxing
import time,traceback
from PIL import Image
from tools.utils.simple_utils import get_uuid
# 下载PyMuPDF,Pillow和pyzbar包
from selenium import webdriver
from conf.conf import selenium_host,pdf_show_host
from conf.conf import location_logo
from dahua_log import dhlog
from tools.idps.idps_utils import ocr_png
def convert_pdf_to_png(pdf_uuid):
    """
    :param pdf_file: pdf文件路径
    :param image_store_path: 存储生成图片的路径
    :return: 返回pdf文件最后一张图的地址
    """
    dhlog.info("pdf=>png:{0}".format(pdf_uuid))
    result = True
    try:
        chrome_capabilities = {
            "browserName": "chrome",
            "version": "",
            "platform": "ANY",
            "javascriptEnabled": True,
        }
        browser = webdriver.Remote("{0}/wd/hub".format(selenium_host), desired_capabilities=chrome_capabilities)
        browser.set_window_size(900, 1300)
        browser.get("{0}/pdf/{1}.pdf".format(pdf_show_host,pdf_uuid))
        time.sleep(3)
        browser.get_screenshot_as_file("files/{0}_page.png".format(pdf_uuid))
        browser.quit()
        dhlog.info("success:{0}".format(pdf_uuid))
    except:
        result = False
        dhlog.info("fail:{0},{1}".format(pdf_uuid,traceback.format_exc()))
    return result

def has_most_word(content,word_list,num=0.65):
    """
    判断前者是否含有后者集合中的项中的num以上的比例
    :param content:
    :param word_list:
    :param num:
    :return:
    """
    true_num = 0
    for each in word_list:
        if each in content:
            true_num += 1
    if true_num*1.0 / len(word_list) > num:
        return True
    else:
        return False

import fitz
from PIL import Image
def get_first_image_from_pdf(pdf_uuid):
    def find_logo(file_uuid,location,after_name):
        # after_name = page_0/90/180/270
        # 导致截图会截取  id_page_0    保存成id_logo
        shot_of_png(file_uuid,location, "logo", after_name=after_name)
        shot_of_png(file_uuid, location, after_name.replace("page", "logo"), after_name=after_name)
        content = ocr_png("files/{0}_{1}.png".format(file_uuid, "logo"))
        # content = ocr_png("files/{0}_{1}.png".format(file_uuid, after_name.replace("page", "logo")))
        dhlog.info(content)
        keyword = "浙江大华科技有限公司"
        if has_most_word(content, keyword, num= 0.69):
            return True
        else:
            return False
    def img_rotate(file_uuid, i, true_rotate=False):
        rotate = [Image.ROTATE_90, Image.ROTATE_180, Image.ROTATE_270][i]
        dhlog.info("旋转{0}".format(i*90+90))
        im = Image.open("files/{0}_page.png".format(file_uuid))
        ng = im.transpose(rotate)
        ng.save("files/{0}_page_{1}.png".format(file_uuid,i*90+90))
        if true_rotate:
            ng.save("files/{0}_page.png".format(file_uuid))

    # 首先要将pdf转换成png
    pdf_obj = fitz.open("files/{0}.pdf".format(pdf_uuid))
    if pdf_obj.pageCount == 0:
        dhlog.error("pdf转换失败:{0}".format(pdf_uuid))
        return False
    page1 = pdf_obj[0]
    pix = page1.getPixmap()
    pix.writePNG("files/{0}_page.png".format(pdf_uuid))  # 默认保存成  id_page
    pix.writePNG("files/{0}_page_0.png".format(pdf_uuid))  # 设定非旋转状态  id_page_0
    dhlog.info("pdf=>png转换完成")
    # for循环四个角度 对png进行截图判定
    if find_logo(pdf_uuid, location_logo, "page_0"):
        return True
    for i in range(3):
        rotate = i * 90 + 90
        img_rotate(pdf_uuid, i)
        after_name = "page_{0}".format(rotate)
        if find_logo(pdf_uuid, location_logo, after_name=after_name):
            img_rotate(pdf_uuid, i, true_rotate=True)
            return True
    return True

def shot_of_png(file_uuid,location,type, after_name="page"):
    """
    :param file_uuid: 图片路径
    :param location: 截图位置
    :param type: 后缀名     head  middle foot
    :return:是否出错
    """
    dhlog.info("png=>{0}:{1}".format(type,file_uuid))
    result = True
    try:
        image_path = "files/{0}_{1}.png".format(file_uuid, after_name)
        img = Image.open(image_path)
        width, height = img.size
        left = location["left"]*width
        upper = location["up"]*height
        right = location["right"]*width
        lower = location["down"]*height
        cropped = img.crop((left, upper, right, lower))
        cropped.save("files/{0}_{1}.png".format(file_uuid,type))
        dhlog.info("success:{0}".format(file_uuid))
    except Exception as e:
        result = False
        dhlog.info("fail:{0},{1}".format(file_uuid, traceback.format_exc()))
    return result


def qrcode_parser(file_uuid):
    zx = zxing.BarCodeReader()
    # 图片放大
    img = Image.open("files/{0}_foot.png".format(file_uuid))
    width,height = img.size
    out = img.resize((int(width*2.5),int(height*2.5)),Image.ANTIALIAS)
    out.save("files/{0}_foot_big.png".format(file_uuid))


    zxdata = zx.decode("files/{0}_foot_big.png".format(file_uuid))
    if zxdata:
        dhlog.info("qrcode:{0}【{1}】".format(zxdata.parsed,file_uuid))
        return zxdata.parsed
    else:
        dhlog.info("识别二维码出错:{0},{1}".format(file_uuid,zxdata))
        return False






# shot_image_path = convert_pdf_to_png("/Users/jingjian/datagrand/gitlab/jingjian/MyTools_branch/dahua/MyTools/files/多页.pdf", "/Users/jingjian/datagrand/gitlab/jingjian/MyTools_branch/dahua/MyTools/files")
# shot_path = shot_of_pdfQRcode(shot_image_path, "/Users/jingjian/datagrand/gitlab/jingjian/MyTools_branch/dahua/MyTools/files/shot.png")
# QRcode = extract_QR_from_shot(shot_path)
# print(QRcode)
