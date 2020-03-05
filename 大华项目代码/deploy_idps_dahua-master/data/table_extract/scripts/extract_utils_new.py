#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/12/27 10:18
import os, sys, re, json, traceback, time, copy, random
from pdf2txt_decoder.pdf2txt_decoder import Pdf2TxtDecoder
from document_beans.table import Table
from document_beans.paragraph import Paragraph
from field_conf import guonei

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

def paragraph_delete(meta_data_list):
    """
    疑似页眉页脚删除
    处理逻辑，去除所有页眉页脚有关的关键字，剩余长度小于制定长度的则去除
    1. 的确去除了东西
    2. 剩余的长度较短
    3. 不含有制定字样  暂时不做判定

    :param meta_data_list:
    :return:
    """
    meta_data_list_due = []
    for each in meta_data_list:
        if isinstance(each,Table):
            meta_data_list_due.append(each)
        else:
            content = each.text
            if has_most_word(content, [u"于", u"传真", u"电话"], num=0):
                meta_data_list_due.append(each)
                continue
            pat_1 = u'[浙江大华科技有限公司需方合同编号设备购销供\sa-zA-z\d]+'
            content_after_re = re.sub(pat_1, u"", content)
            # print(content)
            # print(content_after_re)
            if (len(content) - len(content_after_re) > 4 and len(content_after_re) < 5) or len(content) < 5:
                # print(each.text)
                pass
            else:
                meta_data_list_due.append(each)
    return meta_data_list_due

def get_paragraph_delete(meta_data_list):
    """
    疑似页眉页脚  提取
    处理逻辑，去除所有页眉页脚有关的关键字，剩余长度小于制定长度的则去除
    1. 的确去除了东西
    2. 剩余的长度较短
    3. 不含有制定字样  暂时不做判定

    :param meta_data_list:
    :return:
    """
    delete_mapper_list = []
    for each in meta_data_list:
        if isinstance(each,Table):
            pass
        else:

            content = each.text
            if has_most_word(content, [u"于", u"传真", u"电话", u"行号", u"货"], num=0):
                print(content)
                continue
            pat_1 = u'[浙江大华科技有限公司需方合同编号设备购销供\sa-zA-z\d]+'
            content_after_re = re.sub(pat_1, u"", content)
            # print(content)
            # print(content_after_re)
            if (len(content) - len(content_after_re) > 4 and len(content_after_re) < 5) or len(content) < 5:
                # print("[删除]", end="")
                delete_mapper_list += each.mapper
                pass
            print(content)

    return delete_mapper_list

def extract_split(value,mapper,num=1):
    """
    将value,mapper形式的数据转换成抽取的结果
    :param value:
    :param mapper:
    :param num:
    :return:
    """
    # print(value)
    # print(mapper)
    # 长度判定及首尾不合法字符去除
    if len(value) == 0 or len(mapper) == 0 or len(value) != len(mapper):
        return []
    pat_before = u"^[\(\)_\s]+"   # 首部括号下划线空格的去除
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
    if len(value) == 0 or len(mapper) == 0 or len(value) != len(mapper):
        return []
    '''
    抽取结果拆分    应对句子各种问题
    '''
    # 每个index在mapper中的位置
    # mapper_dict = {}
    # for index, each in enumerate(mapper):
    #     mapper_dict[each] = index
    # 排序处理   并非一定要进行排序，原顺序整合也可以  是真的不需要排序，保持文字的顺序不变
    mapper_sort = copy.deepcopy(mapper)
    # mapper_sort.sort()
    # 整合处理  将连号放在一起
    merge_result = []
    start = mapper_sort[0]
    end = mapper_sort[0]
    index = 1
    while index < len(mapper_sort):
        if mapper_sort[index] == end + 1:
            end = mapper_sort[index]
        else:
            merge_result.append([start, end])
            start = mapper_sort[index]
            end = mapper_sort[index]
        index += 1
    merge_result.append([start, end])
    # print(merge_result)
    # 改为 start,len 的形式
    for each in merge_result:
        each[1] = each[1] - each[0] + 1
    # 最终转换
    result = []
    index = 0
    for each in merge_result:
        each_value = value[index:index+each[1]]
        index = index+each[1]
        result.append([each_value, num, each[0]])
    # print(result)
    return result

def random_float():
    """
    随机一个0.7以上1以下的小数
    :return:
    """
    num = int((random.random() * 0.3 + 0.7) * 10000) / 10000.0
    return num

def paragraph_merge(meta_data_list, delete_prun = False, prun_str = u" _；;:：，,.·"):
    char_list = []
    for each in meta_data_list:
        char_list += each.chars
    if not delete_prun:
        return Paragraph(char_list)
    char_list_delete_prun = []
    for each in char_list:
        if each.get_data()["str"] in prun_str:
            continue
        else:
            char_list_delete_prun.append(each)
    return Paragraph(char_list_delete_prun)


def find_target_paragraph_by_after_word(meta_data_list, after_word, after_word_per, end_index=10, delete_prun = False,
                                        prun_str = u" _；;:：，,.·", before_word = None, before_word_per=0):
    """
    从起始位置开始，根据结束的位置特征来确定结尾，最终收获一个paragraph
    :return:
    """
    # 如果有前置，则先考虑前置
    index_start = 0
    if before_word:
        while index_start < min(len(meta_data_list), end_index):
            if isinstance(meta_data_list[index_start], Table):
                index_start += 1
                continue
            else:
                para_text = meta_data_list[index_start].text
                # 如果找到含有目标文字的段落  这里存在一个问题就是上一个和下一个并没有分成两个段落
                # 也就是说这个段落里面既有有效信息也有无效信息
                # print(para_text, after_word)
                # print(para_text)
                if has_most_word(para_text, before_word, num=before_word_per):
                    break
                index_start += 1
    # 向后查询
    index = index_start
    while index < min(len(meta_data_list), end_index):
        if isinstance(meta_data_list[index], Table):
            index += 1
            continue
        else:
            para_text = meta_data_list[index].text
            # 如果找到含有目标文字的段落  这里存在一个问题就是上一个和下一个并没有分成两个段落
            # 也就是说这个段落里面既有有效信息也有无效信息
            # print(para_text, after_word)
            # print(para_text)
            if has_most_word(para_text, after_word, num=after_word_per):
                break
            index += 1
    # 额外判定是否有段落需要进行补充， 即判定meta_data_list[index]
    if index < len(meta_data_list):
        pat_1 = u"([\d、一二三四五六七八九十]+)?[%s]{%s,%s}" % (after_word, int(len(after_word) * after_word_per), len(after_word))
        content = meta_data_list[index].text
        result_pat_1 = re.findall(pat_1,content)
        if len(result_pat_1) > 0:
            for each in result_pat_1:
                find_index = content.find(each)
                if find_index > 5:
                    char_list1 = meta_data_list[index].chars[:find_index]
                    char_list2 = meta_data_list[index].chars[find_index:]
                    meta_data_list[index] = Paragraph(char_list2)
                    meta_data_list.insert(index, Paragraph(char_list1))
                    index += 1
                    break

    result = paragraph_merge(meta_data_list[index_start:index], delete_prun=delete_prun, prun_str=prun_str)
    # 更新meta_data_list对象
    for i in range(index):
        meta_data_list.remove(meta_data_list[0])
    # 获取新的paragraph对象
    return result




def extract_1(meta_data_list):
    """
    更换抽取思路   需方  供方  电话 传真 联系人 联系地址
    第一部分抽取整个上半部分的内容，无论是para还是table都做文字获取，去除空格下划线冒号等字符干扰
    尽可能找到目标文字段  也就是表1上面的那个部分
    :param meta_data_list:
    :return:
    """
    def extract_target(para, key_word_list, field_name_list):
        """

        :param kew_word_list:   需要抽取的字段在文中的名字   需方  供方  电话  传真
        :param field_name_list:   对应存储的位置  即抽取的字段名
        :return:
        """
        word_list = [u"需方", u"供方", u"电话", u"传真", u"联系人", u"联系地址"]
        if key_word_list[0] == key_word_list[1]:
            word_list.remove(key_word_list[0])
        else:
            word_list.remove(key_word_list[0])
            word_list.remove(key_word_list[1])
        pat_sub = u"{0}".format("|".join(word_list))
        # 替换掉无关字符
        contents = re.sub(pat_sub, "$$$$", para.text).split("$$$$")
        content = ""
        for each in contents:
            if key_word_list[0] in each and key_word_list[1] in each:
                content = each
                break
        if content == "":
            return {
                guonei[field_name_list[0]][0]: [],
                guonei[field_name_list[1]][0]: []
            }
        retult = dict()
        pat_sub2 = u"{0}".format("|".join(key_word_list))
        target_result = re.sub(pat_sub2, "$$$$", content).split("$$$$")
        value1 = target_result[1]
        index1 = para.text.find(value1)
        mapper1 = para.mapper[index1: index1 + len(value1)]
        result[guonei[field_name_list[0]][0]] = extract_split(value1, mapper1, num=1)
        value2= target_result[2]
        index2 = para.text.find(value2)
        mapper2 = para.mapper[index2: index2 + len(value2)]
        result[guonei[field_name_list[1]][0]] = extract_split(value2, mapper2, num=1)
        return result

    target_paragraph = find_target_paragraph_by_after_word(meta_data_list, u"供需双方本着平等互利", 0.7,
                                                           delete_prun=True)
    result = dict()
    try:
        result.update(extract_target(target_paragraph, [u"需方", u"供方"], ["xufang", "gongfang"]))
    except:
        result[guonei["xufang"][0]] = []
        result[guonei["gongfang"][0]] = []
        # print(u"需方供方抽取失败")
    # result.update(extract_target(target_paragraph, [u"电话", u"电话"], ["dianhua1", "dianhua2"]))
    # result.update(extract_target(target_paragraph, [u"传真", u"传真"], ["chuanzhen1", "chuanzhen2"]))
    try:
        result.update(extract_target(target_paragraph, [u"联系人", u"联系人"], ["lianxiren1", "lianxiren2"]))
    except:
        result[guonei["lianxiren1"][0]] = []
        result[guonei["lianxiren2"][0]] = []
        # print(u"联系人抽取失败")
    # 不需要对地址做额外处理了，因为只校验是不是非空了
    try:
        result.update(extract_target(target_paragraph, [u"联系地址", u"联系地址"], ["lianxidizhi1", "lianxidizhi2"]))
    except:
        result[guonei["lianxidizhi1"][0]] = []
        result[guonei["lianxidizhi2"][0]] = []
        # print(u"联系地址抽取失败")
    return result


def extract_2(meta_data_list):
    """
    抽取思路不变  省   项目名   合同编号
    :param meta_data_list:
    :return:
    """
    def find_tagget_by_pat(para, pat_list, field_list):
        result = dict()
        content = para.text.replace("省省", "省 ").replace("省_省", "省  ")
        mapper = para.mapper
        for index, each in enumerate(field_list):
            each_result = re.findall(pat_list[index], content)
            if len(each_result) > 0:
                each_value = each_result[0]
                each_index = content.find(each_value)
                each_mapper = mapper[each_index:each_index + len(each_value)]
                result[guonei[each][0]] = extract_split(each_value, each_mapper)
            else:
                result[guonei[each][0]] = []
        return result

    target_paragraph = find_target_paragraph_by_after_word(meta_data_list, u"商品名称种类规格单位数量含税价格", 0.7,
                                                           delete_prun=True, before_word=u"供需双方本着平等互利",
                                                           before_word_per=0.5, end_index=len(meta_data_list))
    pat_1 = u"货物用[于乎]([^省市]{2,9})[省市]"
    pat_2 = u"[省市]+\s*(.{3,30})项目,?"
    pat_3 = u"评审编号为([\d\-Vv]+)[,，]?以资双方"
    result = find_tagget_by_pat(target_paragraph, [pat_1, pat_2, pat_3], ["sheng", "xiangmuming", "hetongpingshenbianhao"])
    return result


def extract_3(meta_data_list):
    """
    抽取思路不变
    :param meta_data_list:
    :return:
    """
    def find_good(table_list):
        """
        根据表格找到所有的货物信息
        :param table_list: list
        :return:
        """
        # 取出所有货物信息
        good_list = []
        for each_table in table_list:  # 循环每一张表
            each_cells = each_table.cells  # 得到该表的所有单元格
            for each_line in each_cells:
                each_first_cell = each_line[0].text  # 首格
                cell_3 = each_line[3].text  # 数量
                cell_4 = each_line[4].text  # 单价
                # logger_online.info("||{0}||")
                pat_num = u"^[0-9a-zA-Z,，.]+$"
                # logger_online.info(re.findall(pat_num,each_first_cell))
                tar_num = 0
                if len(re.findall(pat_num, each_first_cell)) > 0:
                    tar_num += 1
                if len(re.findall(pat_num, cell_3)) > 0:
                    tar_num += 1
                if len(re.findall(pat_num, cell_4)) > 0:
                    tar_num += 1
                if tar_num > 1:  # 如果有一项中有数字  则是一个合格的货物
                    good_list.append(each_line)
        return good_list

    def deal_good(good_list):
        """
        处理每一条货物信息
        :param each_good:
        :return:
        """
        field_list = ["xuhao", "mingcheng", "xinghao", "shuliang", "danjia", "xiaojijine"]
        float_dict = dict()
        result = {
            guonei["xuhao"][0]: [],  # 序号
            guonei["mingcheng"][0]: [],  # 名称
            guonei["xinghao"][0]: [],  # 型号
            guonei["shuliang"][0]: [],  # 数量
            guonei["danjia"][0]: [],  # 单价
            guonei["xiaojijine"][0]: [],  # 小计金额
            guonei["zongji"][0]: []
        }
        for each_good in good_list:
            # 生成用于区分组的编号
            num = random_float()
            while num in float_dict:
                num = random_float()
            float_dict[num] = 1
            # 获取值
            for index, each_field in enumerate(field_list):
                each = each_good[index]
                if len(each.text) > 0:
                    each_result = extract_split(each.text, each.mapper)
                    for each_value in each_result:
                        each_value[1] = num
                    result[guonei[each_field][0]] += each_result
        return result

    # 防止有跨页表格
    table_list = []
    end_index = 0
    for index, each in enumerate(meta_data_list[:20]):
        if isinstance(each, Table):
            if len(each.cells) > 0 and len(each.cells[0]) > 4:
                table_list.append(each)
                end_index = index
    # 删除掉找到的部分
    for i in range(end_index + 1):
        meta_data_list.remove(meta_data_list[0])
    # 剔选出所有的货物信息
    good_list = find_good(table_list)
    # 货物信息归并
    result = deal_good(good_list)

    # 总计
    find_flag = False
    for each_table in table_list:
        each_cells = each_table.cells
        for each_line in each_cells:
            each_first_cell = each_line[0].text
            if u"总" in each_first_cell and u"计" in each_first_cell:
                for each_cell in each_line[1:]:
                    # if len(each_cell.text)>0:
                    if len(re.findall(u'[\d,\.\s]+', each_cell.text)):
                        result[guonei["zongji"][0]] = extract_split(each_cell.text, each_cell.mapper)
                        break
                find_flag = True
                break
        if find_flag:
            break

    return result


def extract_4(meta_data_list):
    """
    主要是条款类的抽取   这一部分到 交货方式截止
    产品验收  包装方式  到货签收
    抽取思路改进，通过结束标记判定
    :param meta_data_list:
    :return:
    """
    result = dict()
    result[guonei["chanpinyanshou"][0]] = []
    result[guonei["baozhuangfangshi"][0]] = []
    result[guonei["daohuoyanshou"][0]] = []

    field_list = ["chanpinyanshou", "baozhuangfangshi", "daohuoyanshou"]
    after_word_list = [u"包装方式需方须在", u"需方须在交货方式", u"交货方式需填写"]
    after_word_per_list = [0.49, 0.49, 0.7]
    for index, each_field in enumerate(field_list):
        target_paragraph = find_target_paragraph_by_after_word(meta_data_list, after_word_list[index],
                                                               after_word_per_list[index], delete_prun=False)
        result[guonei[each_field][0]] = extract_split(target_paragraph.text, target_paragraph.mapper)
    return result

def extract_5(meta_data_list):
    """
    思路不变   交货方式
    :param meta_data_list:
    :return:
    """
    result ={
        guonei["fahuoxuqiushijian"][0]: [],
        guonei["jiaohuodidiansheng"][0]: [],
        guonei["jiaohuodidianshi"][0]: [],
        guonei["jiaohuodidianqu"][0]: [],
        guonei["jiaohuodidianxiangqing"][0]: [],
        guonei["shouhuoren"][0]: [],
        guonei["shouhuolianxidianhua"][0]: [],
        guonei["yunshufangshi"][0]: []
    }
    target_paragraph_jiaohuofangshi = find_target_paragraph_by_after_word(meta_data_list,
                                                                          u"供方发货备完成", 0.5, delete_prun=False)
    # 替换掉 \d)的形式
    content = re.sub("\d\)", "  ", target_paragraph_jiaohuofangshi.text)
    content = re.sub("[\s_\(\)）（:]", " ", content)
    # print(content)
    # 开始识别
    pat_all = u"发货需求时间([\d\-年月日\s]+)交货地点(.+)省(.+)市(.+)区\s县(.+)收货人(.+)收货联系电话([\d\s或、\-]+)运输方式(.+)"
    find_result = re.findall(pat_all, content)
    if len(find_result) > 0:
        field_list = ["fahuoxuqiushijian", "jiaohuodidiansheng", "jiaohuodidianshi", "jiaohuodidianqu",
                      "jiaohuodidianxiangqing", "shouhuoren", "shouhuolianxidianhua", "yunshufangshi", ]
        for index, each_field in enumerate(field_list):
            each_value = find_result[0][index].strip()
            each_index = content.find(each_value)
            each_mapper = target_paragraph_jiaohuofangshi.mapper[each_index: each_index+len(each_value)]
            result[guonei[each_field][0]] = extract_split(each_value, each_mapper)
    else:
        # 否则独立抽取
        field_list = ["fahuoxuqiushijian", "jiaohuodidiansheng", "jiaohuodidianshi", "jiaohuodidianqu",
                      "jiaohuodidianxiangqing", "shouhuoren", "shouhuolianxidianhua", "yunshufangshi", ]
        pat_list = [u"发货需求时间([\d\-年月日\s]+)交货", u"交货地点(.+)省", u"省(.+)市", u"市(.+)区\s县",
                    u"区\s县(.+)收货人", u"收货人(.+)收货联系", u"收货联系电话([\d\s或、\-]+)运输", u"运输方式(.+)"]
        for index, each_field in enumerate(field_list):
            each_find = re.findall(pat_list[index], content)
            if len(each_find) > 0:
                each_value = each_find[0]
                each_index = content.find(each_value)
                each_mapper = target_paragraph_jiaohuofangshi.mapper[each_index: each_index + len(each_value)]
                result[guonei[each_field][0]] = extract_split(each_value, each_mapper)
    return result


def extract_6(meta_data_list):
    """
    发货时间  运输费用  质量保证  安装服务
    发票开具时间   发票类型
    # 结款日期
    # 支付方式  退货约定   违约责任  不可抗力  合同纠纷1    合同纠纷2  合同纠纷3
    # 合同修订   合同份数  特别约定
    :param meta_data_list:
    :return:
    """
    result = dict()
    result[guonei["gongfangfahuoshijian"][0]] = []
    result[guonei["yunshufeiyongchegndanfang"][0]] = []
    result[guonei["zhiliangbaozheng"][0]] = []
    result[guonei["anzhuangyufuwuzhichi"][0]] = []
    result[guonei["fapiaokaijushijian"][0]] = []
    result[guonei["fapiaoleixing"][0]] = []

    field_list = ["gongfangfahuoshijian", "yunshufeiyongchegndanfang", "zhiliangbaozheng", "anzhuangyufuwuzhichi",
                  "fapiaokaijushijian", "fapiaoleixing"]
    after_word_list = [u"运输费用承担", u"质量保证供方", u"本合同下需方", u"发票开具时间", u"发票类型",
                       u"结款日期及结算方式"]
    after_word_per_list = [0.7, 0.49, 0.7, 0.49, 0.7, 0.7]
    for index, each_field in enumerate(field_list):
        target_paragraph = find_target_paragraph_by_after_word(meta_data_list, after_word_list[index],
                                                               after_word_per_list[index], delete_prun=False)
        result[guonei[each_field][0]] = extract_split(target_paragraph.text, target_paragraph.mapper)
    return result


def extract_7(meta_data_list):
    """
     # 结款日期
    :param meta_data_list:
    :return:
    """
    result = dict()
    result[guonei["jkrqjjsfs"][0]] = []

    target_paragraph = find_target_paragraph_by_after_word(meta_data_list, "支付方式",
                                                           0.9, delete_prun=False)
    content = target_paragraph.text
    contents = content.replace(u"[", u"【").split(u"【")
    for each in contents:
        if u"V" in each or u"v" in each or u"√" in each:
            vaule = each
            if u"]" in each or u"】" in each:
                value = each.replace(u"]", u"】").split(u"】")[1]
            index = content.find(value)
            result[guonei["jkrqjjsfs"][0]] = extract_split(target_paragraph.text[index: index + len(value)],
                                                           target_paragraph.mapper[index: index + len(value)])
            break
    return result

def extract_8(meta_data_list):
    """
    # 支付方式  退货约定   违约责任  不可抗力  合同纠纷1    合同纠纷2  合同纠纷3
    # 合同修订   合同份数  特别约定
    :return: 
    """
    result = dict()
    result[guonei["zhifufangshi"][0]] = []
    result[guonei["tuihuoyueding"][0]] = []
    result[guonei["weiyuezeren"][0]] = []
    result[guonei["bukekangli"][0]] = []
    result[guonei["hetongjiufen1"][0]] = []
    result[guonei["hetongjiufen2"][0]] = []
    result[guonei["hetongjiufen3"][0]] = []
    result[guonei["hetongxiuding"][0]] = []
    result[guonei["hetongfenshu"][0]] = []
    result[guonei["tebieyueding"][0]] = []

    field_list = ["zhifufangshi", "tuihuoyueding", "weiyuezeren", "bukekangli", "hetongjiufen1",
                  "hetongjiufen2", "hetongjiufen3", "hetongxiuding", "hetongfenshu", "tebieyueding"]
    after_word_list = [u"退货约定违约责任", u"违约责任当事人一", u"当事人一方因不可抗力",
                       u"解决合同纠纷方式", u"需方明确因载明的",u"因载明的地址有误",
                       u"合同执行期间如因故",u"本合同一特别约定" , u"特别约定供方收款",
                       u"供方收款账号信息"]
    after_word_per_list = [0.49, 0.49, 0.7, 0.49, 0.49, 0.7, 0.49, 0.49, 0.49, 0.8]
    for index, each_field in enumerate(field_list):
        target_paragraph = find_target_paragraph_by_after_word(meta_data_list, after_word_list[index],
                                                               after_word_per_list[index], delete_prun=False)
        result[guonei[each_field][0]] = extract_split(target_paragraph.text, target_paragraph.mapper)

    return result


def extract_9(meta_data_list):
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

if __name__ == "__main__":
    # for i in range(12):
    #     index = i+1
    #     print("====================={0}=======================".format(index))
    #     rich_content = ""
    #     # with open("20191227/{0}.json".format("01"), "r", encoding='utf8') as f:
    #     with open("test_pdf_new_pdf2txt/{0}.json".format(index), "r", encoding='utf8') as f:
    #         rich_content = json.loads(f.read())
    #
    #     pdf2txt_decoder = Pdf2TxtDecoder(rich_content)
    #     for each in pdf2txt_decoder.get_meta_data_list():
    #         print(each)
    #     print("----------------------------")
    #     meta_data_list_after_delete = paragraph_delete(pdf2txt_decoder.get_meta_data_list())
    #     result = dict()
    #     func_list = [extract_1]#, extract_2, extract_3, extract_4, extract_5, extract_6, extract_7, extract_8]
    #     for each in func_list:
    #         each_result = each(meta_data_list_after_delete)
    #         result.update(each_result)
    #
    #     for each in result:
    #         if each in ["index", "due"]:
    #             continue
    #         # if each not in [guonei["zongji"][0]]:
    #         #     continue
    #         # for key in guonei:
    #         #     if each == guonei[key][0]:
    #         #         print(guonei[key][1], end=":")
    #         #         break
    #         # for a in result[each]:
    #         #     print(a[0], end="||")
    #         # print()
    #     print("-------------------------")
    #     # for each in meta_data_list_after_delete:
    #     #     print(each)
    #
    #     break
    pass




