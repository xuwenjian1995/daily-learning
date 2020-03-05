#!/usr/bin/env python
# coding=utf-8
# author:chenxianglong@datagrand.com
# datetime:2019/12/18 下午2.30
from conf import conf
from dahua_log import dhlog
from tools.utils.simple_utils import time_func, crop_image, rotate_image
from tools.idps import idps_utils
import json
import os
import re
from PIL import Image


def rotation_cmp_func(match_text, display_text):
    if match_text in display_text:
        return True

    return False 


@time_func
def get_img_rotation(img_path, location, match_text, cmp_func=rotation_cmp_func):
    '''
    首先查看图片是否旋转，矫正后通过OCR获取特定区域的信息，进行判断是否存在特定的信息，并返回矫正度数
    :param img: 图片
    :param location: 位置信息
    :param match_text: 需要匹配的字符串
    :return: 返回旋转度数, 并将img_path的图片替换成旋转后的图片（如果旋转度大于0的情况下）
    '''
    crop_path = "/tmp/crop.png"
    rotation_list = [0, 90, 180, 270]
    try:
        img = Image.open(img_path)
    except:
        dhlog.error("Image open failed: {0}".format(img_path))
        return 0

    for rotation in rotation_list:
        try:
            img_ro = img
            if rotation > 0:
                img_ro = img.rotate(rotation, expand=True)
            width, height = img_ro.size
            cropped = img_ro.crop((location["left"] * width,
                                   location["up"] * height,
                                   location["right"] * width,
                                   location["down"] * height))
            cropped.save(crop_path)
            """请求OCR接口，获取识别到的数据"""
            ocr_info = idps_utils.ocr_png(crop_path)
            dhlog.info("ocr识别到的结果为:{0}".format(ocr_info))
            if cmp_func(match_text, ocr_info):  # 判断需要匹配的字符是否存在提取到的信息中
                if rotation > 0:
                    img_ro.save(img_path)  # 保存旋转好的图片
                return rotation
        except Exception as e:
            dhlog.error("旋转图片ocr识别失败Exception e: {0}".format(e))
            continue

    return 0


# ocr抽取出第一张图片
def orc_extract_img(file_path):
    output_dir = "/tmp/tmp"
    status = os.system("pdfimages -l 1 -j {0} {1}".format(file_path, output_dir))
    if status != 0:
        dhlog.error("执行pdfimages命令失败")
        return None

    return output_dir + "-000.jpg"


# ocr识别location的信息
@time_func
def ocr_location(image_path, location):
    """
    截取图片的特定位置并通过OCR识别获取图片中的数据
    """
    crop_path = "/tmp/crop.png"
    crop_succ = crop_image(image_path, crop_path, location)
    if not crop_succ:
        dhlog.error("截图失败")
        return None

    try:
        ocr_code = idps_utils.ocr_png(crop_path)
        print(ocr_code)
        dhlog.info("ocr识别到的结果为:{0}".format(ocr_code))
        return ocr_code
    except:
        dhlog.error("ocr识别失败")
        return None


def extract_t_code(save_file_path, with_no_and_po=False):
    # 返回值： template_code, busiEntity
    # with_no_and_po=true时 template_code, busiEntity, no, po
    # 默认值为"", 非None
    first_img_path = orc_extract_img(save_file_path)
    """若没有转换成功就根据状态返回不同的数据"""
    if not first_img_path:
        if with_no_and_po:
            return "", "", "", ""
        else:
            return "", ""
    """说明转换成功，继续向下执行"""
    def cmp_func(match_str_list, display_text):
        display_text = display_text.replace(" ", "")
        for match_str in match_str_list:
            if match_str in display_text:
                return True
        return False

    """
    图片若有旋转，保存调整过后的图片
    get_img_rotation中有判断获取OCR识别结果，为何不将结果返回，以减少OCR识别次数
    """
    rotation = get_img_rotation(first_img_path, conf.LOCATION_ABOARD_JUDGE,
                                ["HK01", "HK02", "DAHUA TECHNOLOGY(HK) LIMITED"],
                                cmp_func=cmp_func)
    if rotation > 0:
        dhlog.info("rotation is {0}".format(rotation))

    """OCR识别特定区域的图片信息"""
    t_code = ocr_location(first_img_path, conf.LOCATION_ABOARD_HEAD)
    template_code, busiEntity = "", ""
    if t_code:
        try:
            template_code = t_code.split("DAHUA")[0]
            busiEntity = "DAHUA" + t_code.split("LIMITED")[0].split("DAHUA")[1] + "LIMITED"
        except Exception as e:
            pass
    if with_no_and_po:
        """需要编号No和Po的情况下追加这两个数据并返回"""
        t_no, t_po = "", ""
        # OCR识别信息
        t_r = ocr_location(first_img_path, conf.LOCATION_ABOARD_TOP_RIGHT)
        if t_r:
            t_r = t_r.replace(u"：", u":").replace(" ", "")
            match_list = re.findall(u"No:?([\w\s\-]+)Add", t_r)
            if len(match_list) > 0:
                t_no = match_list[0]
            match_list = re.findall(u"CustomerPO:?([\w\s\-]+)Date", t_r)
            if len(match_list) > 0:
                t_po = match_list[0]
        return template_code, busiEntity, t_no, t_po
    else:
        return template_code, busiEntity


# 格式化审核结果返回数据
def format_audit_term(term, rule_type):
    # 结果
    result = "不通过"
    if term["helpfulness"] == 1:
        result = "通过"
    tip = term["audit_tips"]
    title = term["audit_desc"]

    additional_info = dict()
    if term["references"]:
        additional_info = json.loads(term["references"])

    suggestion = term["suggestion"]
    # context = json.loads(term["context"])
    # content = [each["text"] for each in context]

    ret_dict = dict(
        title=title,
        result=result,
        tip=tip,
        suggestion=suggestion,
        # content=content,  # context意义改变，content放置在additional_info附带回来
        diff="",
    )

    ret_dict.update(additional_info)
    return ret_dict


# 大华接口2：上报审核结果结构体改造
def gen_report_review_info(review_info_list, uuid, origin, no, addition_data):
    # 获取规则验证结果
    def get_term_list(review_info, rule_type):
        filter_term_list = [each for each in review_info if each.get("audit_rule") == rule_type]
        return [format_audit_term(term, rule_type) for term in filter_term_list]

    report_info_list = list()
    for task_id, review_info in review_info_list:
        if task_id == -1:  # 任务失败，直接返回状态码等信息
            report_info_list.append(dict(
                message="审核信息失败",
                status=400,
            ))
            continue

        necessary_terms_head_list = get_term_list(review_info, "necessaryTermsHeadList")
        necessary_terms_row_list = get_term_list(review_info, "necessaryTermsRowList")
        not_necessary_terms_list = get_term_list(review_info, "notNecessaryTermsList")
        not_necessary_terms_row_list = get_term_list(review_info, "notNecessaryTermsRowList")
        check_list = get_term_list(review_info, "checkList")
        # 判断结果是否通过
        check_result = "通过"

        # 校验【绝对校验】及【公式校验】的结果
        necessary_list = necessary_terms_head_list + necessary_terms_row_list
        if len(necessary_list) == 0:
            check_result = "不通过"

        for each in necessary_list:
            if each.get("result") == "不通过":
                check_result = "不通过"
                break

        # 校验message
        check_msg_list = list()
        audit_config = [
            (necessary_terms_head_list, "绝对校验:"),
            (necessary_terms_row_list, "产品行公式校验:"),
            (not_necessary_terms_row_list, "产品清单明细校验:"),
            (not_necessary_terms_list, "条款校验:"),
            (check_list, "相对校验:")
        ]
        num_list = list()
        for term_list, prefix in audit_config:
            succ_term_list = [each for each in term_list if each.get("result") == "通过"]
            num_list.append(len(succ_term_list))
            if term_list:
                check_msg_list.append("{0}通过{1}/{2}".format(prefix, len(succ_term_list), len(term_list)))

        page_url = "{0}/#/review/show/reviewDetail/{1}?doc_form=2".format(conf.idps_show_host, task_id)
        report_info = dict(
            # scene_type=addition_data.get("scene_type", ""),
            # currency=addition_data.get("currency", ""),
            # template_code=addition_data.get("template_code", ""),
            addition_data=addition_data,
            status=200,
            flag="success",
            doc_code=no,
            rowid=uuid,
            wrong_info="",
            result=dict(
                type=1,
                page_url=page_url,
                result=check_result,
                message=", ".join(check_msg_list),
                num_list=num_list,
                detail=dict(
                    necessaryTermsHeadList=necessary_terms_head_list,
                    necessaryTermsRowList=necessary_terms_row_list,
                    notNecessaryTermsList=not_necessary_terms_list,
                    checkList=check_list
                )
            )
        )
        report_info["from"] = origin  # 0web 1邮箱
        report_info_list.append(report_info)

    return report_info_list


# 大华接口3：上报抽取结果结构体改造
def gen_extract_info(extract_key_info, template_code):
    '''
    :param extract_key_info: 审核接口返回的数据，{
        tag_id: [[
        cell.text,
        1,
        [
            [cell.text[last_idx:],
            1,
            cell.mapper[last_idx]
            ]
        ], 前端分组展示内容
        tag_name,
        group_key,  # 分组group_key
        ]]
    }
    :return:
    '''
    report_info = dict(
        aiAgreementNum=template_code,
        modelList=list(),
    )
    item_groups = dict()
    for extract_tag_list in extract_key_info.values():
        for text, _, _, tag_name, group_key in extract_tag_list:
            # 条款项抽取内容不上报
            if tag_name[0].isupper():
                continue
            elif tag_name.startswith("item_"):
                if group_key not in item_groups:
                    item_groups[group_key] = dict()
                item_groups[group_key].update({
                    tag_name: text
                })
            else:
                report_info[tag_name] = text

    # 处理currency
    unit_price_key = report_info.get("unitPriceKey")
    if unit_price_key:
        tmp_str = unit_price_key.replace(u"（", u"(").replace(u"）", u")")
        if u"(" in tmp_str and u")" in tmp_str:
            report_info["currency"] = tmp_str.split(u")")[0].split(u"(")[1]
        elif "UnitPrice" in unit_price_key.strip().replace(" ", ""):
            report_info["currency"] = unit_price_key.strip().replace(" ", "").replace("UnitPrice", "")

    # 处理表中行数据
    for line_dict in item_groups.values():
        report_line_dict = dict()
        for key, val in line_dict.items():
            filter_key = key.replace("item_", "")
            report_line_dict[filter_key] = val

        report_info["modelList"].append(report_line_dict)

    return report_info




