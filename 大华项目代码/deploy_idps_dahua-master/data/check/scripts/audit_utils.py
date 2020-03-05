#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/12/8 12:05
import os, sys, re, json, traceback, time,difflib

from table_extract_script.field_conf  import guonei
# from field_conf import guonei
audit_item_example = {
    "audit_suggestion": "1",
    "audit_desc": "2",
    "audit_tips": "3",
    "audit_rule_type": u"建议完善问题",
    "helpfulness": 1,    # 1 通过  2不通过
    "audit_rule":"",
    "context":[
        # {
        #     "text":"xxxxx",
        #     "offset":123
        # }
    ]
}

# 验证非空  返回list
def audit_not_null(extract_result,name_list,title_list,audit_rule="not_necessary",audit_rule_type=u"建议完善问题"):
    result = []
    for index,each in enumerate(name_list):
        target = extract_result[guonei[each][0]]
        audit_item = {
            "audit_suggestion": u"该项内容不可为空",
            "audit_desc": title_list[index],
            "audit_tips": u"非空检查",
            "audit_rule_type": audit_rule_type,
            "helpfulness": 1,  # 1 通过  2不通过
            "audit_rule": audit_rule,
            "context": []
        }
        if len(target)>0:
            context = [{"text":each[0],"offset":each[2]} for each in target]
            audit_item["context"] = context
            result.append(audit_item)
        else:
            audit_item["helpfulness"] = 2
            result.append(audit_item)
    return result

# 验证非空  返回单个审核点
def audit_not_null_each(target,name,value,pat,audit_rule = u"check",audit_rule_type=u"检查项条款"):
    audit_item = {
        "audit_suggestion": u"该项内容不可为空",
        "audit_desc": name,
        "audit_tips": u"非空检查",
        "audit_rule_type": audit_rule_type,
        "helpfulness": 1,  # 1 通过  2不通过
        "audit_rule": audit_rule,
        "context": []
    }
    if len(target)>0:
        context = [{"text":each[0],"offset":each[2]} for each in target]
        audit_item["context"] = context
    else:
        audit_item["helpfulness"] = 2
    return audit_item


# 验证正确 返回单个审核结果   一模一样
def audit_true_value(target,name,value,pat,audit_rule=u"necessary_head",audit_rule_type=u"必改问题"):
    '''
    # 验证正确 返回单个审核结果  一模一样
    # 检查单个值和目标是否一致
    :param target: 目标的抽取结果  参考抽取的单个结果的返回样式  [[value,per,index],...]
    :param name:  比对的对象的名称
    :param value:  正确答案
    :param pat: 经过怎样的正则去除后进行比较
    :param audit_rule: 条款分组用
    :param audit_rule_type:  页面展示用
    :return:

    '''
    audit_item = {
        "audit_suggestion": value,
        "audit_desc": name,
        "audit_tips": u"与一站式数据不一致",
        "audit_rule_type": audit_rule_type,
        "helpfulness": 1,  # 1 通过  2不通过
        "audit_rule": audit_rule,
        "context": []
    }
    if len(target) > 0:
        target.sort(key=lambda each: each[2])
        # 组合好抽取的值
        extract_target = u"".join([each[0] for each in target])
        # 将抽取结果转换成审核展示形式
        audit_item["context"] = [{"text": each[0], "offset": each[2]} for each in target]
        # 正则去除指定匹配符号再比较
        vaule1 = delete_chr(extract_target, pat)
        value2 = delete_chr(value, pat)
        if vaule1 == value2:
            audit_item["audit_tips"] = u"与一站式数据一致"
            audit_item["helpfulness"] = 1
        else:
            audit_item["audit_tips"] = u"与一站式数据不一致"
            audit_item["helpfulness"] = 2
    else: # 啥也没抽出来
        audit_item["helpfulness"] = 2
        audit_item["audit_tips"] = u"未识别到目标"
    return audit_item

def audit_true_text(target,name,value,pat=u"[,，\.。\(\)（）:：；;\"“”’‘\'、\s]",audit_rule="not_necessary",audit_rule_type="建议完善问题"):
    '''
    # 验证正确 返回单个审核结果  互相包含   主要为了忽略编号的问题
    # 检查单个值和目标是否相似
    :param target: 目标的抽取结果  参考抽取的单个结果的返回样式  [[value,per,index],...]
    :param name:  比对的对象的名称
    :param value:  正确答案
    :param pat: 经过怎样的正则去除后进行比较
    :param audit_rule: 条款分组用
    :param audit_rule_type:  页面展示用
    :return:
    '''
    def value_diff_html(value1, value2):

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


            if each[0] == last_falg:
                # print(each[2], end='')
                diff_html += each[2]
            # - +


            if each[0] == "-" and last_falg == "+":
                # print(')</span><span class="red">{0}'.format(each[2]), end='')
                diff_html += u')</span><span class="red">{0}'.format(each[2])
            # - 空
            if each[0] == "-" and last_falg == " ":
                # print('<span class="red">{0}'.format(each[2]), end='')
                diff_html += u'<span class="red">{0}'.format(each[2])
            # + -
            if each[0] == "+" and last_falg == "-":
                # print('</span><span class="green">({0}'.format(each[2]), end='')
                diff_html += u'</span><span class="green">({0}'.format(each[2])
            # + 空
            if each[0] == "+" and last_falg == " ":
                # print('<span class="red">{0}'.format(each[2]), end='')
                diff_html += u'<span class="green">({0}'.format(each[2])
            # 空 +
            if each[0] == " " and last_falg == "+":
                # print(')</span>{0}'.format(each[2]), end='')
                diff_html += u')</span>{0}'.format(each[2])
            # 空 -
            if each[0] == " " and last_falg == "-":
                # print('</span>{0}'.format(each[2]), end='')
                diff_html += u'</span>{0}'.format(each[2])
            last_falg = each[0]
        if last_falg == "-":
            diff_html += u'</span>'
        elif last_falg == "+":
            diff_html += u')</span>'
        return diff_html
    audit_item = {
        "audit_suggestion": value,
        "audit_desc": name,
        "audit_tips": u"与一站式数据不一致",
        "audit_rule_type": audit_rule_type,
        "helpfulness": 1,  # 1 通过  2不通过
        "audit_rule": audit_rule,
        "context": []
    }
    if len(target) > 0:
        target.sort(key=lambda each: each[2])
        # 获取到抽取的值，组合起来
        extract_target = u"".join([each[0] for each in target])
        # 将抽取的结果统一成审核用的战士结果
        audit_item["context"] = [{"text": each[0], "offset": each[2]} for each in target]
        # 对两个结果进行特殊符号去除
        value1 = delete_chr(extract_target, pat)  # 可能含有序号
        value2 = delete_chr(value, pat)   # 标准值
        value1_after_replace = value1.replace(u"原告方", u"供方").replace(u"原告", u"供方")#.replace(u"甲", u"供")
        value2_after_replace = value2.replace(u"被告方", u"需方").replace(u"被告", u"需方")#.replace(u"乙", u"需")
        value1_after_re = re.sub(u"\d/\d", u"", value1_after_replace)
        value2_after_re = re.sub(u"\d/\d", u"", value2_after_replace)
        if ((value1_after_re in value2_after_re and len(value1_after_re) > 0)
            or (value2_after_re in value1_after_re and len(value2_after_re)>0)) \
                and abs(len(value1) - len(value2)) < 5:
            audit_item["audit_tips"] = u"与一站式数据一致"
            audit_item["helpfulness"] = 1
            audit_item["question"] = ""
            audit_item["audit_sample"] = u"条款比对通过"
        else:
            audit_item["audit_tips"] = u"与一站式数据不一致"
            audit_item["helpfulness"] = 2
            # audit_item["question"] = value_diff_html(value1,value2)
            audit_item["audit_sample"] = value_diff_html(extract_target, value)
            # audit_item["references"] = value_diff_html(value1, value2)
            # audit_item["related_law"] = value_diff_html(value1, value2)
    else:
        audit_item["helpfulness"] = 2
        audit_item["audit_tips"] = u"未识别到目标"
        audit_item["audit_sample"] = u"条款缺失"
    return audit_item


# 根据抽取结果返回正确的文本
def get_text_by_index(extract_reslut, pat=u"[\s_,，]"):
    extract_reslut.sort(key=lambda each:each[2])
    text = u"".join([each[0] for each in extract_reslut])
    text = re.sub(pat,u"",text)
    return text

# 格式化每条商品
def format_good(each):
    if each["xinghao"]==None or each["xinghao"]=="None" or each["xinghao"] == "null":
        each["xinghao"] =""
    value = each["mingcheng"] + each["xinghao"] + each["shuliang"] + u"{0}{1}".format(
            float(each["danjia"].replace(",", "")), float(each["xiaojijine"].replace(",", "")))
    return value


def delete_chr(content,pat=u"[_\s]"):
    content = re.sub(pat,'',content)
    return content

def audit_1(extract_result,value_xufang,value_gongfang):
    '''
    第一部分   需方和供方
    :return:    necessary_head
    '''
    result = []
    name_list = [u"xufang",u"gongfang"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    # 需方
    xufang = extract_result[guonei[name_list[0]][0]]
    audit_item = audit_true_value(xufang, u"需方", value_xufang, u"[_\s\(\)（）]",audit_rule="necessary_head",audit_rule_type =u"必要条款")
    result.append(audit_item)
    # 需方
    gongfang = extract_result[guonei[name_list[1]][0]]
    audit_item = audit_true_value(gongfang, u"供方", value_gongfang, u"[_\s\(\)（）]",audit_rule="necessary_head",audit_rule_type =u"必要条款")
    result.append(audit_item)
    return result

def audit_2(extract_result,value_dianhua1,value_dianhua2):
    '''
    第二部分   两个电话
    :param meta_data_list:
    :return:    check
    '''
    name_list = [u"dianhua1", u"dianhua2"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    result = []
    # 电话1
    dianhua1 = extract_result[guonei[name_list[0]][0]]
    audit_item = audit_not_null_each(dianhua1, u"电话1", value_dianhua1, u"[_\s]", audit_rule="check" ,audit_rule_type =u"检查项条款")
    result.append(audit_item)
    # 电话2
    dianhua2 = extract_result[guonei[name_list[1]][0]]
    audit_item = audit_not_null_each(dianhua2, u"电话2", value_dianhua2, u"[_\s]", audit_rule="check",audit_rule_type =u"检查项条款")
    result.append(audit_item)
    return result

def audit_3(extract_result):
    '''
    第三部分   两个传真
    :param meta_data_list:
    :return:
    '''
    return []

def audit_4(extract_result,value_lianxiren1,value_lianxiren2):
    '''
    第四部分   两个联系人
    :param meta_data_list:
    :return:    check
    '''
    name_list= [u"lianxiren1",u"lianxiren2"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    result = []
    # 联系人1
    lianxiren1 = extract_result[guonei[name_list[0]][0]]
    audit_item = audit_not_null_each(lianxiren1, u"联系人1", value_lianxiren1, u"[_\s\.]", audit_rule="check",audit_rule_type =u"检查项条款")
    result.append(audit_item)
    # 联系人2
    lianxiren2 = extract_result[guonei[name_list[1]][0]]
    audit_item = audit_not_null_each(lianxiren2, u"联系人2", value_lianxiren2, u"[_\s\.]", audit_rule="check",audit_rule_type =u"检查项条款")
    result.append(audit_item)
    return result

def audit_5(extract_result,value_lianxidizhi1,value_lianxidizhi2):
    '''
    第五部分   两个联系地址
    :param meta_data_list:
    :return:    check
    '''
    name_list= [u"lianxidizhi1",u"lianxidizhi2"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    result = []
    # 联系地址1
    lianxidizhi1 = extract_result[guonei[name_list[0]][0]]
    audit_item = audit_not_null_each(lianxidizhi1, u"联系地址1", value_lianxidizhi1, u"[_\s]", audit_rule="check",audit_rule_type =u"检查项条款")
    result.append(audit_item)
    # 联系地址2
    lianxidizhi2 = extract_result[guonei[name_list[1]][0]]
    audit_item = audit_not_null_each(lianxidizhi2, u"联系地址2", value_lianxidizhi2, u"[_\s]", audit_rule="check",audit_rule_type =u"检查项条款")
    result.append(audit_item)
    return result

def audit_6(extract_result,value_sheng,value_xiangmuming,value_hetongpingshenbianhao):
    '''
    第六部分   一段话
    :param meta_data_list:
    :return:  necessary_head   check   check
    '''
    result = []
    name_list = [u"sheng", u"xiangmuming", u"hetongpingshenbianhao"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    # 省
    sheng = extract_result[guonei[name_list[0]][0]]
    audit_item = audit_true_value(sheng,u"省",value_sheng,u"[_\s省市]",audit_rule="necessary_head",audit_rule_type =u"必要条款")
    result.append(audit_item)
    # 项目名
    xiangmumign = extract_result[guonei[name_list[1]][0]]
    audit_item = audit_not_null_each(xiangmumign, u"项目名", value_xiangmuming, u"[_\s（）\(\)、,，项目]",audit_rule="check",audit_rule_type =u"检查项条款")
    result.append(audit_item)
    # 合同评审编号
    hetongpingshenbianhao = extract_result[guonei[name_list[2]][0]]
    audit_item = audit_not_null_each(hetongpingshenbianhao, u"合同评审编号", value_hetongpingshenbianhao, u"[_\s（）\(\)、,，]",audit_rule="check",audit_rule_type =u"检查项条款")
    result.append(audit_item)
    return result

def audit_7(extract_result,value_goods,value_zongji):
    '''
    第七部分   表格1抽取
    :param meta_data_list:
    :return:    necessary_row
    "xuhao":["57","序号"],    # 序号
    "mingcheng":["58","名称"],    # 名称
    "xinghao":["6","型号"],    # 型号
    "shuliang":["7","数量"],    # 数量
    "danjia":["8","单价"],     # 单价
    "xiaojijine":["9","小计金额"],   # 小计金额
    '''
    def diff_good(extract_good, crm_good):
        print(extract_good)
        print(crm_good)
        diff_boo = True
        diff_html = u""
        # 名称
        if extract_good["mingcheng"] == crm_good["mingcheng"]:
            diff_html += u'名称:<span class="green">{0}</span>;'.format(extract_good["mingcheng"])
        else:
            diff_html += u'名称:<span class="red">{0}</span><span class="green">({1})</span>;'.format(extract_good["mingcheng"],crm_good["mingcheng"])
        # 型号
        diff_html += u'型号:<span class="green">{0}</span>'.format(extract_good["xinghao"])
        # 数量
        if extract_good["shuliang"] == crm_good["shuliang"]:
            diff_html += u'数量:<span class="green">{0}</span>;'.format(extract_good["shuliang"])
        else:
            diff_html += u'数量:<span class="red">{0}</span><span class="green">({1})</span>;'.format(extract_good["shuliang"],crm_good["shuliang"])
            diff_boo = False
        # 单价
        try:
            if float(extract_good["danjia"].replace(",","")) == float(crm_good["danjia"].replace(",","")):
                diff_html += u'单价:<span class="green">{0}</span>;'.format(extract_good["danjia"])
            else:
                diff_html += u'单价:<span class="red">{0}</span><span class="green">({1})</span>;'.format(
                    extract_good["danjia"], crm_good["danjia"])
                diff_boo = False
        except:
            diff_html += u'单价:<span class="red">{0}</span><span class="green">({1})</span>;'.format(
                extract_good["danjia"], crm_good["danjia"])
            diff_boo = False
        # 小计金额
        try:
            if float(extract_good["xiaojijine"].replace(",", "")) == float(crm_good["xiaojijine"].replace(",", "")):
                diff_html += u'小计金额:<span class="green">{0}</span>;'.format(extract_good["xiaojijine"])
            else:
                diff_html += u'小计金额:<span class="red">{0}</span><span class="green">({1})</span>;'.format(
                    extract_good["xiaojijine"], crm_good["xiaojijine"])
                diff_boo = False
        except:
            diff_html += u'小计金额:<span class="red">{0}</span><span class="green">({1})</span>;'.format(
                extract_good["xiaojijine"], crm_good["xiaojijine"])
            diff_boo = False
        audit_item = {
            "audit_suggestion": u"{0}$${1}$${2}$${3}$${4}".format(crm_good["mingcheng"],
                                                                   crm_good["xinghao"],
                                                                   crm_good["shuliang"],
                                                                   crm_good["danjia"],
                                                                   crm_good["xiaojijine"]),
            "audit_desc": u"货物信息修改",
            "audit_tips": u"与一站式数据不一致",
            "audit_rule_type": u"必要条款-产品清单明细",
            "helpfulness": 2,  # 1 通过  2不通过
            "audit_rule": u"necessary_row",
            "context": [],
            "audit_sample": diff_html,
            "references": u"{0}$${1}$${2}$${3}$${4}".format(extract_good["mingcheng"],
                                                                   extract_good["xinghao"],
                                                                   extract_good["shuliang"],
                                                                   extract_good["danjia"],
                                                                   extract_good["xiaojijine"]),
        }
        if diff_boo:
            audit_item["audit_desc"] = u"货物信息一致"
            audit_item["audit_tips"] = u"与一站式数据一致"
            audit_item["helpfulness"] = 1
        return audit_item

    result = []
    name_list = [u"xuhao",u"mingcheng", u"xinghao", u"shuliang", u"danjia", u"xiaojijine", u"zongji"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    # 得到所有数据
    xuhao = extract_result[guonei[name_list[0]][0]]
    # for each in xuhao:
    #     each.append("xuhao")
    mingcheng = extract_result[guonei[name_list[1]][0]]
    # for each in mingcheng:
    #     each.append("mingcheng")
    xinghao = extract_result[guonei[name_list[2]][0]]
    # for each in xinghao:
    #     each.append("xinghao")
    shuliang = extract_result[guonei[name_list[3]][0]]
    # for each in shuliang:
    #     each.append("shuliang")
    danjia = extract_result[guonei[name_list[4]][0]]
    # for each in danjia:
    #     each.append("danjia")
    xiaojijine = extract_result[guonei[name_list[5]][0]]
    # for each in xiaojijine:
    #     each.append("xiaojijine")
    data_list = [xuhao,mingcheng,xinghao,shuliang,danjia,xiaojijine]
    # print(data_list)
    # 统计组数
    group_list = []
    for each_part in data_list:
        for each_extract_part in each_part:
            group_list.append(each_extract_part[1])
    group_list = list(set(group_list))
    # 获取原始数据
    value_dict = {}
    for each in group_list:
        value_dict[str(each)] = {
            "mingcheng": [],
            "xinghao": [],
            "shuliang": [],
            "danjia": [],
            "xiaojijine": []
        }
    for each in mingcheng:
        value_dict[str(each[1])]["mingcheng"].append(each)
    for each in xinghao:
        value_dict[str(each[1])]["xinghao"].append(each)
    for each in shuliang:
        value_dict[str(each[1])]["shuliang"].append(each)
    for each in danjia:
        value_dict[str(each[1])]["danjia"].append(each)
    for each in xiaojijine:
        value_dict[str(each[1])]["xiaojijine"].append(each)
    for each_group in value_dict:
        # print('-----------')
        # print(each_group)
        for each_key in value_dict[each_group]:
            # print(each_key)
            each_value = value_dict[each_group][each_key]
            if len(each_value) == 0:
                value_dict[each_group][each_key] = u""
            else:
                value_dict[each_group][each_key] = get_text_by_index(each_value)
    # 转换成list便于后面计算，但要存好位置信息之后使用
    value_list = []
    context_list = []
    for each_key in value_dict:
        value_list.append(value_dict[each_key])
        each_context = []
        for a in data_list:
            for b in a:
                if str(b[1]) == each_key:
                    each_context.append(b)
        each_context.sort(key=lambda each:each[1])
        context_list.append(each_context)
    # print('----')
    # print(value_list)
    # print(context_list)

    # 设定三个list    1 都有     2 crm独有    3 扫描件独有
    # 扫描件数据list :value_list       crm数据list:value_goods
    list_all_have = []
    list_only_crm_have = []
    list_only_extract_have = []
    saomiao_list = []
    crm_list = []
    # 先找出完全一致的
    for index1,each_extract in enumerate(value_list):
        if index1 in saomiao_list:
            continue
        for index2,each_crm in enumerate(value_goods):
            if index2 in crm_list:
                continue
            try:
                value1 = format_good(each_extract)
                value2 = format_good(each_crm)
                if value1 == value2:
                    # print(value1)
                    list_all_have.append([index1,index2])
                    saomiao_list.append(index1)
                    crm_list.append(index2)
            except:
                pass
                # print(traceback.format_exc())
    for index1, each_extract in enumerate(value_list):
        if index1 in saomiao_list:
            continue
        for index2, each_crm in enumerate(value_goods):
            if index2 in crm_list:
                continue
            if each_extract["xinghao"] == each_crm["xinghao"]:
                list_all_have.append([index1, index2])
                saomiao_list.append(index1)
                crm_list.append(index2)
    for index1 in range(len(value_list)):
        if index1 not in saomiao_list:
            list_only_extract_have.append(index1)
    for index2 in range(len(value_goods)):
        if index2 not in crm_list:
            list_only_crm_have.append(index2)
    audit_item = {
        "audit_suggestion": "1",
        "audit_desc": "2",
        "audit_tips": "3",
        "audit_rule_type": u"必要条款-产品清单明细",
        "helpfulness": 1,  # 1 通过  2不通过
        "audit_rule": "",   # 分类
        "context": []
    }
    # print(list_all_have)
    # print(list_only_crm_have)
    # print(list_only_extract_have)

    # print(list_all_have)
    for each in list_all_have:
        # audit_item = {
        #     "audit_suggestion": "1",
        #     "audit_desc": "2",
        #     "audit_tips": "3",
        #     "audit_rule_type": u"必要条款--产品清单明细",
        #     "helpfulness": 1,  # 1 通过  2不通过
        #     "audit_rule": "necessary_row",  # 分类
        #     "context": []
        # }
        audit_item = diff_good(value_list[each[0]],value_goods[each[1]])
        audit_item["context"] = [{"text":e[0], "offset":e[2]} for e in context_list[each[0]]]
        result.append(audit_item)

    for each in list_only_extract_have:
        extract_good = value_list[each]
        references = u"{0}$${1}$${2}$${3}$${4}".format(extract_good["mingcheng"],
                                                            extract_good["xinghao"],
                                                            extract_good["shuliang"],
                                                            extract_good["danjia"],
                                                            extract_good["xiaojijine"])
        audit_item = {
            "audit_suggestion": u"",
            "audit_desc":  u"货物信息新增",
            "audit_tips": u"相较一站式数据新增",
            "audit_rule_type": u"必要条款-产品清单明细",
            "helpfulness": 2,  # 1 通过  2不通过
            "audit_rule": "necessary_row",  # 分类
            "context": [{"text":e[0],"offset":e[2]} for e in context_list[each]],
            "references": references,
            "audit_sample": u"货物信息新增"
        }
        result.append(audit_item)
    for each in list_only_crm_have:
        suggestion = u"{0}$${1}$${2}$${3}$${4}".format(value_goods[each]["mingcheng"], value_goods[each]["xinghao"], value_goods[each]["shuliang"],
                      value_goods[each]["danjia"], value_goods[each]["xiaojijine"])
        audit_item = {
            "audit_suggestion": suggestion,
            "audit_desc": u"货物信息遗漏",
            "audit_tips": u"相较一站式数据遗漏",
            "audit_rule_type": u"必要条款-产品清单明细",
            "helpfulness": 2,  # 1 通过  2不通过
            "audit_rule": "necessary_row",  # 分类
            "context": [],
            "references": "$$$$$$$$",
            "audit_sample": u"货物信息遗漏"
        }
        result.append(audit_item)

    # 总计金额
    target = extract_result[guonei[name_list[-1]][0]]
    pat = u"[_\s,，]"
    audit_item = {
        "audit_suggestion": value_zongji,
        "audit_desc": u"总计",
        "audit_tips": u"与一站式数据不一致",
        "audit_rule_type": u"必要条款",
        "helpfulness": 1,  # 1 通过  2不通过
        "audit_rule": "necessary_head",
        "context": []
    }
    if len(target) > 0:
        extract_target = u"".join([each[0] for each in target])
        audit_item["context"] = [{"text": each[0], "offset": each[2]} for each in target]
        try:
            if float(delete_chr(extract_target, pat)) == float(delete_chr(value_zongji, pat)):
                audit_item["audit_tips"] = u"与一站式数据一致"
            else:
                audit_item["helpfulness"] = 2
        except:
            audit_item["helpfulness"] = 2
    else:
        audit_item["audit_suggestion"] = value_zongji
        audit_item["audit_tips"] = u"未识别到目标"
        audit_item["helpfulness"] = 2
    # audit_item = audit_true_value(extract_result[guonei[name_list[-1]][0]], u"总计", value_zongji, u"[_\s,，]")
    result.append(audit_item)
    # print(audit_item)
    return result

def audit_8(extract_result,tiaokuan):
    '''
    第八部分   产品验收条款
    :param meta_data_list:
    :return:   not_necessary
    '''
    result = []
    content = tiaokuan["chanpinyanshou"]
    name_list = [u"chanpinyanshou"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    audit_item = audit_true_text(extract_result[guonei[name_list[0]][0]],u"产品验收条款",content,audit_rule="not_necessary",audit_rule_type=u"非必要条款")
    result.append(audit_item)
    return result

def audit_9(extract_result,tiaokuan):
    '''
    第九部分   包装方式条款
    :param meta_data_list:
    :return:   not_necessary
    '''
    result = []
    content = tiaokuan["baozhuangfangshi"]
    name_list = [u"baozhuangfangshi"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    audit_item = audit_true_text(extract_result[guonei[name_list[0]][0]],u"包装方式条款",content,audit_rule="not_necessary",audit_rule_type=u"非必要条款")
    result.append(audit_item)
    return result

def audit_10(extract_result,tiaokuan):
    '''
    第十部分   到货签收条款
    :param meta_data_list:
    :return:   not_necessary
    '''
    result = []
    content = tiaokuan["daohuoqianshou"]
    name_list = [u"daohuoyanshou"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    audit_item = audit_true_text(extract_result[guonei[name_list[0]][0]],u"到货签收条款",
                                 content,audit_rule="not_necessary",audit_rule_type=u"非必要条款")
    result.append(audit_item)
    return result

def audit_11(extract_result,extra_conf):
    '''
    第十一部分   交货方式条款
    result[guonei["fahuoxuqiushijian"][0]] = []
    result[guonei["jiaohuodidiansheng"][0]] = []
    result[guonei["jiaohuodidianshi"][0]] = []
    result[guonei["jiaohuodidianqu"][0]] = []
    result[guonei["jiaohuodidianxiangqing"][0]] = []
    result[guonei["shouhuoren"][0]] = []
    result[guonei["shouhuolianxidianhua"][0]] = []
    result[guonei["yunshufangshi"][0]] = []
    :param meta_data_list:
    :return:
    '''
    result = []
    name_list = [u"fahuoxuqiushijian", u"jiaohuodidiansheng",# u"jiaohuodidianshi", u"jiaohuodidianqu",
                 #u"jiaohuodidianxiangqing",
                 u"shouhuoren", #u"shouhuolianxidianhua",
                 u"yunshufangshi"]
    title_list = [u"交货方式-发货需求时间", u"交货方式-发货地点省",# u"交货方式-发货地点市", u"交货方式-发货地点区",
                 #u"交货方式-发货地点详情",
                  u"交货方式-收货人", #u"收货联系电话",
                  u"运输方式"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    for index,each in enumerate(name_list):
        audit_item = audit_not_null_each(extract_result[guonei[each][0]], title_list[index], extra_conf[each], u"[_\s省市区县\(\)（）。]", audit_rule="check",
                                      audit_rule_type=u"检查项条款")
        result.append(audit_item)

    # result = audit_true_value(extract_result,name_list,title_list,audit_rule="check",audit_rule_type=u"检查项条款")


    dianhua = "".join([each[0] for each in extract_result[guonei["shouhuolianxidianhua"][0]]])
    context =[{"text":each[0],"offset":each[2]} for each in extract_result[guonei["shouhuolianxidianhua"][0]]]
    dianhua = re.sub(u"[,，、；;\/或]",";",dianhua)
    dianhuas = dianhua.split(";")
    pat_dianhua = "^1\d{10}$|^\d{3,4}\-\d{8}$"
    dianhua_boo = True
    for each in dianhuas:
        if len(re.findall(pat_dianhua,each))==0:
            dianhua_boo = False
            break
    audit_item = {
        "audit_suggestion": u"需符合电话号码格式",
        "audit_desc": u"交货方式-收货联系电话",
        "audit_tips": u"格式检查",
        "audit_rule_type": u"检查项条款",
        "helpfulness": 1,  # 1 通过  2不通过
        "audit_rule": "check",
        "context": context
    }
    if not dianhua_boo:
        audit_item["helpfulness"] = 2
    result.append(audit_item)


    return result

def audit_12(extract_result, tiaokuan):
    '''
    第十二部分   供方发货时间条款
    :param meta_data_list:
    :return:
    '''
    result = []
    content = tiaokuan["gongfangfahuo"]
    name_list = [u"gongfangfahuoshijian"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    audit_item = audit_true_text(extract_result[guonei[name_list[0]][0]], u"供方发货时间", content,
                                 audit_rule="not_necessary",audit_rule_type=u"非必要条款")
    result.append(audit_item)
    return result

def audit_13(extract_result,tiaokuan):
    '''
    第十三部分   运输费用承担方条款
    :param meta_data_list:
    :return:
    '''
    result = []
    content = tiaokuan["yunshufeiyong"]
    name_list = [u"yunshufeiyongchegndanfang"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    audit_item = audit_true_text(extract_result[guonei[name_list[0]][0]], u"运输费用承担方", content,
                                 audit_rule="not_necessary",audit_rule_type=u"非必要条款")
    result.append(audit_item)
    return result

def audit_14(extract_result,tiaokuan):
    '''
    第十四部分   质量保证条款
    :param meta_data_list:
    :return:
    '''
    result = []
    content = tiaokuan["zhiliangbaozheng"]
    name_list = [u"zhiliangbaozheng"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    audit_item = audit_true_text(extract_result[guonei[name_list[0]][0]], u"质量保证", content,
                                 audit_rule="not_necessary",audit_rule_type=u"非必要条款")
    result.append(audit_item)
    return result

def audit_15(extract_result,tiaokuan):
    '''
    第十五部分   安装与服务条款
    :param meta_data_list:
    :return:
    9、本合同下甲方负责安装的，甲方（包括甲方委托或指定的第三方）应严格按照以下要求安装：1）产品随机配备的说明书（若乙方培训另有要求的，以乙方培训内容为准）；2）工程项目施工质量手册，请参见乙方官方网："http://www.dahuatech.com/"服务支持；3）如仍存在安装疑义的，请联系乙方代表。如甲方未按照上述要求，擅自更改安装方案，造成质量、安全事故的，全部损失由甲方自行承担。
    '''
    result = []
    content = tiaokuan["anzhuangfuwu"]
    name_list = [u"anzhuangyufuwuzhichi"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    audit_item = audit_true_text(extract_result[guonei[name_list[0]][0]], u"安装与服务", content,
                                 audit_rule="not_necessary",audit_rule_type=u"非必要条款")
    result.append(audit_item)
    return result

def audit_16(extract_result):
    '''
    第十六部分   发票开具时间
    :param meta_data_list:
    :return:
    '''
    result = []
    name_list = [u"fapiaokaijushijian"]
    title_list = [u"发票开具时间"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    result = audit_not_null(extract_result, name_list, title_list, audit_rule="check",audit_rule_type=u"检查项条款")

    return result

def audit_17(extract_result):
    '''
    第十七部分   发票类型
    :param meta_data_list:
    :return:
    '''
    result = []
    name_list = [u"fapiaoleixing"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    target_extract_result = extract_result[guonei[name_list[0]][0]]
    content = "".join([each[0] for each in target_extract_result])
    audit_item = {
        "audit_suggestion": u"该项内容二选一",
        "audit_desc": "发票类型",
        "audit_tips": u"选择检查",
        "audit_rule_type": u"检查项条款",
        "helpfulness": 1,  # 1 通过  2不通过
        "audit_rule": "check",
        "context": [{"text":each[0],"offset":each[2]} for each in target_extract_result]
    }

    if u"V" not in content and u"√" not in content and u"v" not in content:
        audit_item["helpfulness"] = 2
    result.append(audit_item)
    return result

def audit_18(extract_result, extra_conf):
    '''
    第十八部分   结款日期与结算方式
    :param meta_data_list:
    :return:
    '''
    result = []
    name_list = [u"jkrqjjsfs"]
    title_list = [u"结款日期及结算方式"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    target_extract_result = extract_result[guonei[name_list[0]][0]]  # 抽取到的结果
    target_content = u"".join([each[0] for each in target_extract_result])
    crm_result = extra_conf[name_list[0]]
    target_content_list = target_content.split("【")
    select_boo = False
    select_content = u""
    for each in target_content_list:
        if "v" in each or "V" in each or "√" in each:
            select_boo = True
            select_content = each
    select_content_after_re = re.sub(u"[【】\s_\.,，\(\)（）。、：:;；Vv√]",u"",select_content)
    select_content_after_re = re.sub(u"[Oo]",u"0", select_content_after_re)
    crm_result_after_re = re.sub(u"[【】\s_\.,，\(\)（）。、：:；;Vv√]", u"", crm_result)
    crm_result_after_re = re.sub(u"[Oo]", u"0", crm_result_after_re)
    audit_item = {
        "audit_suggestion": crm_result,
        "audit_desc": title_list[0],
        "audit_tips": u"该项不可不选或为空",
        "audit_rule_type": u"必要条款",
        "helpfulness": 2,  # 1 通过  2不通过
        "audit_rule": "necessary_head",
        "context":[{"text":each[0],"offset":each[2]} for each in target_extract_result]
    }
    if not select_boo:
        pass
    else:
        if select_content_after_re == crm_result_after_re:
            audit_item["helpfulness"] = 1
        else:
            audit_item["audit_tips"] = u"与一站式数据不一致"


    result.append(audit_item)

    # print(target_extract_result)
    # print(crm_result)



    # result = audit_not_null(extract_result,name_list,title_list,audit_rule="necessary_head",audit_rule_type=u"必要条款")
    return result

def audit_19(extract_result):
    '''
    第十九部分   支付方式   zhifufangshi
    :param meta_data_list:
    :return:
    '''
    result = []
    name_list = [u"zhifufangshi"]
    title_list = [u"支付方式"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    # result = audit_not_null(extract_result, name_list, title_list, audit_rule="check",audit_rule_type=u"检查项条款")
    target_extract_result = extract_result[guonei[name_list[0]][0]]  # 抽取到的结果
    target_content = u"".join([each[0] for each in target_extract_result])

    audit_item = {
        "audit_suggestion": u"该项不可不选或为空",
        "audit_desc": title_list[0],
        "audit_tips": u"该项不可不选或为空",
        "audit_rule_type": u"检查项条款",
        "helpfulness": 2,  # 1 通过  2不通过
        "audit_rule": "check",
        "context": [{"text": each[0], "offset": each[2]} for each in target_extract_result]
    }

    if u"v" in target_content or u"V" in target_content or u"√" in target_content:
        audit_item["helpfulness"] = 1
    else:
        audit_item["audit_tips"] = u"与一站式数据不一致"

    result.append(audit_item)
    return result

def audit_20(extract_result,tiaokuan):
    '''
    第二十部分   退货约定   tuihuoyueding
    :param meta_data_list:
    :return:
    退货约定：非质量原因供方原则上不接受退货，供方同意退货的，需方按照供方要求支付退货费用后，双方签订退货协议；否则，需方不得以退货为由，拒绝履行付款义务。对于已开发票的退货，需方必须退回发票或提供红字开票通知单。
    '''
    result = []
    content = tiaokuan["tuihuoyueding"]
    name_list = [u"tuihuoyueding"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    audit_item = audit_true_text(extract_result[guonei[name_list[0]][0]], u"退货约定", content,
                                 audit_rule="not_necessary",audit_rule_type=u"非必要条款")
    result.append(audit_item)
    return result

def audit_21(extract_result,tiaokuan):
    '''
    第二十一部分   违约责任   weiyuezeren
    :param meta_data_list:
    :return:
    违约责任：1）任何一方不履行本合同义务或履行本合同义务不符合约定的，均属于违约行为。违约方应向守约方支付合同总金额20%作为违约金，并应对守约方因此造成的损失承担赔偿责任。本合同另有规定的除外。2）由于供方原因，未能按合同约定向需方交货，供方应向需方支付迟延履行违约金。每迟延1日，供方应向需方支付相当于迟延交付货物货款的1‰作为迟延履行违约金，但迟延履行违约金总额不超过合同总金额的20%。3）由于需方原因，未能按合同约定付款，需方应向供方支付违约金。每迟延1日，需方应向供方支付相当于迟延支付货款总额的1‰作为迟延履行违约金，但迟延履行违约金总额不超过合同总金额的20%。同时，交货期相应顺延。需方迟延付款超过30个自然日，供方有权解除合同。4）货款必须汇到供方书面指定的银行账号，否则，视为需方未按合同约定履行付款义务，供方有权要求需方继续履行付款业务，并追究需方逾期付款的违约责任。5）本合同约定交货方式、收货地点有误或变更，须需方提供盖章书面文件通知供方，由此产生的费用由需方承担。因需方通知有误或通知不及时，致使本合同交货出现的问题，供方不承担任何责任。
    '''
    result = []
    content = tiaokuan["weiyuezeren"]
    name_list = [u"weiyuezeren"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    audit_item = audit_true_text(extract_result[guonei[name_list[0]][0]], u"违约责任", content,
                                 audit_rule="not_necessary",audit_rule_type=u"非必要条款")
    result.append(audit_item)
    return result

def audit_22(extract_result,tiaokuan):
    '''
    第二十二部分   不可抗力   bukekangli
    :param meta_data_list:
    :return:
    '''
    result = []
    content = tiaokuan["bukekangli"]
    name_list = [u"bukekangli"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    audit_item = audit_true_text(extract_result[guonei[name_list[0]][0]], u"不可抗力", content,
                                 audit_rule="not_necessary",audit_rule_type=u"非必要条款")
    result.append(audit_item)
    return result

def audit_23(extract_result,tiaokuan):
    '''
    第二十三部分   解决合同纠纷   hetongjiufen1   hetongjiufen2   hetongjiufen3
    :param meta_data_list:
    :return:
    '''
    result = []
    content = [tiaokuan["jiejuejiufen1"],tiaokuan["jiejuejiufen3"]]
    # if len(content)==0:
    #     content=[
    #         u"解决合同纠纷的方式：执行本合同发生争议，由当事人双方协商解决。协商不成，双方同意向供方所在地人民法院提起诉讼。",
    #         u"需明确以下第____种通讯地址作为司法机关诉讼、仲裁、执行送达司法文书的地址：（1）地址：需方注册地   收件人：需方法定代表人；（2）地址：____  收件人：____",
    #         u"因载明的地址有误或未及时告知变更后的地址或指定收件人拒收，导致诉讼文书未能实际被接收的，邮寄送达的诉讼文书退回之日即视为送达之日。"
    #     ]
    name_list = [u"hetongjiufen1", u"hetongjiufen3"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []

    audit_item = audit_true_text(extract_result[guonei[name_list[0]][0]], u"合同纠纷概述", content[0],audit_rule="not_necessary",audit_rule_type=u"非必要条款")
    result.append(audit_item)

    audit_item = audit_true_text(extract_result[guonei[name_list[1]][0]], u"合同纠纷-送达日定义", content[1],audit_rule="not_necessary",audit_rule_type=u"非必要条款")
    result.append(audit_item)

    # 解决合同纠纷2
    if guonei["hetongjiufen2"][0] not in extract_result:
        extract_result[guonei["hetongjiufen2"][0]] = []
    audit_item = {
        "audit_suggestion": u"该项内容二选一",
        "audit_desc": "合同纠纷-通讯地址",
        "audit_tips": u"特定业务逻辑审核",
        "audit_rule_type": u"非必要条款",
        "helpfulness": 1,  # 1 通过  2不通过
        "audit_sample": u"特定业务逻辑审核通过",
        "audit_rule": "not_necessary",
        "context": [{"text": each[0], "offset": each[2]} for each in extract_result[guonei["hetongjiufen2"][0]]],
    }
    extract_content = u"".join([each[0] for each in extract_result[guonei["hetongjiufen2"][0]]])
    extract_content = re.sub(u"[：:_\s]+",u"",extract_content)
    extract_content = extract_content.replace("（","(").replace("）",")")
    pat_1 = u"明确以下第([\d])种通讯地址"
    re_result_1 = re.findall(pat_1, extract_content)
    if len(re_result_1) > 0:
        if u"1" in re_result_1[0]:
            pat_2 = u"(1)地址.{1,}收件人.{1,}"
            if re.findall(pat_2,extract_content) == 0:
                audit_item["helpfulness"] = 2
                audit_item["audit_suggestion"] = u"(1)地址及收件人不可为空"
                audit_item["audit_sample"] = u"(1)地址及收件人不可为空"
        elif u"2" in re_result_1[0]:
            pat_2 = u"(2)地址.{1,}收件人.{1,}"
            if re.findall(pat_2, extract_content) == 0:
                audit_item["helpfulness"] = 2
                audit_item["audit_suggestion"] = u"(2)地址及收件人不可为空"
                audit_item["audit_sample"] = u"(2)地址及收件人不可为空"
        else:
            audit_item["helpfulness"] = 2
            audit_item["audit_sample"] = u"未获取到待审核目标"
    else:
        audit_item["helpfulness"] = 2
        audit_item["audit_sample"] = u"未获取到待审核目标"
    result.append(audit_item)
    # print(json.dumps(result,ensure_ascii=False,indent=2))
    return result

def audit_24(extract_result,tiaokuan):
    '''
    第二十四部分   合同修订   hetongxiuding
    :param meta_data_list:
    :return:
    '''
    result = []
    content = tiaokuan["hetongxiuding"]
    name_list = [u"hetongxiuding"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    audit_item = audit_true_text(extract_result[guonei[name_list[0]][0]], u"合同修订", content,
                                 audit_rule="not_necessary",audit_rule_type=u"非必要条款")
    result.append(audit_item)
    return result

def audit_25(extract_result,tiaokuan):
    '''
    第二十五部分   合同份数   hetongfenshu
    :param meta_data_list:
    :return:
    '''
    result = []
    content = tiaokuan["hetongfenshu"]
    name_list = [u"hetongfenshu"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    audit_item = audit_true_text(extract_result[guonei[name_list[0]][0]], u"合同份数", content,
                                 audit_rule="not_necessary",audit_rule_type=u"非必要条款")
    result.append(audit_item)
    return result

def audit_26(extract_result,tiaokuan):
    '''
    第二十六部分   特别约定   tebieyueding
    :param meta_data_list:
    :return:
    需方理解，遵守适用的法律法规，包括美国出口管制法律的规定，是供方基本的公司政策。需方承诺，针对从供方及其关联人处购买的货物，需方将遵守相关的进口、出口、再出口的法律法规，具体要求包括但不限于：1）需方承诺，这些货物不会被用于被任何适用法律禁止的最终用途，包括化学武器、生物武器、核武器。导弹以及其他军用项目的设计、开发、生产、存储或使用。2）需方理解，如果货物含有源自美国的物品（U.S. Origin Items），该等货物（“管制货物”）可能受到美国出口管制条例（Export Administration Regulation，或EAR）的管辖，需方承诺，在管制货物的出口和再出口时，遵守相关的法律要求，包括，按照EAR或其他适用法律的要求，例如像美国政府申请获得出口许可；3）需方承诺，不会把管制货物转售给被美国或欧盟制裁的国家、实体或个人，包括但不限于美国财政部外国资产控制办公室管理的“特别指定国民及受封锁人士”清单（Specially Designated Nationals and Blocked PersonsList）和美国商务部工业和安全局管理的“拒绝交易对象”（Denied PersonsList）与"实体清单"（Entity List）以及受到欧盟金融制裁的欧盟人士、集团和实体综合清单上的个人或实体；4）需方承诺，对管制货物的使用和处理不会违反适用的法律法规。
    '''
    result = []
    content = tiaokuan["tebieyueding"]
    name_list = [u"tebieyueding"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []
    audit_item = audit_true_text(extract_result[guonei[name_list[0]][0]], u"特别约定", content,
                                 audit_rule="not_necessary",audit_rule_type=u"非必要条款")
    result.append(audit_item)
    return result

def audit_27(extract_result,extra_conf):
    '''
    第二十七部分   表格2
    xufanggaizhang         gongfanggaizhang
    lianxiren3             lianxirengongfang
    hetongqiandingriqi1    hetongqiandingriqi2
    zhanghumingcheng1      zhagnhumingcheng2
    kaihuyinhang1          kaihuyinhang2
    yinhangzhanghu1        yinhangzhanghu2
    shuihao1               shuihao2
    dizhidianhua1          dizhidianhua2

    :param meta_data_list:
    :return:
    '''
    result = []
    name_list1 = ["lianxiren3",
                  "hetongqiandingriqi1", "hetongqiandingriqi2", "zhanghumingcheng1",
                  "kaihuyinhang1", "yinhangzhanghu1",
                  "shuihao1", "dizhidianhua1"]
    title_list1 = ["需方联系人",
                  "需方合同签订日期", "供方合同签订日期", "需方账户名称",
                  "需方开户银行", "需方银行账户",
                  "需方税号", "需方地址电话", ]
    for each_name in name_list1:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []

    name_list2 = ["xufanggaizhang", "gongfanggaizhang", "lianxirengongfang"]
    title_list2 = ["需方(盖章)", "供方(盖章)", "供方联系人"]
    for each_name in name_list2:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []

    name_list3= ["zhanghumingcheng2", "kaihuyinhang2", "yinhangzhanghu2", "shuihao2",  "dizhidianhua2"]
    title_list3 = ["供方账户名称", "供方开户银行", "供方银行账户", "供方税号", "供方地址电话"]
    for each_name in name_list3:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []

    # result = audit_not_null(extract_result,name_list1,title_list1,audit_rule="check", audit_rule_type=u"检查项条款")
    for index, each in enumerate(name_list1):
        audit_item = audit_not_null_each(extract_result[guonei[each][0]], title_list1[index], extra_conf[each],
                                      pat=u"[,，\.。\(\)（）:：；;\s]",
                                      audit_rule="check", audit_rule_type=u"检查项条款")
        result.append(audit_item)

    for index,each in enumerate(name_list2):
        audit_item = audit_true_value(extract_result[guonei[each][0]], title_list2[index], extra_conf[each],
                                 pat=u"[,，\.。\(\)（）:：；;\s\·]",
                                 audit_rule="necessary_head",audit_rule_type=u"必要条款")
        result.append(audit_item)

    for index,each in enumerate(name_list3):
        audit_item = audit_true_value(extract_result[guonei[each][0]], title_list3[index], extra_conf[each],
                                 pat=u"[,，\.。\(\)（）:：；;\s\-]",
                                 audit_rule="check",audit_rule_type=u"检查项条款")
        result.append(audit_item)


    return result

def audit_28(extract_result,extra_conf):
    '''
    第二十八部分   供方收款账号信息   gongfangshoukuanzhanghaoxinxi
    "dianhuikaihuhang":["22", "电汇开户行"],      # 电汇开户行
    "dianhuizhanghao":["23", "电汇账号"],       # 电汇账号
    "dianhuihanghao":["24", "电汇行号"],        # 电汇行号
    "chengduikaihuhang":["25", "承兑开户行"],     # 承兑开户行
    "chengduizhanghao":["26", "承兑账号"],      # 承兑账号
    "chengduihanghao":["27", "承兑行号"],       # 承兑行号
    :param meta_data_list:
    :return:
    '''
    result = []
    name_list = ["dianhuikaihuhang", #"dianhuizhanghao",
                 "dianhuihanghao",
                 "chengduikaihuhang", #"chengduizhanghao",
                 "chengduihanghao"]
    title_list = ["电汇开户行", #"电汇账号",
                  "电汇行号",
                  "承兑开户行", #"承兑账号",
                  "承兑行号"]
    for each_name in name_list:
        if guonei[each_name][0] not in extract_result:
            extract_result[guonei[each_name][0]] = []

    for index,each in enumerate(name_list):
        if guonei[each][0] in extract_result:
            audit_item = audit_true_value(extract_result[guonei[each][0]], title_list[index], extra_conf[each],
                                     pat=u"[,，\.。\(\)（）:：；;\s]",
                                     audit_rule="check",audit_rule_type=u"检查项条款")
        else:
            audit_item = audit_true_value([], title_list[index], extra_conf[each],
                                          pat=u"[,，\.。\(\)（）:：；;\s]",
                                          audit_rule="check", audit_rule_type=u"检查项条款")
        result.append(audit_item)
    return result


def audit_29(text):
    '''
    金额大小写
    :return:
    '''
    money_dict = {
        u"壹": 1,
        u"贰": 2,
        u"叁": 3,
        u"肆": 4,
        u"伍": 5,
        u"陆": 6,
        u"柒": 7,
        u"捌": 8,
        u"玖": 9,
        u"零": 0
    }

    def transform(money):
        # print(money)
        if u"亿" in money:
            moneys = money.split(u"亿")
            if len(moneys) == 2:
                return transform(moneys[0]) * 100000000 + transform(moneys[1])
            else:
                return transform(moneys[0]) * 100000000
        elif u"万" in money:
            moneys = money.split(u"万")
            if len(moneys) == 2:
                return transform(moneys[0]) * 10000 + transform(moneys[1])
            else:
                return transform(moneys[0]) * 10000
        elif u"仟" in money:
            moneys = money.split(u"仟")
            if len(moneys) == 2:
                return transform(moneys[0]) * 1000 + transform(moneys[1])
            else:
                return transform(moneys[0]) * 1000
        elif u"佰" in money:
            moneys = money.split(u"佰")
            if len(moneys) == 2:
                return transform(moneys[0]) * 100 + transform(moneys[1])
            else:
                return transform(moneys[0]) * 100
        elif u"拾" in money:
            if money.startswith(u"拾"):
                money = u"壹" + money
            moneys = money.split(u"拾")
            if len(moneys) == 2:
                return transform(moneys[0]) * 10 + transform(moneys[1])
            else:
                return transform(moneys[0]) * 10
        elif u"元" in money:
            moneys = money.split(u"元")
            if len(moneys) == 2:
                return transform(moneys[0]) * 1 + transform(moneys[1])
            else:
                return transform(moneys[0]) * 1
        elif u"角" in money:
            moneys = money.split(u"角")
            if len(moneys) == 2:
                return transform(moneys[0]) * 0.1 + transform(moneys[1])
            else:
                return transform(moneys[0]) * 0.1
        elif u"分" in money:
            moneys = money.split(u"分")
            return transform(moneys[0]) * 0.01
        else:
            if len(money) == 1:
                return money_dict[money]
            elif len(money) == 0:
                return 0
            else:
                return money_dict[money[len(money) - 1]]


    # 对数字形式的带空格的做额外处理
    pat_numandspace = u"[\d\s,\.]+"
    numandspace_result = re.findall(pat_numandspace, text)
    for each in numandspace_result:
        each_num = each.replace(" ", "")
        each_numspace = each_num + " "*(len(each) - len(each_num))
        text = text.replace(each, each_numspace)

    pat_2_1 = u"[壹贰叁肆伍陆柒捌玖拾佰仟万亿零元角分]{2,}"
    result_2_1 = re.finditer(pat_2_1, text)
    return_false = []
    return_true = []
    result = []
    # 找到所有的大写 默认为金额
    for each in result_2_1:
        each_value = each.group()
        if each_value[0] not in u"壹贰叁肆伍陆柒捌玖拾":
            continue
        # 转小写数字
        # print(type(each_value))
        num = transform(each_value)
        start_index = each.span()[0]
        end_index = each.span()[1]
        target_str = text[max(start_index - 25, 0):min(len(text), end_index + 25)]
        pat_2_2 = "((\d{1,3}(,\d{3})+(\.\d{1,2})?\s*)|(\d{2,}(\.\d{1,2})?)\s*)"
        result_2_2 = re.finditer(pat_2_2, target_str)
        result_2_2_list = []
        find_flag = False
        for each2 in result_2_2:
            if each2.group().startswith("0"):
                continue
            each2_value = float(each2.group().replace(",", "").replace(" ", ""))
            result_2_2_list.append([each2.group(), each2.span()[0]])
            # 找到了大小一致的，放在最后面
            if int(num * 100) == int(each2_value * 100):
                find_flag = True
                break
        # 如果找到了数值却没有找到大小一致的
        if len(result_2_2_list) > 0 and find_flag == False:
            # result_2_2_list.sort(key=lambda e: len(e[0]) * (-1))
            return_false.append([{"text": each_value, "offset": start_index}, {"text": str(result_2_2_list[-1][0]),"offset": result_2_2_list[-1][1] + max(start_index - 25, 0)}])
        if find_flag:
            return_true.append([{"text": each_value, "offset": start_index}, {"text": str(result_2_2_list[-1][0]),
                                                                               "offset": result_2_2_list[-1][1] + max(
                                                                                   start_index - 25, 0)}])

    for each in return_false:
        audit_item = {
            "audit_suggestion": u"{0}:<span class=\"red\">{1}</span><span class=\"green\">({2})</span>".format(each[0]["text"],each[1]["text"],transform(each[0]["text"])),
            "audit_desc": u'扫描件金额大小写校验',
            "audit_tips": u"扫描件金额大小写不一致",
            "audit_rule_type": u"必要条款",
            "audit_rule": "necessary_head",
            "helpfulness": 2,
            "context": each
        }
        result.append(audit_item)

    for each in return_true:
        audit_item = {
            "audit_suggestion": u'扫描件金额大小写一致',
            "audit_desc": u'扫描件金额大小写校验',
            "audit_tips": u"扫描件金额大小写一致",
            "audit_rule_type": u"必要条款",
            "audit_rule": "necessary_head",
            "helpfulness": 1,
            "context": each
        }
        result.append(audit_item)

    return result


if __name__ == "__main__":
    text = u"机械硬盘ST4000VM00O10322.00003,220.002前端设想机ST4000VMO01l5oo500.00总计大写:叁仟贰佰贰拾元整4,220.00软件名称及版本:12、供方保证交付的货物为全新品,产品的功能验收以产品随机配备的说明"
    print(audit_29(text))
    pass
