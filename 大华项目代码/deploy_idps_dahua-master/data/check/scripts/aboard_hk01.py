#!/usr/bin/env python
# coding=utf-8
# author:chenxianglong@datagrand.com
# datetime:2019/12/16 19.00
# 审核hk01模板的内容

from pdf2txt_decoder.pdf2txt_decoder import Pdf2TxtDecoder
from table_extract_script.aboard_hk01 import run as extract
import json
import os
import difflib
import re
try:
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    from ..driver import logger_processor as logger
except:
    class LoggerClass(object):
        @staticmethod
        def info(message):
            print(message)

    logger = LoggerClass()

is_debug = 1
# 包括cell的(text, context_list)
DEFAULT_FORMAT_EXTRACT_RESULT = (None, list())  # 从extract_result中获取默认的结果


def debug_save_file(context):
    meta_context = dict(
        extra_conf=context.get("extra_conf", dict()),
        rich_content=context.get("rich_content", dict()),
        file_uuid=context.get("extra_conf", dict()).get("file_uuid", "tmp")
    )
    if is_debug:
        file_path = "/root/contract_check_online/check/app/scripts/files/{}.json".format(meta_context["file_uuid"])
        logger.info("保存文件：{}".format(file_path))
        with open(file_path, "w") as fw:
            fw.write(json.dumps(meta_context))


def debug_load_file():
    if is_debug:
        file_path = os.path.dirname(__file__) + "/tmp.json"
        # file_path = os.path.dirname(__file__) + "/c5.pdf.json"
        with open(file_path, "r") as fr:
            return json.loads(fr.read())


def debug_extra_conf():
    if is_debug:
        return dict(
            template_dict=dict(),
            post_data=dict()
        )


# 生成差异html文件
def value_diff_html(value1, value2):
    value1 = value1 or ""
    value2 = value2 or ""
    pat_ignore = u"[,，\.。\(\)（）:：；;\"“”’‘\'、\s]"
    diff_obj = difflib.Differ()
    diff_result = list(diff_obj.compare(value1, value2))
    diff_html = u""
    last_flag = u" "
    for each in diff_result:
        if len(re.sub(pat_ignore, "", each[2])) == 0 and each[0]!=" ":
            if each[0] == "-":
                diff_html += each[2]
            continue

        if each[0] == last_flag:
            diff_html += each[2]

        if each[0] == "-" and last_flag == "+":
            diff_html += u')</span><span class="red">{0}'.format(each[2])
        # - 空
        if each[0] == "-" and last_flag == " ":
            diff_html += u'<span class="red">{0}'.format(each[2])
        # + -
        if each[0] == "+" and last_flag == "-":
            diff_html += u'</span><span class="green">({0}'.format(each[2])
        # + 空
        if each[0] == "+" and last_flag == " ":
            diff_html += u'<span class="green">({0}'.format(each[2])
        # 空 +
        if each[0] == " " and last_flag == "+":
            diff_html += u')</span>{0}'.format(each[2])
        # 空 -
        if each[0] == " " and last_flag == "-":
            diff_html += u'</span>{0}'.format(each[2])
        last_flag = each[0]
    if last_flag == "-":
        diff_html += u'</span>'
    elif last_flag == "+":
        diff_html += u')</span>'
    return diff_html


# 生成审核项内容
def gen_audit_item(audit_suggestion="", audit_desc="", audit_tips="",
                   audit_rule_type="", helpfulness=1, audit_rule="", context=list()):
    '''
    :param audit_suggestion: # 建议
    :param audit_desc: # 描述
    :param audit_tips:
    :param audit_rule_type:  # 审核类型
    :param helpfulness:  # 1 通过  2不通过
    :param audit_rule:
    :param context:
    :return:
    '''
    audit_suggestion = audit_suggestion or ""
    return dict(
        audit_suggestion=audit_suggestion,  # 处理后返回接口调用的字段名是 suggestion
        audit_desc=audit_desc,
        audit_tips=audit_tips,
        audit_rule_type=audit_rule_type,
        helpfulness=helpfulness,
        audit_rule=audit_rule,
        context=context,
        related_law="",  # 第一项的内容中用作返回抽取结果的字段
    )


# 格式化抽取结果为dict
def format_extract_result(extract_info):
    """传进来的是json字符串，重新格式化"""
    format_result = dict(
        item_groups=list()
    )
    item_groups = dict()
    for extract_tag_list in extract_info.values():
        for _, _, context_list, tag_name, group_key in extract_tag_list:
            context_list = [dict(text=text, offset=offset) for text, _, offset in context_list]
            context_text = " ".join([each.get("text", "") for each in context_list])
            if tag_name.startswith("item_"):
                if group_key not in item_groups:
                    item_groups[group_key] = dict()
                item_groups[group_key].update({
                    tag_name: (context_text, context_list)
                })
            else:
                format_result[tag_name] = (context_text, context_list)

    format_result["item_groups"] = list(item_groups.values())
    return format_result


# 比较字符串是否相等
def cmp_str_func(str1, str2):
    str1, str2 = str(str1), str(str2)
    if str1 == str2:
        return True
    if not str1 or not str2:
        return False

    if str1.strip() == str2.strip():
        return True
    else:
        return False


# 校对必要条款(A.合同头信息)
def audit_necessary_terms(extract_result, post_data):
    '''
    :param extract_result:  抽取结果
    :param post_data: 上传结果
    :return: 校验结果列表
    '''
    audit_result = list()
    audit_rule_type = "必要条款"
    audit_rule = "necessaryTermsHeadList"
    keys_list = list()  # [(extract_key, post_key, display_key)]
    # 1. 业务主体
    keys_list.append(("entityName", "DHBusinessEntryName", "Unit entry"))
    # 2. 客户名称
    keys_list.append(("customerName", "DHAccount", "Account Name"))
    # 3. 贸易方式
    keys_list.append(("tradeMethod", "DHTradeType", "Trade Method"))
    # 4. 收货客户
    keys_list.append(("consignee", "DHConsigneeAccountName", "Consignee"))
    # 5. 买方
    keys_list.append(("buyerLTD", "BuyerLTD", "Buyer"))
    # 6. 卖方
    keys_list.append(("sellerLTD", "SellerLTD", "Seller"))
    # 7. total Amount
    # keys_list.append(("totalAmount", "", "Amount"))  # todo 买方和卖方没有对应的json字段
    # 8. amount excl. tax
    # keys_list.append(("amountExclTax", "", "Amount Excl. Tax"))
    # 9. amount incl. tax
    # keys_list.append(("amountInclTax", "", "Amount Incl. Tax"))

    for extract_key, post_key, display_key in keys_list:
        extract_val, extract_context_list = extract_result.get(extract_key, DEFAULT_FORMAT_EXTRACT_RESULT)
        post_val = post_data.get(post_key)

        if cmp_str_func(extract_val, post_val):
            title = display_key + "一致"
            helpfulness = 1
        else:
            title = display_key + "不一致"
            helpfulness = 2

        audit_item = gen_audit_item(audit_rule=audit_rule,
                                    audit_rule_type=audit_rule_type,
                                    audit_desc=display_key,
                                    helpfulness=helpfulness,
                                    audit_suggestion=post_val,
                                    audit_tips=title,
                                    context=extract_context_list,
                                    )

        additional_info = dict(
            compare_type=1,   # 1代表和外部数据比较了，2代表没有和外部数据比较
            content=[extract_val] if extract_val else list(),     # content放置在additional_info附带回来
            diff=value_diff_html(extract_val, post_val)
        )
        audit_item["references"] = json.dumps(additional_info, ensure_ascii=False)
        audit_result.append(audit_item)

    return audit_result


# 校对非必要条款(B.合同头信息)
def audit_unnecessary_terms_b(extract_result, post_data):
    '''
    :param extract_result:  抽取结果
    :param post_data: 上传结果
    :return: 校验结果列表
    '''
    audit_result = list()
    audit_rule_type = "非必要条款"
    audit_rule = "checkList"
    keys_list = list()  # [(extract_key, post_key, display_key)]
    # 1. 签约日期
    keys_list.append(("signDate", "DHSignDate", "Sign date"))
    # 2. 客户地址
    keys_list.append(("entityAddress", "DHAccountAdd", "Account address"))
    # 3. 客户PO
    keys_list.append(("purchaserPO", "CustomerPO", "Customer PO"))
    # 4. 付款条件
    keys_list.append(("paymentTerms", "DHPaymentCondition", "Payment Terms"))
    # 5. 收货地址
    keys_list.append(("shippingAddress", "DHConsigneeAccountAdd", "Shipping Address"))
    # 6. Discount
    keys_list.append(("discount", "Discount", "Discount"))
    # 7. Voucher
    keys_list.append(("voucherDiscount", "VoucherNoTax", "Voucher"))

    for extract_key, post_key, display_key in keys_list:
        extract_val, extract_context_list = extract_result.get(extract_key, DEFAULT_FORMAT_EXTRACT_RESULT)
        post_val = post_data.get(post_key)

        if cmp_str_func(extract_val, post_val):
            title = display_key + "一致"
            helpfulness = 1
        else:
            title = display_key + "不一致"
            helpfulness = 2

        audit_item = gen_audit_item(audit_rule=audit_rule,
                                    audit_rule_type=audit_rule_type,
                                    audit_desc=display_key,
                                    helpfulness=helpfulness,
                                    audit_suggestion=post_val,
                                    audit_tips=title,
                                    context=extract_context_list,
                                    )
        additional_info = dict(
            compare_type=1,  # 1代表和外部数据比较了，2代表没有和外部数据比较
            content=[extract_val] if extract_val else list(),  # content放置在additional_info附带回来
            diff=value_diff_html(extract_val, post_val)
        )
        audit_item["references"] = json.dumps(additional_info, ensure_ascii=False)
        audit_result.append(audit_item)

    return audit_result


# 校对非必要条款(C.合同产品行信息)
def audit_unnecessary_terms_c(extract_result, post_data):
    '''
    :param extract_result:  抽取结果
    :param post_data: 上传结果
    :return: 校验结果列表
    '''
    audit_result = list()
    audit_rule_type = "合同产品行信息"
    audit_rule = "notNecessaryTermsRowList"

    keys_list = list()  # [(extract_key, post_key, display_key)]
    # 1. Dahua Model
    keys_list.append(("item_innerModel", "DHInmodel", "Dahua Model"))
    # 2. Quantity
    keys_list.append(("item_quantity", "QuantityReuestd", "Quantity"))
    # 3. Output model(Customer Model)
    keys_list.append(("item_outerModel", "DHOutModel", "Output Model"))
    # 4. Unit Price excl. Tax(Currency)
    keys_list.append(("item_unitPriceExclTax", "DHOSOriginalNoTaxPrice", "Unit Price"))
    # 5. Unit Price with % discount excl.Tax(Currency)
    keys_list.append(("item_unitPriceExclTaxDicount", "DHOSNoTaxPrice", "Unit Price With Discount Excl"))
    # 6. Amount
    keys_list.append(("item_amountExclTax", "TotalAmount", "Amount"))

    # 使用Dahua Model作为主键来对比
    extract_primary_key, post_primary_key = "item_innerModel", "DHInmodel"
    # 处理后的抽取结果，处理后crm中数据
    deal_extract_result, deal_post_data = dict(), dict()
    # 处理后的抽取结果是由[dict(lineNo=xxx, xxx=xxx)] -> dict($item_enuPingName=dict(lineNo=xxx, xxx=xxx))
    for extract_item_group in extract_result["item_groups"]:
        primary_key, _ = extract_item_group.get(extract_primary_key, DEFAULT_FORMAT_EXTRACT_RESULT)
        if primary_key:
            deal_extract_result[primary_key] = extract_item_group
    # 处理后的crm结果是由[dict(DHPinName=xxx, xxx=xxx)] -> dict($DHPinName=dict(DHPinName=xxx, xxx=xxx))
    for post_item_data in post_data["itemList"]:
        primary_key = post_item_data.get(post_primary_key)
        if primary_key:
            deal_post_data[primary_key] = post_item_data
    # 只在扫描件中的keys
    not_in_crm_keys = set(deal_extract_result.keys()) - set(deal_post_data.keys())
    # 只在crm中的keys
    not_in_sc_keys = set(deal_post_data.keys()) - set(deal_extract_result.keys())
    # 公共key
    common_keys = set(deal_extract_result.keys()) & (set(deal_post_data.keys()))
    # 新增类型
    for primary_key in not_in_crm_keys:
        extract_dict = deal_extract_result[primary_key]
        content_list = list()
        l_keys_list = list()
        total_extract_context_list = list()
        for extract_key, (extract_val, extract_context_list) in extract_dict.items():
            if extract_val:
                l_keys_list.append(extract_key)
                content_list.append(extract_val)
                total_extract_context_list.extend(extract_context_list)
        audit_item = gen_audit_item(audit_rule=audit_rule,
                                    audit_rule_type=audit_rule_type,
                                    audit_desc=primary_key,
                                    helpfulness=2,
                                    audit_suggestion="",
                                    audit_tips="crm不存在该数据",
                                    context=total_extract_context_list
                                    )
        additional_info = dict(
            type="新增",
            key_list=l_keys_list,
            compare_type=1,
            content=content_list,  # content放置在additional_info附带回来
        )
        # 添加l_key_list与content_list对应关系，加入到additional_info中返回
        for key, val in zip(l_keys_list, content_list):
            additional_info.update({
                key: val
            })

        audit_item["references"] = json.dumps(additional_info, ensure_ascii=False)   # 后端需要根据这个处理
        audit_result.append(audit_item)

    # 遗漏类型
    for primary_key in not_in_sc_keys:
        post_dict = deal_post_data[primary_key]
        # 传入crm中的数据
        audit_suggestion = json.dumps(post_dict, ensure_ascii=False)
        audit_item = gen_audit_item(audit_rule=audit_rule,
                                    audit_rule_type=audit_rule_type,
                                    audit_desc=primary_key,
                                    helpfulness=2,
                                    audit_suggestion=audit_suggestion,
                                    audit_tips="sc不存在该数据",
                                    context=list(),
                                    )
        additional_info = dict(
            type="遗漏",
            compare_type=1,
            content=list(),  # content放置在additional_info附带回来
        )
        audit_item["references"] = json.dumps(additional_info, ensure_ascii=False)  # 后端需要根据这个处理
        audit_result.append(audit_item)

    # 修改类型
    for primary_key in common_keys:
        post_dict = deal_post_data[primary_key]
        extract_dict = deal_extract_result[primary_key]
        not_same_list = list()
        for extract_key, post_key, display_key in keys_list:
            extract_val, extract_context_list = extract_dict.get(extract_key, DEFAULT_FORMAT_EXTRACT_RESULT)
            post_val = post_dict.get(post_key)
            # 值不一样
            if not cmp_str_func(extract_val, post_val):
                not_same_list.append((extract_key, extract_val, extract_context_list, post_key, post_val))

        content_list = list()  # 用于返回数据的content_list
        l_keys_list = list()
        total_extract_context_list = list()  # 用于前端展示的context_list
        audit_suggestion = json.dumps(post_dict, ensure_ascii=False) # 传入json数据
        for extract_key, (extract_val, extract_context_list) in extract_dict.items():
            if extract_val:
                l_keys_list.append(extract_key)
                content_list.append(extract_val)
                total_extract_context_list.extend(extract_context_list)

        if len(not_same_list) == 0:
            helpfulness = 1
            audit_tips = "crm与sc中数据一致"
            additional_info = dict(
                type="通过",
                key_list=l_keys_list,
                compare_type=1,
                content=content_list,  # content放置在additional_info附带回来
            )
        else:
            helpfulness = 2
            audit_tips = "crm与sc中数据不一致"
            additional_info = dict(
                type="修改",
                key_list=l_keys_list,
                compare_type=1,
                content=content_list,  # content放置在additional_info附带回来
            )

        audit_item = gen_audit_item(audit_rule=audit_rule,
                                    audit_rule_type=audit_rule_type,
                                    audit_desc=primary_key,
                                    helpfulness=helpfulness,
                                    audit_suggestion=audit_suggestion,
                                    audit_tips=audit_tips,
                                    context=total_extract_context_list,
                                    )
        # 添加l_key_list与content_list对应关系，加入到additional_info中返回
        for key, val in zip(l_keys_list, content_list):
            additional_info.update({
                key: val
            })
        audit_item["references"] = json.dumps(additional_info, ensure_ascii=False)  # 后端需要根据这个处理
        audit_result.append(audit_item)

    return audit_result


# 校对条款7-15
def audit_fixed_terms(extract_result, template_dict):
    '''
    :param extract_result:  抽取结果
    :param template_dict: 上传模板结果
    :return: 校验结果列表
    '''
    audit_result = list()
    audit_rule_type = "非必要条款"
    audit_rule = "notNecessaryTermsList"

    keys_list = list()  # [(extract_key, template_key, display_key)]
    # 7. Tax
    keys_list.append(("Tax", "Tax", "Tax"))
    # 8. Warranty
    keys_list.append(("Warranty", "Warranty", "Warranty"))
    # 9. Claim
    keys_list.append(("Claim", "Claim", "Claim"))
    # 10. Export Compliance
    keys_list.append(("Export_Compliance", "Export Compliance", "Export Compliance"))
    # 11. Force Majeure
    keys_list.append(("Force_Majeure", "Force Majeure", "Force Majeure"))
    # 12. Applicable Laws and Arbitration
    keys_list.append(("Applicable_Laws_And_Arbitration", "Applicable Laws and Arbitration", "Applicable Laws and Arbitration"))
    # 13. Special Conditions
    keys_list.append(("Special_Conditions", "Special Conditions", "Special Conditions"))
    # 14. Counterparts
    keys_list.append(("Counterparts", "Counterparts", "Counterparts"))
    # 15. Export Clearance
    keys_list.append(("Export_Clearance", "Export Clearance", "Export Clearance"))

    for extract_key, template_key, display_key in keys_list:
        extract_val, extract_context_list = extract_result.get(extract_key, DEFAULT_FORMAT_EXTRACT_RESULT)
        template_val = template_dict.get(template_key)

        if cmp_str_func(extract_val, template_val):
            title = display_key + "一致"
            tip = "与模板数据一致"
            helpfulness = 1
        else:
            title = display_key + "不一致"
            tip = "与模板数据不一致"
            helpfulness = 2

        audit_item = gen_audit_item(audit_rule=audit_rule,
                                    audit_rule_type=audit_rule_type,
                                    audit_desc=display_key,
                                    helpfulness=helpfulness,
                                    audit_suggestion=template_val,
                                    audit_tips=tip,
                                    context=extract_context_list,
                                    )
        additional_info = dict(
            compare_type=2,  # 1代表和外部数据比较了，2代表没有和外部数据比较
            content=[extract_val] if extract_val else list(),  # content放置在additional_info附带回来
            diff=value_diff_html(extract_val, template_val)
        )
        audit_item["references"] = json.dumps(additional_info, ensure_ascii=False)
        audit_result.append(audit_item)

    return audit_result


def trans_to_float(float_str):
    try:
        return float("%.2f" % float(float_str))
    except:
        logger.info("trans_to_float err:{}".format(float_str))
        return 0


# 校对产品行公式数据（四舍五入，取两位小数）
def audit_formula_terms(extract_result):
    '''
    :param extract_result:  抽取结果
    :return: 校验结果列表
    '''
    audit_result = list()

    discount, _ = extract_result.get("discount", DEFAULT_FORMAT_EXTRACT_RESULT)
    voucherDiscount, _ = extract_result.get("voucherDiscount", DEFAULT_FORMAT_EXTRACT_RESULT)
    vat, _ = extract_result.get("vat", DEFAULT_FORMAT_EXTRACT_RESULT)
    amountExclTax, _ = extract_result.get("amountExclTax", DEFAULT_FORMAT_EXTRACT_RESULT)
    amountInclTax, _ = extract_result.get("amountInclTax", DEFAULT_FORMAT_EXTRACT_RESULT)
    totalAmount, _ = extract_result.get("totalAmount", DEFAULT_FORMAT_EXTRACT_RESULT)

    # 转换成小数
    discount = trans_to_float(discount)
    voucherDiscount = trans_to_float(voucherDiscount)
    vat = trans_to_float(vat)
    amountExclTax = trans_to_float(amountExclTax)
    amountInclTax = trans_to_float(amountInclTax)
    totalAmount = trans_to_float(totalAmount)

    lin_sum_amount = 0
    # 总金额相关的context列表
    amount_context_list = list()
    # 每行数据进行公式校验
    audit_rule_type = "必要条款"
    audit_rule = "necessaryTermsHeadList"
    # unitPriceExclTaxDiscount * quantity 等于 amountExclTax
    # 或
    # unitPriceExclTax * quantity 等于 amountExclTax
    for extract_item_group in extract_result["item_groups"]:

        line_no, _ = extract_item_group.get("item_lineNumber", DEFAULT_FORMAT_EXTRACT_RESULT)
        line_amount, _ = extract_item_group.get("item_amountExclTax", DEFAULT_FORMAT_EXTRACT_RESULT)
        quantity, _ = extract_item_group.get("item_quantity", DEFAULT_FORMAT_EXTRACT_RESULT)
        unitPriceExclTax, _ = extract_item_group.get("item_unitPriceExclTax", DEFAULT_FORMAT_EXTRACT_RESULT)
        unitPriceExclTaxDicount, _ = extract_item_group.get("item_unitPriceExclTaxDicount", DEFAULT_FORMAT_EXTRACT_RESULT)

        line_amount = trans_to_float(line_amount)
        quantity = trans_to_float(quantity)
        unitPriceExclTax = trans_to_float(unitPriceExclTax)
        unitPriceExclTaxDicount = trans_to_float(unitPriceExclTaxDicount)

        if trans_to_float(line_amount):
            lin_sum_amount += line_amount
            text, context_list = extract_item_group.get("item_amountExclTax", DEFAULT_FORMAT_EXTRACT_RESULT)
            amount_context_list.extend(context_list)

        context = list()
        if unitPriceExclTaxDicount and line_amount and quantity:
            if trans_to_float(unitPriceExclTaxDicount * quantity) == line_amount:
                title = "{0}行公式校验：unitPriceExclTaxDiscount * quantity 等于 amountExclTax".format(line_no)
                helpfulness = 1
            else:
                title = "{0}行公式校验：unitPriceExclTaxDiscount * quantity 不等于 amountExclTax".format(line_no)
                helpfulness = 2
            suggestion = "{0}".format(trans_to_float(unitPriceExclTaxDicount * quantity))
            for key in ["item_unitPriceExclTaxDicount", "item_quantity", "item_amountExclTax"]:
                text, context_list = extract_item_group.get(key, DEFAULT_FORMAT_EXTRACT_RESULT)
                context.extend(context_list)

        elif unitPriceExclTax and line_amount and quantity:
            if trans_to_float(unitPriceExclTax * quantity) == line_amount:
                title = "{0}行公式校验：unitPriceExclTax * quantity 等于 amountExclTax".format(line_no)
                helpfulness = 1
            else:
                title = "{0}行公式校验：unitPriceExclTax * quantity 不等于 amountExclTax".format(line_no)
                helpfulness = 2
            suggestion = "{0}".format(trans_to_float(unitPriceExclTax * quantity))
            for key in ["item_unitPriceExclTax", "item_quantity", "item_amountExclTax"]:
                text, context_list = extract_item_group.get(key, DEFAULT_FORMAT_EXTRACT_RESULT)
                context.extend(context_list)
        else:
            title = "{0}行公式校验缺少必要数据".format(line_no)
            helpfulness = 2
            suggestion = ""
            for key in ["item_unitPriceExclTaxDicount", "item_unitPriceExclTax", "item_quantity", "item_amountExclTax"]:
                text, context_list = extract_item_group.get(key, DEFAULT_FORMAT_EXTRACT_RESULT)
                if text:
                    context.extend(context_list)

        audit_item = gen_audit_item(audit_rule=audit_rule,
                                    audit_rule_type=audit_rule_type,
                                    audit_desc=title,
                                    helpfulness=helpfulness,
                                    audit_suggestion=suggestion,
                                    audit_tips=title,
                                    context=context,
                                    )
        additional_info = dict(
            compare_type=2,  # 1代表和外部数据比较了，2代表没有和外部数据比较
            content=[each["text"] for each in context],  # content放置在additional_info附带回来
        )
        audit_item["references"] = json.dumps(additional_info, ensure_ascii=False)
        audit_result.append(audit_item)

    # 总金额进行公式校验
    audit_rule_type = "单元行公式-必要条款"
    audit_rule = "necessaryTermsRowList"
    # lin_sum_amount - (discount) - (voucherDiscount) == totalAmount
    if discount and voucherDiscount and lin_sum_amount and totalAmount:
        if trans_to_float(lin_sum_amount - discount - voucherDiscount ) == totalAmount:
            title = "公式校验：lin_sum_amount - discount - voucherDiscount 等于 totalAmount"
            helpfulness = 1
        else:
            title = "公式校验：lin_sum_amount - discount - voucherDiscount 不等于 totalAmount"
            helpfulness = 2
        suggestion = "{0}".format(trans_to_float(lin_sum_amount - discount - voucherDiscount))
        for key in ["discount", "voucherDiscount", "totalAmount"]:
            text, extract_context_list = extract_result.get(key, DEFAULT_FORMAT_EXTRACT_RESULT)
            amount_context_list.extend(extract_context_list)

    elif discount and lin_sum_amount and totalAmount:
        if trans_to_float(lin_sum_amount - discount) == totalAmount:
            title = "公式校验：lin_sum_amount - discount 等于 totalAmount"
            helpfulness = 1
        else:
            title = "公式校验：lin_sum_amount - discount 不等于 totalAmount"
            helpfulness = 2
        suggestion = "{0}".format(trans_to_float(lin_sum_amount - discount))
        for key in ["discount", "totalAmount"]:
            text, extract_context_list = extract_result.get(key, DEFAULT_FORMAT_EXTRACT_RESULT)
            amount_context_list.extend(extract_context_list)

    elif voucherDiscount and lin_sum_amount and totalAmount:
        if trans_to_float(lin_sum_amount - voucherDiscount) == totalAmount:
            title = "公式校验：lin_sum_amount - voucherDiscount 等于 totalAmount"
            helpfulness = 1
        else:
            title = "公式校验：lin_sum_amount - voucherDiscount 不等于 totalAmount"
            helpfulness = 2
        suggestion = "{0}".format(trans_to_float(lin_sum_amount - voucherDiscount))
        for key in ["voucherDiscount", "totalAmount"]:
            text, extract_context_list = extract_result.get(key, DEFAULT_FORMAT_EXTRACT_RESULT)
            amount_context_list.extend(extract_context_list)

    elif lin_sum_amount and totalAmount:
        if lin_sum_amount == totalAmount:
            title = "公式校验：lin_sum_amount 等于 totalAmount"
            helpfulness = 1
        else:
            title = "公式校验：lin_sum_amount 不等于 totalAmount"
            helpfulness = 2

        suggestion = "{0}".format(lin_sum_amount)
        for key in ["totalAmount"]:
            text, extract_context_list = extract_result.get(key, DEFAULT_FORMAT_EXTRACT_RESULT)
            amount_context_list.extend(extract_context_list)
    else:
        title = "公式校验缺少必要数据"
        helpfulness = 2
        suggestion = ""
        for key in ["discount", "voucherDiscount", "totalAmount"]:
            text, extract_context_list = extract_result.get(key, DEFAULT_FORMAT_EXTRACT_RESULT)
            amount_context_list.extend(extract_context_list)

    audit_item = gen_audit_item(audit_rule=audit_rule,
                                audit_rule_type=audit_rule_type,
                                audit_desc="Amount",  # 修改显示
                                helpfulness=helpfulness,
                                audit_suggestion=suggestion,
                                audit_tips=title,
                                context=amount_context_list,
                                )
    additional_info = dict(
        compare_type=2,  # 1代表和外部数据比较了，2代表没有和外部数据比较
        content=[each["text"] for each in amount_context_list], # content放置在additional_info附带回来
    )
    audit_item["references"] = json.dumps(additional_info, ensure_ascii=False)
    audit_result.append(audit_item)

    # amount excl tax + vat == amount incl tax
    if amountInclTax and amountExclTax and vat:
        if trans_to_float(amountExclTax + vat) == amountInclTax:
            title = "公式校验：amountExclTax + vat 等于 amountInclTax"
            helpfulness = 1
        else:
            title = "公式校验：amountExclTax + vat 不等于 amountInclTax"
            helpfulness = 2
        suggestion = "{0}".format(trans_to_float(amountExclTax + vat))
        context = list()
        for key in ["amountExclTax", "vat", "amountInclTax"]:
            text, extract_context_list = extract_result.get(key, DEFAULT_FORMAT_EXTRACT_RESULT)
            context.extend(extract_context_list)
        audit_item = gen_audit_item(audit_rule=audit_rule,
                                    audit_rule_type=audit_rule_type,
                                    audit_desc="Amount Incl. Tax",
                                    helpfulness=helpfulness,
                                    audit_suggestion=suggestion,
                                    audit_tips=title,
                                    context=context,
                                    )
        additional_info = dict(
            compare_type=2,  # 1代表和外部数据比较了，2代表没有和外部数据比较
            content=[each["text"] for each in context],  # content放置在additional_info附带回来
        )
        audit_item["references"] = json.dumps(additional_info, ensure_ascii=False)
        audit_result.append(audit_item)

    # the buyer == customerName
    # the seller = entity
    keys_list = [("buyerLTD", "customerName"),
                 ("sellerLTD", "entityName")]

    for key1, key2 in keys_list:
        val1, extract_context_list1 = extract_result.get(key1, DEFAULT_FORMAT_EXTRACT_RESULT)
        val2, extract_context_list2 = extract_result.get(key2, DEFAULT_FORMAT_EXTRACT_RESULT)
        if cmp_str_func(val1, val2):
            # title = "{0}与{1}一致".format(key1, key2)
            title = key1
            helpfulness = 1
        else:
            # title = "{0}与{1}不一致".format(key1, key2)
            title = key1
            helpfulness = 2

        context = list()
        if val1:
            context.extend(extract_context_list1)
        if val2:
            context.extend(extract_context_list2)

        audit_item = gen_audit_item(audit_rule=audit_rule,
                                    audit_rule_type=audit_rule_type,
                                    audit_desc=title,
                                    helpfulness=helpfulness,
                                    audit_suggestion=val1,
                                    audit_tips=title,
                                    context=context,
                                    )
        additional_info = dict(
            compare_type=2,  # 1代表和外部数据比较了，2代表没有和外部数据比较
            content=[each["text"] for each in context],  # content放置在additional_info附带回来
            diff=value_diff_html(val1, val2)
        )
        audit_item["references"] = json.dumps(additional_info, ensure_ascii=False)
        audit_result.append(audit_item)

    return audit_result


def run(context):
    if context["tag_type_name"] not in [u"国外合同"]:
        return None
    # 保存上传的json数据
    debug_save_file(context)
    extra_conf = context.get('extra_conf') or debug_extra_conf()
    template_dict = extra_conf.get("template_dict", dict())
    post_data = extra_conf.get("post_data", dict())
    pdf2txt_decoder = Pdf2TxtDecoder(context["rich_content"])
    # 抽取结果
    extract_result = extract(dict(pdf2txt_decoder=pdf2txt_decoder, result=dict()))
    extract_result_str = json.dumps(extract_result, ensure_ascii=False)
    # 审核结果
    extract_result = format_extract_result(extract_result)

    audit_items = list()
    if post_data:
        # 必要条款审核
        audit_items.extend(audit_necessary_terms(extract_result, post_data))
        audit_items.extend(audit_unnecessary_terms_b(extract_result, post_data))
    if audit_items:
        audit_items[0]["related_law"] = extract_result_str
        audit_items.extend(audit_unnecessary_terms_c(extract_result, post_data))

    audit_items.extend(audit_fixed_terms(extract_result, template_dict))
    audit_items.extend(audit_formula_terms(extract_result))
    # 使用第一个审核结果内容将抽取结果返回
    logger.info(json.dumps(audit_items, ensure_ascii=False))

    context.update({"audit_items": audit_items})


if __name__ == "__main__":
    meta_context = debug_load_file()
    meta_context.update(dict(tag_type_name=u"国外合同"))
    run(meta_context)
