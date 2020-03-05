#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/12/6 10:28
import os, sys, re, json, traceback, time
from field_conf import guonei
from document_beans.paragraph import Paragraph
from document_beans.table import Table
import copy,random
try:
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    from table_extract.app.driver import logger_online
except:
    class a(object):
        def __init__(self):
            pass
        def info(self,message):
            print(message)
    logger_online = a()

def paragraph_delete(meta_data_list):
    '''
    疑似页眉页脚删除
    :param meta_data_list:
    :return:
    '''
    meta_data_list_due = []
    for each in meta_data_list:
        if isinstance(each,Table):
            meta_data_list_due.append(each)
        else:
            content = each.text
            pat_1 = u'[a-zA-Z0-9:：；;\"\'\s_#]+|浙江大华科技有限公司|需方合同编号|供方合同编号'
            content = re.sub(pat_1, u"",content)
            if len(content) < 4 and has_most_word(content,[u"传真",u"电话",u"联系人",u"联系地址",u"座",u"层",u"行号", u"于"],num = 0)!=True:
                # print(each.text)
                pass
            else:
                meta_data_list_due.append(each)
    return meta_data_list_due

def has_most_word(content,word_list,num=0.65):
    # if isinstance(content,str):
    #     content = content.decode("utf8")
    # if isinstance(word_list,str):
    #     word_list = word_list.decode("utf8")
    true_num = 0
    for each in word_list:
        if each in content:
            true_num += 1
    if true_num*1.0 / len(word_list) > num:
        return True
    else:
        return False



def extract_split(value,mapper,num=1):
    # print(value)
    # print(mapper)
    if len(value) ==0 or len(mapper)==0 or len(value)!=len(mapper):
        return []
    pat_before = u"^[\(\)_\s]+"
    before = re.findall(pat_before,value)
    if len(before) > 0:
        value = value[len(before[0]):]
        mapper = mapper[len(before[0]):]
    pat_after = u"[_\s]+$"
    after = re.findall(pat_after, value)
    if len(after) > 0:
        mapper = mapper[:len(value) - len(after[0])]
        value = value[:len(value)-len(after[0])]
        # mapper = mapper[:len(value)-len(after[0])]
    if len(value) ==0 or len(mapper)==0 or len(value)!=len(mapper):
        return []
    '''
    抽取结果拆分    应对句子各种问题
    :param value:
    :param mapper:
    :return:
    '''
    # 每个index在mapper中的位置
    mapper_dict = {}
    for index,each in enumerate(mapper):
        mapper_dict[each] = index
    # 排序处理   并非一定要进行排序，原顺序整合也可以
    mapper_sort = copy.deepcopy(mapper)
    # mapper_sort.sort()
    # 整合处理
    merge_result = []
    start = mapper_sort[0]
    end = mapper_sort[0]
    index = 1
    while index < len(mapper_sort):
        if mapper_sort[index] == end + 1:
            end = mapper_sort[index]
        else:
            merge_result.append([start,end])
            start = mapper_sort[index]
            end = mapper_sort[index]
        index += 1
    merge_result.append([start, end])
    # print(merge_result)
    # 改为 start,len 的形式
    for each in merge_result:
        each[1] = each[1] - each[0] +1
    # 最终转换
    result = []
    index = 0
    for each in merge_result:
        each_value = value[index:index+each[1]]
        index = index+each[1]
        result.append([each_value,num,each[0]])
    # print(result)
    return result

def find_similarity_content(meta_data_list,content):
    # 需要一个综合比较的方法
    # 1.paragraph中有的，并且content中也有的字符，占content的比例，必须超过80%
    # 2.paragraph如果长度达到content的两倍及以上，则content必须处于一个它本身1.3倍长度的paragraph的字串中
    for i in range(len(meta_data_list)):
        for j in range(1,len(meta_data_list)+1):
            paragraph_content = ""
            for p in range(i,j):
                pass


def random_float():
    num = int((random.random()*0.3+0.7)*10000)/10000.0
    return num

# index对应paragraph序号
def index_to_paragraph_num(meta_data_list):
    index_dict = {}
    for index,each in enumerate(meta_data_list):
        if isinstance(each,Table):
            continue
        else:
            for each_index in each.mapper:
                index_dict[each_index] = index
    return index_dict

# parapraph合成
def paragraph_merge(meta_data_list):
    char_list = []
    for each in meta_data_list:
        char_list += each.chars
    return Paragraph(char_list)

# 根据目标段落和index_dict计算出已经处理的段落序号
def due_paragraph_list(paragraph,index_dict):
    index_list = []
    for each in paragraph.mapper:
        index_list.append(index_dict[each])
    index_list = list(set(index_list))
    index_list.sort()
    return index_list

def extract_1(meta_data_list):
    '''
    第一部分   需方和供方
    :return:
    '''
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    paragraph_all = paragraph_merge(meta_data_list)
    # 寻找目标
    # print(paragraph_all)
    result = {}
    if u"需方" in paragraph_all.text and u"供方" in paragraph_all.text and u"电话" in paragraph_all.text:
        index_flag1 = min(paragraph_all.text.find(u"需方"),paragraph_all.text.find(u"供方"))
        index_flag2 = paragraph_all.text.find(u"电话")
        target_paragraph = Paragraph(paragraph_all.chars[index_flag1:index_flag2])
        # print(target_paragraph)
        content = (target_paragraph.text).replace(u"：", u":").replace(u"；", u";").replace(u";", u":")
        contents = content.split(u"供方")
        if paragraph_all.text.find(u"需方") > paragraph_all.text.find(u"供方"):
            contents = content.split(u"需方")
        xf = u""
        gf = u""
        if len(contents) == 2:
            xf_contents = contents[0].split(u":")
            if len(xf_contents) == 2:
                xf = xf_contents[1]
            gf_contents = contents[1].split(u":")
            if len(gf_contents) == 2:
                gf = gf_contents[1]
        if xf!=u"":
            value = xf
            index = target_paragraph.text.find(value)
            mapper = target_paragraph.mapper[index:index+len(value)]
            result[guonei["xufang"][0]] = extract_split(value,mapper)
        else:
            result[guonei["xufang"][0]] = []
        if gf!=u"":
            value = gf
            index = target_paragraph.text.find(value)
            mapper = target_paragraph.mapper[index:index+len(value)]
            result[guonei["gongfang"][0]] = extract_split(value,mapper)
        else:
            result[guonei["gongfang"][0]] = []
        # 返回已处理的部分内容
        result["due"] = due_paragraph_list(target_paragraph,index_dict)
        # print(result["due"])
        result["index"] = result["due"][-1]
        # print("1:{0}".format(meta_data_list[result["index"]]))
    else:
        result[guonei["xufang"][0]] = []
        result[guonei["gongfang"][0]] = []
        result["index"] = 0
        result["due"] = []
    return result

def extract_2(meta_data_list):
    '''
    第二部分   两个电话
    :param meta_data_list:
    :return:
    '''
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    paragraph_all = paragraph_merge(meta_data_list)
    # 寻找目标
    result = {}
    if u"电话" in paragraph_all.text and u"传真" in paragraph_all.text:
        index_flag1 = paragraph_all.text.find(u"电话")
        index_flag2 = paragraph_all.text.find(u"传真")
        target_paragraph = Paragraph(paragraph_all.chars[index_flag1:index_flag2])
        # print(target_paragraph)
        content = (target_paragraph.text).replace(u"：", u":").replace(u"；", u";").replace(u";", u":")
        contents = content.split(u"电话")
        dianhua1 = u""
        dianhua2 = u""
        if len(contents) == 3:
            dianhua1_contents = contents[1].split(u":")
            if len(dianhua1_contents) == 2:
                dianhua1 = dianhua1_contents[1]
            dianhua2_contents = contents[2].split(u":")
            if len(dianhua2_contents) == 2:
                dianhua2 = dianhua2_contents[1]
        if dianhua1 != u"":
            value = dianhua1
            index = target_paragraph.text.find(value)
            mapper = target_paragraph.mapper[index:index + len(value)]
            result[guonei["dianhua1"][0]] = extract_split(value, mapper)
        else:
            result[guonei["dianhua1"][0]] = []
        if dianhua2 != u"":
            value = dianhua2
            index = target_paragraph.text.find(value)
            mapper = target_paragraph.mapper[index:index + len(value)]
            result[guonei["dianhua2"][0]] = extract_split(value, mapper)
        else:
            result[guonei["dianhua2"][0]] = []
        # 返回已处理的部分内容
        result["due"] = due_paragraph_list(target_paragraph, index_dict)
        # print(result["due"])
        result["index"] = result["due"][-1]
        # print("1:{0}".format(meta_data_list[result["index"]]))
    else:
        result[guonei["dianhua1"][0]] = []
        result[guonei["dianhua2"][0]] = []
        result["index"] = 0
        result["due"] = []
    return result

def extract_3(meta_data_list):
    '''
    第三部分   两个传真
    :param meta_data_list:
    :return:
    '''
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    paragraph_all = paragraph_merge(meta_data_list)
    # 寻找目标
    result = {}
    if u"传真" in paragraph_all.text and u"联系人" in paragraph_all.text:
        index_flag1 = paragraph_all.text.find(u"传真")
        index_flag2 = paragraph_all.text.find(u"联系人")
        target_paragraph = Paragraph(paragraph_all.chars[index_flag1:index_flag2])
        # print(target_paragraph)
        content = (target_paragraph.text).replace(u"：", u":").replace(u"；", u";").replace(u";", u":")
        contents = content.split(u"传真")
        chuanzhen1 = u""
        chuanzhen2 = u""
        if len(contents) == 3:
            chuanzhen1_contents = contents[1].split(u":")
            if len(chuanzhen1_contents) == 2:
                chuanzhen1 = chuanzhen1_contents[1]
            chuanzhen2_contents = contents[2].split(u":")
            if len(chuanzhen2_contents) == 2:
                chuanzhen2 = chuanzhen2_contents[1]
        if chuanzhen1 != u"":
            value = chuanzhen1
            index = target_paragraph.text.find(value)
            mapper = target_paragraph.mapper[index:index + len(value)]
            result[guonei["chuanzhen1"][0]] = extract_split(value, mapper)
        else:
            result[guonei["chuanzhen1"][0]] = []
        if chuanzhen2 != u"":
            value = chuanzhen2
            index = target_paragraph.text.find(value)
            mapper = target_paragraph.mapper[index:index + len(value)]
            result[guonei["chuanzhen2"][0]] = extract_split(value, mapper)
        else:
            result[guonei["chuanzhen2"][0]] = []
        # 返回已处理的部分内容
        result["due"] = due_paragraph_list(target_paragraph, index_dict)
        # print(result["due"])
        result["index"] = result["due"][-1]
        # print("1:{0}".format(meta_data_list[result["index"]]))
    else:
        result[guonei["chuanzhen1"][0]] = []
        result[guonei["chuanzhen2"][0]] = []
        result["index"] = 0
        result["due"] = []
    return result

def extract_4(meta_data_list):
    '''
    第四部分   两个联系人
    :param meta_data_list:
    :return:
    '''
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    paragraph_all = paragraph_merge(meta_data_list)
    # 寻找目标
    result = {}
    if u"联系人" in paragraph_all.text and u"联系地址" in paragraph_all.text:
        index_flag1 = paragraph_all.text.find(u"联系人")
        index_flag2 = paragraph_all.text.find(u"联系地址")
        target_paragraph = Paragraph(paragraph_all.chars[index_flag1:index_flag2])
        # print(target_paragraph)
        content = (target_paragraph.text).replace(u"：", u":").replace(u"；", u";").replace(u";", u":")
        contents = content.split(u"联系人")
        lianxiren1 = u""
        lianxiren2 = u""
        if len(contents) == 3:
            lianxiren1_contents = contents[1].split(u":")
            if len(lianxiren1_contents) == 2:
                lianxiren1 = lianxiren1_contents[1]
            lianxiren2_contents = contents[2].split(u":")
            if len(lianxiren2_contents) == 2:
                lianxiren2 = lianxiren2_contents[1]
        if lianxiren1 != u"":
            value = lianxiren1
            index = target_paragraph.text.find(value)
            mapper = target_paragraph.mapper[index:index + len(value)]
            result[guonei["lianxiren1"][0]] = extract_split(value, mapper)
        else:
            result[guonei["lianxiren1"][0]] = []
        if lianxiren2 != u"":
            value = lianxiren2
            index = target_paragraph.text.find(value)
            mapper = target_paragraph.mapper[index:index + len(value)]
            result[guonei["lianxiren2"][0]] = extract_split(value, mapper)
        else:
            result[guonei["lianxiren2"][0]] = []
        # 返回已处理的部分内容
        result["due"] = due_paragraph_list(target_paragraph, index_dict)
        # print(result["due"])
        result["index"] = result["due"][-1]
        # print("1:{0}".format(meta_data_list[result["index"]]))
    else:
        result[guonei["lianxiren1"][0]] = []
        result[guonei["lianxiren2"][0]] = []
        result["index"] = 0
        result["due"] = []
    return result

def extract_5(meta_data_list):
    '''
    第五部分   两个联系地址
    :param meta_data_list:
    :return:
    '''
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    paragraph_all = paragraph_merge(meta_data_list)
    # 寻找目标
    result = {}
    if u"联系地址" in paragraph_all.text and u"供需双方本" in paragraph_all.text:
        index_flag1 = paragraph_all.text.find(u"联系地址")
        index_flag2 = paragraph_all.text.find(u"供需双方本")
        target_paragraph = Paragraph(paragraph_all.chars[index_flag1:index_flag2])
        # print(target_paragraph)
        content = (target_paragraph.text).replace(u"：", u":").replace(u"；", u";").replace(u";", u":")
        contents = content.split(u"联系地址")
        lianxidizhi1 = u""
        lianxidizhi2 = u""
        if len(contents) == 3:
            lianxidizhi1_contents = contents[1].split(u":")
            if len(lianxidizhi1_contents) == 2:
                lianxidizhi1 = lianxidizhi1_contents[1]
            lianxidizhi2_contents = contents[2].split(u":")
            if len(lianxidizhi2_contents) == 2:
                lianxidizhi2 = lianxidizhi2_contents[1]
        if lianxidizhi1 != u"":
            value = lianxidizhi1
            index = target_paragraph.text.find(value)
            mapper = target_paragraph.mapper[index:index + len(value)]
            result[guonei["lianxidizhi1"][0]] = extract_split(value, mapper)
        else:
            result[guonei["lianxidizhi1"][0]] = []
        if lianxidizhi2 != u"":
            value = lianxidizhi2
            index = target_paragraph.text.find(value)
            mapper = target_paragraph.mapper[index:index + len(value)]
            result[guonei["lianxidizhi2"][0]] = extract_split(value, mapper)
        else:
            result[guonei["lianxidizhi2"][0]] = []
        # 地址额外处理
        if len(result[guonei["lianxidizhi2"][0]]) > 1:
            result[guonei["lianxidizhi1"][0]] += result[guonei["lianxidizhi2"][0]][1:]
            result[guonei["lianxidizhi2"][0]] = [result[guonei["lianxidizhi2"][0]][0]]

        # 返回已处理的部分内容
        result["due"] = due_paragraph_list(target_paragraph, index_dict)
        # print(result["due"])
        result["index"] = result["due"][-1]
        # print("1:{0}".format(meta_data_list[result["index"]]))
    else:
        result[guonei["lianxidizhi1"][0]] = []
        result[guonei["lianxidizhi2"][0]] = []
        result["index"] = 0
        result["due"] = []
    return result

def extract_6(meta_data_list):
    '''
    第六部分   一段话
    :param meta_data_list:
    :return:
    '''
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    paragraph_all = paragraph_merge(meta_data_list)
    # print(paragraph_all)
    # 寻找目标
    result = {}
    if u"信守执行" in paragraph_all.text and u"供需双方本" in paragraph_all.text:
        index_flag1 = paragraph_all.text.find(u"供需双方本")
        index_flag2 = max(paragraph_all.text.find(u"信守执行"),paragraph_all.text.find(u"商品名称"))
        target_paragraph = Paragraph(paragraph_all.chars[index_flag1:index_flag2])
        # print(target_paragraph)
        content = target_paragraph.text.replace("_"," ").replace("省 省","省  ")
        # print(content)
        mapper = target_paragraph.mapper
        pat_1 = u"货物用[于乎]([^省市]{2,9})[省市]"
        pat_2 = u"[省市][\s_]*(.+)项目,?"
        pat_3 = u"评审编号为([\s\d\-\_Vv]+)[,，]?以资双方"
        # 省/市
        sheng_result = re.findall(pat_1, content)
        if len(sheng_result) > 0:
            value1 = sheng_result[0]
            index1 = content.find(value1)
            mapper1 = mapper[index1:index1 + len(value1)]
            result[guonei["sheng"][0]] = extract_split(value1,mapper1)
        else:
            result[guonei["sheng"][0]] = []
        # 项目名称
        xiangmuming_result = re.findall(pat_2, content)
        # print(xiangmuming_result)
        if len(xiangmuming_result) > 0:
            value2 = xiangmuming_result[0]
            if value2.startswith(u"省") or value2.startswith(u"市"):
                value2 = value2[1:]
            index2 = content.find(value2)
            mapper2 = mapper[index2:index2 + len(value2)]
            result[guonei["xiangmuming"][0]] = extract_split(value2,mapper2)
        else:
            result[guonei["xiangmuming"][0]] = []
        # 评审编号
        hetongpingshenbianhao_result = re.findall(pat_3, content)
        if len(hetongpingshenbianhao_result) > 0:
            value3 = hetongpingshenbianhao_result[0]
            index3 = content.find(value3)
            mapper3 = mapper[index3:index3 + len(value3)]
            result[guonei["hetongpingshenbianhao"][0]] = extract_split(value3,mapper3)
        else:
            result[guonei["hetongpingshenbianhao"][0]] = []
        # 返回已处理的部分内容
        result["due"] = due_paragraph_list(target_paragraph, index_dict)
        # print(result["due"])
        result["index"] = result["due"][-1]
    else:
        result[guonei["sheng"][0]] = []
        result[guonei["xiangmuming"][0]] = []
        result[guonei["hetongpingshenbianhao"][0]] = []
        result["index"] = 0
        result["due"] = []


    return result

def extract_7(meta_data_list):
    '''
    第七部分   表格1抽取
    :param meta_data_list:
    :return:
    '''
    result = {
        guonei["xuhao"][0]:[],  # 序号
        guonei["mingcheng"][0]:[],  # 名称
        guonei["xinghao"][0]:[],  # 型号
        guonei["shuliang"][0]:[],  # 数量
        guonei["danjia"][0]:[],  # 单价
        guonei["xiaojijine"][0]:[],  # 小计金额
        guonei["zongji"][0]:[]
    }
    # 防止有跨页表格
    table_list = []
    for index,each in enumerate(meta_data_list):
        if isinstance(each,Table):
            table_list.append(each)
    # 找到最后一个表格所在的位置
    for index,each in enumerate(meta_data_list[::-1]):
        if isinstance(each,Table):
            result["index"] = len(meta_data_list) - index -1
    # 取出所有货物信息
    good_list = []
    for each_table in table_list:
        each_cells = each_table.cells
        for each_line in each_cells:
            each_first_cell = each_line[0].text
            cell_3 = each_line[3].text
            cell_4 = each_line[4].text
            # logger_online.info("||{0}||")
            pat_num = u"^[0-9a-zA-Z,，.]+$"
            # logger_online.info(re.findall(pat_num,each_first_cell))
            tar_num = 0
            if len(re.findall(pat_num,each_first_cell)) > 0:
                tar_num += 1
            if len(re.findall(pat_num, cell_3)) > 0:
                tar_num += 1
            if len(re.findall(pat_num, cell_4)) > 0:
                tar_num += 1
            if tar_num >1:
                good_list.append(each_line)
    # 归类，并依次放置
    float_dict = {}
    for each_good in good_list:
        each_index = each_good[0]
        each_name = each_good[1]
        each_model = each_good[2]
        each_num = each_good[3]
        each_price = each_good[4]
        each_total = each_good[5]
        num = random_float()
        while num in float_dict:
            num = random_float()
        float_dict[num]=1
        # 序号
        if len(each_index.text) > 0:
            index_value = extract_split(each_index.text,each_index.mapper)
            for each_value in index_value:
                each_value[1] = num
            result[guonei["xuhao"][0]] += index_value
        # 名称
        if len(each_name.text) > 0:
            name_value = extract_split(each_name.text, each_name.mapper)
            for each_value in name_value:
                each_value[1] = num
            result[guonei["mingcheng"][0]] += name_value
        # 型号
        if len(each_model.text) > 0:
            model_value = extract_split(each_model.text, each_model.mapper)
            for each_value in model_value:
                each_value[1] = num
            result[guonei["xinghao"][0]] += model_value
        # 数量
        if len(each_num.text) > 0:
            num_value = extract_split(each_num.text, each_num.mapper)
            for each_value in num_value:
                each_value[1] = num
            result[guonei["shuliang"][0]] += num_value
        # 单价
        if len(each_price.text) > 0:
            price_value = extract_split(each_price.text, each_price.mapper)
            for each_value in price_value:
                each_value[1] = num
            result[guonei["danjia"][0]] += price_value
        # 金额小计
        if len(each_total.text) > 0:
            total_value = extract_split(each_total.text, each_total.mapper)
            for each_value in total_value:
                each_value[1] = num
            result[guonei["xiaojijine"][0]] += total_value
    # 总计
    find_flag = False
    for each_table in table_list:
        each_cells = each_table.cells
        for each_line in each_cells:
            each_first_cell = each_line[0].text
            if u"总计" in each_first_cell:
                for each_cell in each_line[1:]:
                    #if len(each_cell.text)>0:
                    if len(re.findall(u'[\d,\.\s]+',each_cell.text)):
                        result[guonei["zongji"][0]] = extract_split(each_cell.text,each_cell.mapper)
                        break
                find_flag = True
                break
        if find_flag:
            break


    return result

def extract_8(meta_data_list,content=u"供方保证交付的货物为全新品产品的功能验收以产品随机配备的说明书功能描述为准需方收货后七天内未书面提出异议视为合格产品"):
    '''
    第八部分   产品验收条款
    :param meta_data_list:
    :return:
    '''
    result = {}
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    # 获取到目标句子
    char_list = []
    last_index = 0
    for index, each in enumerate(meta_data_list):
        if isinstance(each,Table):
            continue
        if index - last_index > 2:
            break
        text = each.text.replace(" ","").replace("_","").replace("、","").replace(",","").replace("。","")
        if has_most_word(content,text,num=0.8):
            char_list += each.chars
            last_index = index
    if len(char_list) > 0:
        target_paragraph = Paragraph(char_list)
        result[guonei["chanpinyanshou"][0]]=extract_split(target_paragraph.text,target_paragraph.mapper)
        # 返回已处理的部分内容
        result["due"] = due_paragraph_list(target_paragraph, index_dict)
        # print(result["due"])
        result["index"] = result["due"][-1]
    else:
        result[guonei["chanpinyanshou"][0]] = []
        # 返回已处理的部分内容
        result["due"] = []
        # print(result["due"])
        result["index"] = 0

    return result

def extract_9(meta_data_list,content=u"包装方式原厂纸箱包装"):
    '''
    第九部分   包装方式条款
    :param meta_data_list:
    :return:
    '''
    result = {}
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    # 获取到目标句子
    char_list = []
    last_index = 0
    for index, each in enumerate(meta_data_list):
        if isinstance(each,Table):
            continue
        if index - last_index > 2:
            break
        text = each.text.replace(" ","").replace("_","").replace("、","").replace(",","").replace("。","")
        if has_most_word(content,text,num=0.7):
            char_list += each.chars
            last_index = index
    if len(char_list) > 0:
        target_paragraph = Paragraph(char_list)
        result[guonei["baozhuangfangshi"][0]]=extract_split(target_paragraph.text,target_paragraph.mapper)
        # 返回已处理的部分内容
        result["due"] = due_paragraph_list(target_paragraph, index_dict)
        # print(result["due"])
        result["index"] = result["due"][-1]
    else:
        result[guonei["baozhuangfangshi"][0]] = []
        # 返回已处理的部分内容
        result["due"] = []
        # print(result["due"])
        result["index"] = 0

    return result

def extract_10(meta_data_list,content=u"需方需在货物到达时按厂商出口装箱标准进行验收并签收需方无合理原因即拒绝签收的视为违约供方有权自行处理该批货货物并就所受损失包括但不限于返程物流费用仓储费用等向需方索赔"):
    '''
    第十部分   到货签收条款
    :param meta_data_list:
    :return:
    '''
    result = {}
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    # 获取到目标句子
    char_list = []
    last_index = 0
    for index, each in enumerate(meta_data_list):
        if isinstance(each,Table):
            continue
        if index - last_index > 2:
            break
        text = each.text.replace(" ","").replace("_","").replace("、","").replace(",","").replace("。","")
        if has_most_word(content,text,num=0.7):
            char_list += each.chars
            last_index = index
    if len(char_list) > 0:
        target_paragraph = Paragraph(char_list)
        result[guonei["daohuoyanshou"][0]]=extract_split(target_paragraph.text,target_paragraph.mapper)
        # 返回已处理的部分内容
        result["due"] = due_paragraph_list(target_paragraph, index_dict)
        # print(result["due"])
        result["index"] = result["due"][-1]
    else:
        result[guonei["daohuoyanshou"][0]] = []
        # 返回已处理的部分内容
        result["due"] = []
        # print(result["due"])
        result["index"] = 0

    return result

def extract_11(meta_data_list):
    '''
    第十一部分   交货方式条款
    :param meta_data_list:
    :return:
    '''
    result = {}
    result[guonei["fahuoxuqiushijian"][0]] = []
    result[guonei["jiaohuodidiansheng"][0]] = []
    result[guonei["jiaohuodidianshi"][0]] = []
    result[guonei["jiaohuodidianqu"][0]] = []
    result[guonei["jiaohuodidianxiangqing"][0]] = []
    result[guonei["shouhuoren"][0]] = []
    result[guonei["shouhuolianxidianhua"][0]] = []
    result[guonei["yunshufangshi"][0]] = []

    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    paragraph_all = paragraph_merge(meta_data_list)
    if has_most_word(paragraph_all.text,[u"交货", u"方式", "发货", "需求", "时间", "地点", "收货人", "联系方式", "运输方式"]):
        index_flag1 = paragraph_all.text.find(u"交货方式")
        tmp1 = paragraph_all.text.find(u"供方发货时间")
        tmp2 = paragraph_all.text.find(u"运输费用")
        tmp3 = paragraph_all.text.find(u"质量保证")
        index_flag2 = tmp1
        if index_flag2==-1:
            index_flag2 = tmp2
        if index_flag2==-1:
            index_flag2 = tmp3
        if index_flag2==-1:
            index_flag2 = len(paragraph_all.text)
        if u"。" in paragraph_all.text[index_flag2-5:index_flag2]:
            index_flag2 = paragraph_all.text[index_flag2 - 5:index_flag2].find(u"。")+index_flag2-5
        target_paragraph = Paragraph(paragraph_all.chars[index_flag1:index_flag2])
        # 替换掉 \d)的形式
        pat_sub = "\d\)"
        content = re.sub(pat_sub,"  ",target_paragraph.text)
        # 开始识别
        pat_1 = u"发货需求时间"
        pat_2 = u"交货地点"
        pat_3 = u"收货人"
        pat_4 = u"收货联系电话"
        pat_5 = u" 运输方式"
        content = re.sub(pat_1, "  $$  ", content)
        content = re.sub(pat_2, " $$ ", content)
        content = re.sub(pat_3, "$$ ", content)
        content = re.sub(pat_4, "  $$  ", content)
        content = re.sub(pat_5, "  $$ ", content)
        pat_6 = u"[;；:：，,]"
        # content = re.sub(pat_6, " ", content)
        contents = content.split("$$")
        if len(contents)>5:
            # print(content)
            fahuoxuqiushijian = re.sub(pat_6, " ", contents[1]).strip()
            jiaohuodidian = re.sub(pat_6, " ", contents[2]).strip()
            shouhuoren = re.sub(pat_6, " ", contents[3]).strip()
            shouhuolianxidianhua = contents[4].strip()
            yunshufangshi = re.sub(pat_6, " ", contents[5]).strip()
            if fahuoxuqiushijian!=u"":
                index = content.find(fahuoxuqiushijian)
                result[guonei["fahuoxuqiushijian"][0]] = extract_split(fahuoxuqiushijian, target_paragraph.mapper[index:index+len(fahuoxuqiushijian)])
            else:
                result[guonei["fahuoxuqiushijian"][0]] = []
            # logger_online.info("交货地点:{0}".format(jiaohuodidian))
            if jiaohuodidian!=u"":
                pat_sheng = u'.{2,5}省'
                pat_shi = u'省?(.{2,3}市)'
                pat_xian = u'市(.{1,8}[区县])'
                pat_xiangxi = u'[区县](.+)'
                sheng = re.findall(pat_sheng,jiaohuodidian)
                # logger_online.info("省:{0}".format(sheng))
                # print(jiaohuodidian)
                if len(sheng)>0:
                    value = sheng[0]
                    index = content.find(value)
                    jiaohuodidian = jiaohuodidian[jiaohuodidian.find(value)+len(value)-2:]
                    result[guonei["jiaohuodidiansheng"][0]] = extract_split(value, target_paragraph.mapper[index:index + len(value)])
                else:
                    result[guonei["jiaohuodidiansheng"][0]] = []
                shi = re.findall(pat_shi, jiaohuodidian)
                # logger_online.info("市:{0}".format(shi))
                if len(shi) > 0:
                    value = shi[0]
                    index = content.find(value)
                    jiaohuodidian = jiaohuodidian[jiaohuodidian.find(value)+len(value)-2:]
                    # print(jiaohuodidian)
                    result[guonei["jiaohuodidianshi"][0]] = extract_split(value, target_paragraph.mapper[index:index + len(value)])
                else:
                    result[guonei["jiaohuodidianshi"][0]] = []
                    pat_xian = u'(.{1,8}[区县])'
                xian = re.findall(pat_xian, jiaohuodidian)
                # logger_online.info("县:{0}".format(xian))
                if len(xian) > 0:
                    value = xian[0]
                    index = content.find(value)
                    jiaohuodidian = jiaohuodidian[jiaohuodidian.find(value) + len(value) - 2:]
                    result[guonei["jiaohuodidianqu"][0]] = extract_split(value, target_paragraph.mapper[index:index + len(value)])
                else:
                    result[guonei["jiaohuodidianqu"][0]] = []
                    pat_xiangxi = u'[市区县](.+)'
                xiangxi = re.findall(pat_xiangxi, jiaohuodidian)
                # logger_online.info("详细:{0}".format(xiangxi))
                if len(xiangxi) > 0:
                    value = xiangxi[0]
                    index = content.find(value)
                    # print(value)
                    # print(content)
                    # print(index)
                    result[guonei["jiaohuodidianxiangqing"][0]] = extract_split(value, target_paragraph.mapper[
                                                                                index:index + len(value)])
                else:
                    result[guonei["jiaohuodidianxiangqing"][0]] = []
            else:
                result[guonei["jiaohuodidiansheng"][0]] = []
                result[guonei["jiaohuodidianshi"][0]] = []
                result[guonei["jiaohuodidianqu"][0]] = []
                result[guonei["jiaohuodidianxiangqing"][0]] = []
            if shouhuoren!=u"":
                index = content.find(shouhuoren)
                result[guonei["shouhuoren"][0]] = extract_split(shouhuoren, target_paragraph.mapper[index:index + len(shouhuoren)])
            else:
                result[guonei["shouhuoren"][0]] = []
            if shouhuolianxidianhua!=u"":
                shouhuolianxidianhua = shouhuolianxidianhua.replace(":"," ").replace("："," ").strip()
                pat_1 = u'[或,，；、/]'
                shouhuolianxidianhua = re.sub(pat_1,';',shouhuolianxidianhua).split(";")
                num_dict = {}
                result[guonei["shouhuolianxidianhua"][0]] = []
                for each in shouhuolianxidianhua:
                    value = each
                    index = content.find(value)
                    num = random_float()
                    while num in num_dict:
                        num = random_float()
                    extract_result = extract_split(value,target_paragraph.mapper[index:index + len(value)],num = num)
                    result[guonei["shouhuolianxidianhua"][0]] += extract_result
            else:
                result[guonei["shouhuolianxidianhua"][0]] = []
            if yunshufangshi!=u"":
                # print(yunshufangshi)
                index = content.find(yunshufangshi)
                result[guonei["yunshufangshi"][0]] = extract_split(yunshufangshi,target_paragraph.mapper[index:index + len(yunshufangshi)])
            else:
                result[guonei["yunshufangshi"][0]] = []

            # 返回已处理的部分内容
            result["due"] = due_paragraph_list(target_paragraph, index_dict)
            # print(result["due"])
            result["index"] = result["due"][-1]
        else:
            # 返回已处理的部分内容
            result["due"] = []
            # print(result["due"])
            result["index"] = 0
    else:
        # 返回已处理的部分内容
        result["due"] = []
        # print(result["due"])
        result["index"] = 0









    # 获取到目标句子
    # char_list = []
    # for each in meta_data_list:
    #     if isinstance(each,Table):
    #         continue
    #     text = each.text.replace(" ","").replace("_","").replace("、","").replace(",","").replace("。","")
    #     if has_most_word(content,text,num=0.7):
    #         char_list += each.chars
    # if len(char_list) > 0:
    #     target_paragraph = Paragraph(char_list)
    #     result[guonei["daohuoyanshou"][0]]=extract_split(target_paragraph.text,target_paragraph.mapper)
    #     # 返回已处理的部分内容
    #     result["due"] = due_paragraph_list(target_paragraph, index_dict)
    #     # print(result["due"])
    #     result["index"] = result["due"][-1]
    # else:
    #     result[guonei["daohuoyanshou"][0]] = []
    #     # 返回已处理的部分内容
    #     result["due"] = []
    #     # print(result["due"])
    #     result["index"] = 0

    return result

def extract_12(meta_data_list,content=u"供方发货时间供方备货完成后3日内发货"):
    '''
    第十二部分   供方发货时间条款
    :param meta_data_list:
    :return:
    '''
    result = {}
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    # 获取到目标句子
    char_list = []
    last_index = 0
    for index, each in enumerate(meta_data_list):
        # print(each)
        if isinstance(each,Table):
            continue
        if index - last_index > 2:
            break
        text = each.text.replace(" ","").replace("_","").replace("、","").replace(",","").replace("。","")
        if has_most_word(content,text,num=0.7):
            char_list += each.chars
            last_index = index
    if len(char_list) > 0:
        target_paragraph = Paragraph(char_list)
        result[guonei["gongfangfahuoshijian"][0]]=extract_split(target_paragraph.text,target_paragraph.mapper)
        # 返回已处理的部分内容
        result["due"] = due_paragraph_list(target_paragraph, index_dict)
        # print(result["due"])
        result["index"] = result["due"][-1]
    else:
        result[guonei["gongfangfahuoshijian"][0]] = []
        # 返回已处理的部分内容
        result["due"] = []
        # print(result["due"])
        result["index"] = 0

    return result

def extract_13(meta_data_list,content=u"运输费用承担方攻防指定的运输方式由供方承担如需方指定物流运输方式应在供方发货之日前提出且运输费用由需方承担"):
    '''
    第十三部分   运输费用承担方条款
    :param meta_data_list:
    :return:
    '''
    result = {}
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    # 获取到目标句子
    char_list = []
    last_index = 0
    for index, each in enumerate(meta_data_list):
        if isinstance(each,Table):
            continue
        if index - last_index > 2:
            break
        text = each.text.replace(" ","").replace("_","").replace("、","").replace(",","").replace("。","")
        if has_most_word(content,text,num=0.8):
            char_list += each.chars
            last_index = index
    if len(char_list) > 0:
        target_paragraph = Paragraph(char_list)
        result[guonei["yunshufeiyongchegndanfang"][0]]=extract_split(target_paragraph.text,target_paragraph.mapper)
        # 返回已处理的部分内容
        result["due"] = due_paragraph_list(target_paragraph, index_dict)
        # print(result["due"])
        result["index"] = result["due"][-1]
    else:
        result[guonei["yunshufeiyongchegndanfang"][0]] = []
        # 返回已处理的部分内容
        result["due"] = []
        # print(result["due"])
        result["index"] = 0

    return result

def extract_14(meta_data_list,content=u"质量保证供方在提供的产品发生质量问题依法提供退换保修各产品免费质保年限详见供方官方网站服务与下载-服务政策http://www.dahuatech.com,双方另有约定除外(须在备注处注明)"):
    '''
    第十四部分   质量保证条款
    :param meta_data_list:
    :return:
    '''
    result = {}
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    # 获取到目标句子
    char_list = []
    last_index = 0
    for index, each in enumerate(meta_data_list):
        if isinstance(each,Table):
            continue
        if index - last_index > 2:
            break
        text = each.text.replace(" ","").replace("_","").replace("、","").replace(",","")\
            .replace("。","").replace("“","").replace("”","").replace("，","").replace("：","")\
            .replace(":","").replace(";","").replace("；","").replace("\"","")
        if has_most_word(content,text,num=0.8):
            char_list += each.chars
            last_index = index
    if len(char_list) > 0:
        target_paragraph = Paragraph(char_list)
        result[guonei["zhiliangbaozheng"][0]]=extract_split(target_paragraph.text,target_paragraph.mapper)
        # 返回已处理的部分内容
        result["due"] = due_paragraph_list(target_paragraph, index_dict)
        # print(result["due"])
        result["index"] = result["due"][-1]
    else:
        result[guonei["zhiliangbaozheng"][0]] = []
        # 返回已处理的部分内容
        result["due"] = []
        # print(result["due"])
        result["index"] = 0

    return result

def extract_15(meta_data_list,content=u"本合同下甲方负责安装的甲方包括甲方委托或指定的第三方应严格按照以下要求安装1产品随机配备的说明书若乙方培训另有要求的以乙方培训内容为准2工程项目施工质量手册请参见乙方官方网http://www.dahuatech.com/服务支持3如仍存在安装疑义的请联系乙方代表如甲方未按照上述要求擅自更改安装方案造成质量安全事故的全部损失由甲方自行承担"):
    '''
    第十五部分   安装与服务条款
    :param meta_data_list:
    :return:
    '''
    result = {}
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    # 获取到目标句子
    char_list = []
    last_index = 0
    for index, each in enumerate(meta_data_list):
        if isinstance(each,Table):
            continue
        if index - last_index > 2:
            break
        pat_1 = u'[_、,。，：；:;\"“”（）\(\)\s]'
        text = re.sub(pat_1,'',each.text)
        # text = each.text.replace(" ","").replace("_","").replace("、","").replace(",","")\
        #     .replace("。","").replace("“","").replace("”","").replace("，","").replace("：","")\
        #     .replace(":","").replace(";","").replace("；","").replace("\"","")
        if has_most_word(content,text,num=0.8):
            char_list += each.chars
            last_index = index
    if len(char_list) > 0:
        target_paragraph = Paragraph(char_list)
        # print(target_paragraph)
        # print(content)
        result[guonei["anzhuangyufuwuzhichi"][0]]=extract_split(target_paragraph.text,target_paragraph.mapper)
        # 返回已处理的部分内容
        result["due"] = due_paragraph_list(target_paragraph, index_dict)
        # print(result["due"])
        result["index"] = result["due"][-1]
    else:
        result[guonei["anzhuangyufuwuzhichi"][0]] = []
        # 返回已处理的部分内容
        result["due"] = []
        # print(result["due"])
        result["index"] = 0

    return result

def extract_16(meta_data_list,content=u"发票开具时间供方发货完毕后日天内开具"):
    '''
    第十六部分   发票开具时间
    :param meta_data_list:
    :return:
    '''
    result = {}
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    # 获取到目标句子
    char_list = []
    last_index = 0
    for index, each in enumerate(meta_data_list):
        if isinstance(each,Table):
            continue
        if index - last_index > 2:
            break
        pat_1 = u'[_、,。，：；:;\"“”（）\(\)\s]'
        text = re.sub(pat_1,'',each.text)
        # print(text)
        # print(has_most_word(content,text,num=0.8))
        if has_most_word(content,text,num=0.8):
            char_list += each.chars
            last_index = index
    if len(char_list) > 0:
        target_paragraph = Paragraph(char_list)
        # print('---')
        # print(target_paragraph)
        pat_2 = u"完毕后(.{1,4}[日天])内"
        extract_result = re.findall(pat_2,target_paragraph.text)
        if len(extract_result)>0:
            value = extract_result[0]
            index = target_paragraph.text.find(value)
            result[guonei["fapiaokaijushijian"][0]]=extract_split(value,target_paragraph.mapper[index:index+len(value)])
        else:
            result[guonei["fapiaokaijushijian"][0]] = []
        # 返回已处理的部分内容
        result["due"] = due_paragraph_list(target_paragraph, index_dict)
        # print(result["due"])
        result["index"] = result["due"][-1]
    else:
        result[guonei["fapiaokaijushijian"][0]] = []
        # 返回已处理的部分内容
        result["due"] = []
        # print(result["due"])
        result["index"] = 0

    return result

def extract_17(meta_data_list,content=u"发票类型增值税普通发票增值税专用发票若需增值税专用发票请提供开票信息"):
    '''
    第十七部分   发票类型
    :param meta_data_list:
    :return:
    '''
    result = {}
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    # 获取到目标句子
    char_list = []
    last_index = 0
    for index, each in enumerate(meta_data_list):
        if isinstance(each,Table):
            continue
        if index - last_index > 2:
            break
        pat_1 = u'[_、,。，：；:;\"“”（）\(\)\s【】\dVv!]'
        text = re.sub(pat_1,'',each.text)
        # text = each.text.replace(" ","").replace("_","").replace("、","").replace(",","")\
        #     .replace("。","").replace("“","").replace("”","").replace("，","").replace("：","")\
        #     .replace(":","").replace(";","").replace("；","").replace("\"","")
        if has_most_word(text,content,num=0.8) or has_most_word(content,text,num=0.8):
            char_list += each.chars
            last_index = index
    if len(char_list) > 0:
        target_paragraph = Paragraph(char_list)
        # pat_2 = u'[一二三四五六七八九十、。\d]'
        # text = re.sub(pat_2,' ',target_paragraph.text)
        text = target_paragraph.text
        # text = target_paragraph.text
        index_flag = text.find(u"结款日期")
        if index_flag == -1:
            index_flag = len(text)
        value = text[:index_flag].strip()
        index = text.find(value)
        result[guonei["fapiaoleixing"][0]]=extract_split(target_paragraph.text[index:index+len(value)],target_paragraph.mapper[index:index+len(value)])
        # 返回已处理的部分内容
        result["due"] = due_paragraph_list(target_paragraph, index_dict)
        # print(result["due"])
        result["index"] = result["due"][-1]
    else:
        result[guonei["fapiaoleixing"][0]] = []
        # 返回已处理的部分内容
        result["due"] = []
        # print(result["due"])
        result["index"] = 0

    return result

def extract_18(meta_data_list):
    '''
    第十八部分   结款日期与结算方式
    :param meta_data_list:
    :return:
    '''
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    paragraph_all = paragraph_merge(meta_data_list)
    # print(paragraph_all)
    # 寻找目标
    result = {}
    if u"结款日期" in paragraph_all.text and u"支付方式" in paragraph_all.text:
        index_flag1 = paragraph_all.text.find(u"结款日期")
        index_flag2 = paragraph_all.text.find(u"支付方式")
        # 加入前面的序号
        pat_1 = u"[\d一二三四五六七八九十、\s]+$"
        index_flag3 = re.findall(pat_1,paragraph_all.text[:index_flag1])
        if len(index_flag3) > 0:
            index_flag1 -= len(index_flag3[0])
        # 去除后面的序号
        index_flag4 = re.findall(pat_1, paragraph_all.text[index_flag1:index_flag2])
        if len(index_flag4) > 0:
            index_flag2 -= len(index_flag4[0])

        target_paragraph = Paragraph(paragraph_all.chars[index_flag1:index_flag2])
        # print(target_paragraph)
        result[guonei["jkrqjjsfs"][0]] = extract_split(target_paragraph.text,target_paragraph.mapper)
        # 返回已处理的部分内容
        result["due"] = due_paragraph_list(target_paragraph, index_dict)
        # print(result["due"])
        result["index"] = result["due"][-1]
        # print("1:{0}".format(meta_data_list[result["index"]]))
    else:
        result[guonei["jkrqjjsfs"][0]] = []
        result["index"] = 0
        result["due"] = []
    return result

def extract_19(meta_data_list):
    '''
    第十九部分   支付方式   zhifufangshi
    :param meta_data_list:
    :return:
    '''
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    paragraph_all = paragraph_merge(meta_data_list)
    # print(paragraph_all)
    # 寻找目标
    result = {}
    if u"支付方式" in paragraph_all.text and u"退货约定" in paragraph_all.text:
        index_flag1 = paragraph_all.text.find(u"支付方式")
        index_flag2 = paragraph_all.text.find(u"退货约定")
        # 加入前面的序号
        pat_1 = u"[\d一二三四五六七八九十、\s]+$"
        index_flag3 = re.findall(pat_1, paragraph_all.text[:index_flag1])
        if len(index_flag3) > 0:
            index_flag1 -= len(index_flag3[0])
        # 去除后面的序号
        index_flag4 = re.findall(pat_1, paragraph_all.text[index_flag1:index_flag2])
        if len(index_flag4) > 0:
            index_flag2 -= len(index_flag4[0])
        target_paragraph = Paragraph(paragraph_all.chars[index_flag1:index_flag2])
        # print(target_paragraph)
        result[guonei["zhifufangshi"][0]] = extract_split(target_paragraph.text, target_paragraph.mapper)
        # 返回已处理的部分内容
        result["due"] = due_paragraph_list(target_paragraph, index_dict)
        # print(result["due"])
        result["index"] = result["due"][-1]
        # print("1:{0}".format(meta_data_list[result["index"]]))
    else:
        result[guonei["zhifufangshi"][0]] = []
        result["index"] = 0
        result["due"] = []
    return result

def extract_20(meta_data_list,content=u"退货约定：非质量原因供方原则上不接受退货，供方同意退货的，需方按照供方要求支付退货费用后，双方签订退货协议；否则，需方不得以退货为由，拒绝履行付款义务。对于已开发票的退货，需方必须退回发票或提供红字开票通知单。"):
    '''
    第二十部分   退货约定   tuihuoyueding
    :param meta_data_list:
    :return:
    '''
    result = {}
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    # 获取到目标句子
    char_list = []
    last_index = 0
    for index, each in enumerate(meta_data_list):
        if isinstance(each, Table):
            continue
        # print(each)
        pat_1 = u'[_、,。，：；:;\"“”（）\(\)\s]'
        text = re.sub(pat_1, '', each.text)
        # text = each.text.replace(" ","").replace("_","").replace("、","").replace(",","")\
        #     .replace("。","").replace("“","").replace("”","").replace("，","").replace("：","")\
        #     .replace(":","").replace(";","").replace("；","").replace("\"","")
        if index - last_index > 2:
            break
        if (has_most_word(text, content, num=0.8) or has_most_word(content, text, num=0.8)):
            char_list += each.chars
            last_index = index
    if len(char_list) > 0:
        target_paragraph = Paragraph(char_list)
        # pat_2 = u'[一二三四五六七八九十、。\d]'
        # text = re.sub(pat_2,' ',target_paragraph.text)
        text = target_paragraph.text
        # text = target_paragraph.text
        index_flag = text.find(u"违约责任")
        if index_flag == -1:
            index_flag = len(text)
        value = text[:index_flag].strip()
        index = text.find(value)
        result[guonei["tuihuoyueding"][0]] = extract_split(target_paragraph.text[index:index + len(value)],
                                                           target_paragraph.mapper[index:index + len(value)])
        # 返回已处理的部分内容
        result["due"] = due_paragraph_list(Paragraph(target_paragraph.chars[index:index + len(value)]), index_dict)
        print(result["due"])
        result["index"] = result["due"][-1]
    else:
        result[guonei["tuihuoyueding"][0]] = []
        # 返回已处理的部分内容
        result["due"] = []
        # print(result["due"])
        result["index"] = 0

    return result

def extract_21(meta_data_list,content=u"15、违约责任：1)任何一方不履行本合同义务或履行本合同义务不符合约定的，均属于违约行为。违约方应向守约方支付合同总金额20%作为违约金，并应对守约方因此造成的损失承担赔偿责任。本合同另有规定的除外。2)由于供方原因，未能按合同约定向需方交货，供方应向需方支付迟延履行违约金。每迟延1日，供方应向需方支付相当于迟延交付货物货款的1‰作为迟延履行违约金，但迟延履行违约金总额不超过合同总金额的20%。3)由于需方原因，未能按合同约定付款，需方应向供方支付违约金。每迟延1日，需方应向供方支付相当于迟延支付货款总额的1‰作为迟延履行违约金，但迟延履行违约金总额不超过合同总金额的20%。同时，交货期相应顺延。需方迟延付款超过30个自然日，供方有权解除合同。4)货款必须汇到供方书面指定的银行帐号，否则，视为需方未按合同约定履行付款义务，供方有权要求需方继续履行付款义务，并追究需方逾期付款的违约责任。本合同约定交货方式、收货地点有误或变更，须需方提供盖章书面文件通知供方，由此产生的费用由需方承担。因需方通知有误或通知不及时，致使本合同交货出现的问题，供方不承担任何责任；"):
    '''
    第二十一部分   违约责任   weiyuezeren
    :param meta_data_list:
    :return:
    '''
    result = {}
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    # 获取到目标句子
    char_list = []
    last_index = 0
    for index, each in enumerate(meta_data_list):
        if isinstance(each, Table):
            continue
        if index - last_index > 2:
            break
        pat_1 = u'[_、,。，：；:;\"“”（）\(\)\s]'
        text = re.sub(pat_1, '', each.text)
        # text = each.text.replace(" ","").replace("_","").replace("、","").replace(",","")\
        #     .replace("。","").replace("“","").replace("”","").replace("，","").replace("：","")\
        #     .replace(":","").replace(";","").replace("；","").replace("\"","")
        if has_most_word(text, content, num=0.8) or has_most_word(content, text, num=0.8):
            char_list += each.chars
            last_index = index
    print(char_list)
    if len(char_list) > 0:
        target_paragraph = Paragraph(char_list)
        print(target_paragraph)
        # pat_2 = u'[一二三四五六七八九十、。\d]'
        # text = re.sub(pat_2,' ',target_paragraph.text)
        text = target_paragraph.text
        # text = target_paragraph.text
        index_flag = text.find(u"当事人一方因")
        if index_flag == -1:
            index_flag = len(text)
        value = text[:index_flag].strip()
        index = text.find(value)
        result[guonei["weiyuezeren"][0]] = extract_split(target_paragraph.text[index:index + len(value)],
                                                           target_paragraph.mapper[index:index + len(value)])
        # 返回已处理的部分内容
        result["due"] = due_paragraph_list(target_paragraph, index_dict)
        # print(result["due"])
        result["index"] = result["due"][-1]
    else:
        result[guonei["weiyuezeren"][0]] = []
        # 返回已处理的部分内容
        result["due"] = []
        # print(result["due"])
        result["index"] = 0

    return result

def extract_22(meta_data_list,content=u"当事人一方因不可抗力而不能履行合同时，应当及时通知对方，并在合理期限内提供有关机构出具的证明，可以全部或部分免除该方当事人的责任。"):
    '''
    第二十二部分   不可抗力   bukekangli
    :param meta_data_list:
    :return:
    '''
    result = {}
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    # 获取到目标句子
    char_list = []
    last_index = 0
    for index, each in enumerate(meta_data_list):
        if isinstance(each, Table):
            continue
        if index - last_index > 2:
            break
        pat_1 = u'[_、,。，：；:;\"“”（）\(\)\s]'
        text = re.sub(pat_1, '', each.text)
        # text = each.text.replace(" ","").replace("_","").replace("、","").replace(",","")\
        #     .replace("。","").replace("“","").replace("”","").replace("，","").replace("：","")\
        #     .replace(":","").replace(";","").replace("；","").replace("\"","")
        if has_most_word(text, content, num=0.8) or has_most_word(content, text, num=0.8):
            char_list += each.chars
            last_index = index
    if len(char_list) > 0:
        target_paragraph = Paragraph(char_list)
        # pat_2 = u'[一二三四五六七八九十、。\d]'
        # text = re.sub(pat_2,' ',target_paragraph.text)
        text = target_paragraph.text
        # text = target_paragraph.text
        index_flag = text.find(u"解决合同纠纷")
        if index_flag == -1:
            index_flag = len(text)
        value = text[:index_flag].strip()
        index = text.find(value)
        result[guonei["bukekangli"][0]] = extract_split(target_paragraph.text[index:index + len(value)],
                                                         target_paragraph.mapper[index:index + len(value)])
        # 返回已处理的部分内容
        result["due"] = due_paragraph_list(target_paragraph, index_dict)
        # print(result["due"])
        result["index"] = result["due"][-1]
    else:
        result[guonei["bukekangli"][0]] = []
        # 返回已处理的部分内容
        result["due"] = []
        # print(result["due"])
        result["index"] = 0

    return result

def extract_23(meta_data_list):
    '''
    第二十三部分   解决合同纠纷   hetongjiufen1   hetongjiufen2   hetongjiufen3
    :param meta_data_list:
    :return:
    '''
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    paragraph_all = paragraph_merge(meta_data_list)
    # print(paragraph_all)
    # 寻找目标
    result = {}
    result["due"] = []
    result["index"] = 0
    if u"解决合同" in paragraph_all.text and u"需方明确" in paragraph_all.text:
        index_flag1 = paragraph_all.text.find(u"解决合同")
        index_flag2 = paragraph_all.text.find(u"需方明确")
        # 加入前面的序号
        pat_1 = u"[\d一二三四五六七八九十、\s]+$"
        index_flag3 = re.findall(pat_1, paragraph_all.text[:index_flag1])
        if len(index_flag3) > 0:
            index_flag1 -= len(index_flag3[0])
        # 去除后面的序号
        index_flag4 = re.findall(pat_1, paragraph_all.text[index_flag1:index_flag2])
        if len(index_flag4) > 0:
            index_flag2 -= len(index_flag4[0])

        target_paragraph = Paragraph(paragraph_all.chars[index_flag1:index_flag2])
        # print(target_paragraph)
        result[guonei["hetongjiufen1"][0]] = extract_split(target_paragraph.text, target_paragraph.mapper)
        # 返回已处理的部分内容
        result["due"] += due_paragraph_list(target_paragraph, index_dict)
        result["due"].sort()
        # print(result["due"])
        result["index"] = result["due"][-1]
        # print("1:{0}".format(meta_data_list[result["index"]]))
    else:
        result[guonei["hetongjiufen1"][0]] = []
        # result["index"] = 0
        # result["due"] = []
    if u"需方明确" in paragraph_all.text and u"因载明的" in paragraph_all.text:
        index_flag1 = paragraph_all.text.find(u"需方明确")
        index_flag2 = paragraph_all.text.find(u"因载明的")
        # 加入前面的序号
        pat_1 = u"[\d一二三四五六七八九十、\s]+$"
        index_flag3 = re.findall(pat_1, paragraph_all.text[:index_flag1])
        if len(index_flag3) > 0:
            index_flag1 -= len(index_flag3[0])
        # 去除后面的序号
        index_flag4 = re.findall(pat_1, paragraph_all.text[index_flag1:index_flag2])
        if len(index_flag4) > 0:
            index_flag2 -= len(index_flag4[0])

        target_paragraph = Paragraph(paragraph_all.chars[index_flag1:index_flag2])
        # print(target_paragraph)
        result[guonei["hetongjiufen2"][0]] = extract_split(target_paragraph.text, target_paragraph.mapper)
        # 返回已处理的部分内容
        result["due"] += due_paragraph_list(target_paragraph, index_dict)
        result["due"].sort()
        # print(result["due"])
        result["index"] = result["due"][-1]
    else:
        result[guonei["hetongjiufen2"][0]] = []
    if u"因载明的" in paragraph_all.text and u"合同执行期间" in paragraph_all.text:
        index_flag1 = paragraph_all.text.find(u"因载明的")
        index_flag2 = paragraph_all.text.find(u"合同执行期间")
        # 加入前面的序号
        pat_1 = u"[\d一二三四五六七八九十、\s]+$"
        index_flag3 = re.findall(pat_1, paragraph_all.text[:index_flag1])
        if len(index_flag3) > 0:
            index_flag1 -= len(index_flag3[0])
        # 去除后面的序号
        index_flag4 = re.findall(pat_1, paragraph_all.text[index_flag1:index_flag2])
        if len(index_flag4) > 0:
            index_flag2 -= len(index_flag4[0])

        target_paragraph = Paragraph(paragraph_all.chars[index_flag1:index_flag2])
        # print(target_paragraph)
        result[guonei["hetongjiufen3"][0]] = extract_split(target_paragraph.text, target_paragraph.mapper)
        # 返回已处理的部分内容
        result["due"] += due_paragraph_list(target_paragraph, index_dict)
        result["due"].sort()
        # print(result["due"])
        result["index"] = result["due"][-1]
    else:
        result[guonei["hetongjiufen3"][0]] = []
    return result

def extract_24(meta_data_list,content=u"合同执行期间，如因故不能履行或需要修改，必须经双方同意，并签订补充协议或另订合同，方为有效。"):
    '''
    第二十四部分   合同修订   hetongxiuding
    :param meta_data_list:
    :return:
    '''
    result = {}
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    # 获取到目标句子
    char_list = []
    last_index = 0
    for index, each in enumerate(meta_data_list):
        if isinstance(each, Table):
            continue
        if index - last_index > 2:
            break
        pat_1 = u'[_、,。，：；:;\"“”（）\(\)\s]'
        text = re.sub(pat_1, '', each.text)
        # text = each.text.replace(" ","").replace("_","").replace("、","").replace(",","")\
        #     .replace("。","").replace("“","").replace("”","").replace("，","").replace("：","")\
        #     .replace(":","").replace(";","").replace("；","").replace("\"","")
        if has_most_word(text, content, num=0.8) or has_most_word(content, text, num=0.8):
            char_list += each.chars
            last_index = index
    if len(char_list) > 0:
        target_paragraph = Paragraph(char_list)
        # pat_2 = u'[一二三四五六七八九十、。\d]'
        # text = re.sub(pat_2,' ',target_paragraph.text)
        text = target_paragraph.text
        # text = target_paragraph.text
        index_flag = text.find(u"本合同一式")
        if index_flag == -1:
            index_flag = len(text)
        value = text[:index_flag].strip()
        index = text.find(value)
        result[guonei["hetongxiuding"][0]] = extract_split(target_paragraph.text[index:index + len(value)],
                                                        target_paragraph.mapper[index:index + len(value)])
        # 返回已处理的部分内容
        result["due"] = due_paragraph_list(target_paragraph, index_dict)
        # print(result["due"])
        result["index"] = result["due"][-1]
    else:
        result[guonei["hetongxiuding"][0]] = []
        # 返回已处理的部分内容
        result["due"] = []
        # print(result["due"])
        result["index"] = 0

    return result

def extract_25(meta_data_list,content=u"本合同一式肆份，自双方盖章之日起生效，双方各执贰份，具有同等法律效力。"):
    '''
    第二十五部分   合同份数   hetongfenshu
    :param meta_data_list:
    :return:
    '''
    result = {}
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    # 获取到目标句子
    char_list = []
    last_index = 0
    for index, each in enumerate(meta_data_list):
        if isinstance(each, Table):
            continue
        if index - last_index > 2:
            break
        pat_1 = u'[_、,。，：；:;\"“”（）\(\)\s]'
        text = re.sub(pat_1, '', each.text)
        # text = each.text.replace(" ","").replace("_","").replace("、","").replace(",","")\
        #     .replace("。","").replace("“","").replace("”","").replace("，","").replace("：","")\
        #     .replace(":","").replace(";","").replace("；","").replace("\"","")
        if has_most_word(text, content, num=0.8) or has_most_word(content, text, num=0.8):
            char_list += each.chars
            last_index = index
    if len(char_list) > 0:
        target_paragraph = Paragraph(char_list)
        # pat_2 = u'[一二三四五六七八九十、。\d]'
        # text = re.sub(pat_2,' ',target_paragraph.text)
        text = target_paragraph.text
        # text = target_paragraph.text
        index_flag = text.find(u"特别约定")
        if index_flag == -1:
            index_flag = len(text)
        value = text[:index_flag].strip()
        index = text.find(value)
        result[guonei["hetongfenshu"][0]] = extract_split(target_paragraph.text[index:index + len(value)],
                                                           target_paragraph.mapper[index:index + len(value)])
        # 返回已处理的部分内容
        result["due"] = due_paragraph_list(target_paragraph, index_dict)
        # print(result["due"])
        result["index"] = result["due"][-1]
    else:
        result[guonei["hetongfenshu"][0]] = []
        # 返回已处理的部分内容
        result["due"] = []
        # print(result["due"])
        result["index"] = 0

    return result

def extract_26(meta_data_list,content=u"特别约定需方理解，遵守适用的法律法规，包括美国出口管制法律的规定，是供方基本的公司政策。需方承诺，针对从供方及其关联人处购买的货物，需方将遵守相关的进口、出口、再出口的法律法规，具体要求包括但不限于： 1）需方承诺，这些货物不会被用于被任何适用法律禁止的最终用途，包括化学武器、生物武器、核武器、导弹以及其他军用项目的设计、开发、生产、存储或使用； 2）需方理解，如果货物含有源自美国的物品（U.S. Origin Items）,该等货物（“管制货物”）可能受到美国出口管制条例（Export Administration Regulation，或EAR）的管辖。需方承诺，在管制货物的出口和再出口时，遵守相关的法律要求，包括，按照EAR或其他适用法律的要求，例如向美国政府申请获得出口许可； 3）需方承诺，不会把管制货物转售给被美国或欧盟制裁的国家、实体或个人，包括但不限于美国财政部外国资产控制办公室管理的“特别指定国民及受封锁人士”清单（Specially Designated Nationals and Blocked Persons List）和美国商务部工业和安全局管理的“拒绝交易对象”（Denied Persons List）与“实体清单”（ Entity List）以及受到欧盟金融制裁的欧盟人士、集团和实体综合清单上的个人或实体； 4）需方承诺，对管制货物的使用和处理不会违反适用的法律法规。"):
    '''
    第二十六部分   特别约定   tebieyueding
    :param meta_data_list:
    :return:
    '''
    result = {}
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    # 获取到目标句子
    char_list = []
    last_index = 0
    for index, each in enumerate(meta_data_list):
        if isinstance(each, Table):
            continue
        if index - last_index > 2:
            break
        pat_1 = u'[_、,。，：；:;\"“”（）\(\)\s]'
        text = re.sub(pat_1, '', each.text)
        # text = each.text.replace(" ","").replace("_","").replace("、","").replace(",","")\
        #     .replace("。","").replace("“","").replace("”","").replace("，","").replace("：","")\
        #     .replace(":","").replace(";","").replace("；","").replace("\"","")
        if has_most_word(text, content, num=0.8) or has_most_word(content, text, num=0.8):
            char_list += each.chars
            last_index = index
    if len(char_list) > 0:
        target_paragraph = Paragraph(char_list)
        # pat_2 = u'[一二三四五六七八九十、。\d]'
        # text = re.sub(pat_2,' ',target_paragraph.text)
        text = target_paragraph.text
        # text = target_paragraph.text
        index_flag = text.find(u"供方收款账号")
        if index_flag == -1:
            index_flag = len(text)
        value = text[:index_flag].strip()
        index = text.find(value)
        result[guonei["tebieyueding"][0]] = extract_split(target_paragraph.text[index:index + len(value)],
                                                          target_paragraph.mapper[index:index + len(value)])
        # 返回已处理的部分内容
        result["due"] = due_paragraph_list(target_paragraph, index_dict)
        # print(result["due"])
        result["index"] = result["due"][-1]
    else:
        result[guonei["tebieyueding"][0]] = []
        # 返回已处理的部分内容
        result["due"] = []
        # print(result["due"])
        result["index"] = 0

    return result

def extract_27(meta_data_list):
    '''
    第二十七部分   表格2
    xufanggaizhang         gongfanggaizhang
    lianxiren3             lianxirengongfang
    hetongqiandingriqi1    hetongqiandingriqi2
    zhanghumingcheng1      zhanghumingcheng2
    kaihuyinhang1          kaihuyinhang2
    yinhangzhanghu1        yinhangzhanghu2
    shuihao1               shuihao2
    dizhidianhua1          dizhidianhua2

    :param meta_data_list:
    :return:
    '''
    result = {
        guonei["xufanggaizhang"][0]:[],
        guonei["gongfanggaizhang"][0]: [],
        guonei["lianxiren3"][0]: [],
        guonei["lianxirengongfang"][0]: [],
        guonei["hetongqiandingriqi1"][0]: [],
        guonei["hetongqiandingriqi2"][0]: [],
        guonei["zhanghumingcheng1"][0]: [],
        guonei["zhanghumingcheng2"][0]: [],
        guonei["kaihuyinhang1"][0]: [],
        guonei["kaihuyinhang2"][0]: [],
        guonei["yinhangzhanghu1"][0]: [],
        guonei["yinhangzhanghu2"][0]: [],
        guonei["shuihao1"][0]: [],
        guonei["shuihao2"][0]: [],
        guonei["dizhidianhua1"][0]: [],
        guonei["dizhidianhua2"][0]: [],
    }
    # 防止有跨页表格
    table_list = []
    for index, each in enumerate(meta_data_list):
        if isinstance(each, Table):
            table_list.append(each)
    # 找到最后一个表格所在的位置
    for index, each in enumerate(meta_data_list[::-1]):
        if isinstance(each, Table):
            result["index"] = len(meta_data_list) - index - 1
    # 获取所有的行
    all_cells = []
    for each_table in table_list:
        for each_line in each_table.cells:
            if len(each_line) >= 4:
                all_cells.append(each_line)
    # 获取数据
    def table_data_deal(line,result,key_word_list=u"",name_list=[]):
        index1 = -1
        index2 = -1
        for index, each_cell in enumerate(line):
            if has_most_word(each_cell.text,key_word_list,num=0.9):
                if index1 < 0:
                    index1 = index
                else:
                    index2 = index
                    break
        if index1 >= 0 and index2 >= 0:
            text = u""
            mapper = []
            for each in line[index1 + 1:index2]:
                text += each.text
                mapper += each.mapper
            result[guonei[name_list[0]][0]] = extract_split(text,mapper)
            text = u""
            mapper = []
            for each in line[index2 + 1:]:
                text += each.text
                mapper += each.mapper
            result[guonei[name_list[1]][0]] = extract_split(text, mapper)


    # 需方盖章  供方盖章
    if len(all_cells) > 0:
        table_data_deal(all_cells[0],result,key_word_list=u"盖章",name_list=["xufanggaizhang","gongfanggaizhang"])
    # 联系人  联系人
    if len(all_cells) > 1:
        table_data_deal(all_cells[1], result, key_word_list=u"联系人", name_list=["lianxiren3", "lianxirengongfang"])
    # 合同签订日期
    if len(all_cells) > 2:
        table_data_deal(all_cells[2], result, key_word_list=u"签订", name_list=["hetongqiandingriqi1", "hetongqiandingriqi2"])
    # 账户名称
    if len(all_cells) > 3:
        table_data_deal(all_cells[3], result, key_word_list=u"账户名称", name_list=["zhanghumingcheng1", "zhanghumingcheng2"])
    # 开户银行
    if len(all_cells) > 4:
        table_data_deal(all_cells[4], result, key_word_list=u"开户银行", name_list=["kaihuyinhang1", "kaihuyinhang2"])
    # 银行账户
    if len(all_cells) > 5:
        table_data_deal(all_cells[5], result, key_word_list=u"银行账户", name_list=["yinhangzhanghu1", "yinhangzhanghu2"])
    # 税号
    if len(all_cells) > 6:
        table_data_deal(all_cells[6], result, key_word_list=u"税号", name_list=["shuihao1", "shuihao2"])
    # 地址电话
    if len(all_cells) > 7:
        table_data_deal(all_cells[7], result, key_word_list=u"地址电话", name_list=["dizhidianhua1", "dizhidianhua2"])




    return result

def extract_28(meta_data_list):
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
    result={
        guonei["dianhuikaihuhang"][0]: [],
        guonei["dianhuizhanghao"][0]: [],
        guonei["dianhuihanghao"][0]: [],
        guonei["chengduikaihuhang"][0]: [],
        guonei["chengduizhanghao"][0]: [],
        guonei["chengduihanghao"][0]: [],
    }
    # 获取index字典 以及 整合后的段落对象
    index_dict = index_to_paragraph_num(meta_data_list)
    paragraph_all = paragraph_merge(meta_data_list)
    # 去掉水印识别错误部分
    # chars = []
    # for each in paragraph_all.chars:
    #     if each.get_data()["x"] > 8000:
    #         continue
    #     else:
    #         chars.append(each)
    # paragraph_all = Paragraph(chars)
    char_dict = dict()
    char_list = list()
    for each in paragraph_all.chars:
        y = each.get_data()["y"]
        if y in char_list:
            continue
        if y not in char_dict:
            char_dict[y] = 1
        else:
            char_dict[y] += 1
        if char_dict[y]>3:
            char_list.append(y)
    chars = []
    for each in paragraph_all.chars:
        if each.get_data()["y"] in char_list:
            chars.append(each)
    paragraph_all = Paragraph(chars)


    pat_1 = u"开户行及账号:(.{3,10}行[\s\d]+)行号"
    pat_2 = u"行号:(\d+)"
    result1 = (re.findall(pat_1,paragraph_all.text))
    result2 = (re.findall(pat_2, paragraph_all.text))
    if len(result1) ==2:
        value1 = re.sub(u"[\d\s]","",result1[0])
        index1 = paragraph_all.text.find(value1)
        result[guonei["dianhuikaihuhang"][0]] = extract_split(value1,paragraph_all.mapper[index1:index1+len(value1)])

        value2 = re.sub(u"[\d\s]","",result1[1])
        index2 = paragraph_all.text.find(value2)
        result[guonei["chengduikaihuhang"][0]] = extract_split(value2, paragraph_all.mapper[index2:index2 + len(value2)])

        value3 = result1[0].split(u"行")[-1]
        index3 = paragraph_all.text.find(value3)
        result[guonei["dianhuizhanghao"][0]] = extract_split(value3, paragraph_all.mapper[index3:index3 + len(value3)])

        value4 = result1[1].split(u"行")[-1]
        index4 = paragraph_all.text.find(value4)
        result[guonei["chengduizhanghao"][0]] = extract_split(value4, paragraph_all.mapper[index4:index4 + len(value4)])
    elif len(result1) ==1:
        if u"电汇" in paragraph_all.text:
            value1 = re.sub(u"[\d\s]", "", result1[0])
            index1 = paragraph_all.text.find(value1)
            result[guonei["dianhuikaihuhang"][0]] = extract_split(value1,
                                                                  paragraph_all.mapper[index1:index1 + len(value1)])
            value3 = result1[0].split(u"行")[-1]
            index3 = paragraph_all.text.find(value3)
            result[guonei["dianhuizhanghao"][0]] = extract_split(value3,
                                                                 paragraph_all.mapper[index3:index3 + len(value3)])
        else:
            value1 = re.sub(u"[\d\s]", "", result1[0])
            index1 = paragraph_all.text.find(value1)
            result[guonei["chengduikaihuhang"][0]] = extract_split(value1,
                                                                  paragraph_all.mapper[index1:index1 + len(value1)])
            value3 = result1[0].split(u"行")[-1]
            index3 = paragraph_all.text.find(value3)
            result[guonei["chengduizhanghao"][0]] = extract_split(value3,
                                                                 paragraph_all.mapper[index3:index3 + len(value3)])

    if len(result2) == 2:
        value1 = result2[0]
        index1 = paragraph_all.text.find(value1)
        result[guonei["dianhuihanghao"][0]] = extract_split(value1, paragraph_all.mapper[index1:index1 + len(value1)])

        value2 = result2[1]
        index2 = paragraph_all.text.find(value2)
        result[guonei["chengduihanghao"][0]] = extract_split(value2, paragraph_all.mapper[index2:index2 + len(value2)])
    elif len(result2) ==1:
        if u"电汇" in paragraph_all.text:
            value1 = result2[0]
            index1 = paragraph_all.text.find(value1)
            result[guonei["dianhuihanghao"][0]] = extract_split(value1,
                                                                paragraph_all.mapper[index1:index1 + len(value1)])
        else:
            value1 = result2[0]
            index1 = paragraph_all.text.find(value1)
            result[guonei["chengduihanghao"][0]] = extract_split(value1,
                                                                paragraph_all.mapper[index1:index1 + len(value1)])




    # 寻找目标
    # result = {}
    # result[guonei["gongfangshoukuanzhanghaoxinxi"][0]]=[]
    # result["index"] = 0
    # result["due"] = []
    return result


if __name__ == "__main__":
    # extract_split("一二三四五六七八九十一二三四五",[1,2,3,4,5,7,8,9,11,15,16,6,98,34,35])
    # pat_2 = u"[省市_]{1,3}\s?(.+)项目,?合同"
    # pat_3 = u"评审编号为(.+),?以资双方"
    # a = '供需双方本着平等互利、协商一致的原则,签订本合同,需方保证所订货物用于 湖北省_省 武汉市东湖高新技术开发区光谷大道二期智能交通设备采购工程项目,合同评审编号为1-3068609605,以资双方信守执行。'
    # print(u"供需双方本着" in a and u"信守执行" in a)
    # b = re.findall(pat_2, a)
    # print(b)
    pass