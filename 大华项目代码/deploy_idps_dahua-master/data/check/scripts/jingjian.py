#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/12/5 15:05
import os, sys, re, json, traceback, time
try:
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    from ..driver import logger_processor as logger
    # from ..scripts.table_extract_script.jingjian import run as extract
except:
    class a(object):
        def __init__(self):
            pass
        def info(self,message):
            print(message)
    logger = a()
    # logger.info("questiongs:{0}".format(traceback.format_exc()))


import audit_utils
from table_extract_script.jingjian import run as extract
from table_extract_script.extract_utils import get_paragraph_delete
from table_extract_script.field_conf import guonei

from pdf2txt_decoder.pdf2txt_decoder import Pdf2TxtDecoder
from document_beans.paragraph import Paragraph
from document_beans.table import Table
from document_beans.title import Title
from document_beans.cell import Cell
from uuid import uuid4 as uuid
def get_uuid():
    return str(uuid()).replace("-","")

def write_out_file(rich_content):
    # 输出成文档供测试
    folder_path = "/root/contract_check_online/check/app/scripts/files/"
    # rich_content = data["rich_content"]
    # ------------------------
    file_name = get_uuid()
    with open("{0}/{1}.json".format(folder_path, file_name), "a") as f:
        f.write(json.dumps(rich_content))
    logger.info("输出成文件:{0}".format(file_name))


def find_tagget_by_pat(content, pat_list, field_list):
    result = dict()
    content = para.text.replace("省省", "省 ")
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


def run(data):
    # 判定文档类型
    if data["tag_type_name"] not in [u"国内销售合同", u"测试国内用_jing"]:
        return None
    # 转换抽取结果
    entities = data["entities"]
    guonei_name_dict = dict()
    for each in guonei:
        guonei_name_dict[guonei[each][1]] = guonei[each][0]
    logger.info("=========guonei_name_dict=========")
    logger.info(json.dumps(guonei_name_dict, ensure_ascii=False, indent=2))
    extract_result = dict()
    for each in entities:
        each_id = guonei_name_dict.get(each.get_name(), None)
        if not each_id:
            logger.info(u"key={0}未有对应".format(each.get_name()))
            continue
        if each_id in extract_result:
            extract_result[each_id].append([each.get_value(), 1, each.get_offset()])
        else:
            extract_result[each_id] = [[each.get_value(), 1, each.get_offset()]]
    # 进行抽取  完成产品信息的抽取
    rich_content = data["rich_content"]
    pdf2txt_decoder = Pdf2TxtDecoder(rich_content)
    result = extract({"pdf2txt_decoder": pdf2txt_decoder, "result": {}})
    extract_result.update(result)
    # 获取到抽取结果之后需要做一些处理
    # 抽取出 省  项目名  项目编号    交货方式（时间，地点，人，联系方式，运输方式）
    # try:
    #     logger.info(u"進行省、項目名、項目项目编号的识别")
    #     extract_result[guonei["sheng"][0]] = []
    #     extract_result[guonei["xiangmuming"][0]] = []
    #     extract_result[guonei["hetongpingshenbianhao"][0]] = []
    #     if len(extract_result.get(guonei["yiduanhua"][0], list())) > 0:
    #         content = extract_result[guonei["yiduanhua"][0]][0][0]
    #         logger.info(u"原文:{0}".format(content))
    #         i = extract_result[guonei["yiduanhua"][0]][0][2]
    #         pat_1 = u"货物用[于乎]([^省市]{2,9})[省市]"
    #         pat_2 = u"[省市]+\s*(.+)项目,?"
    #         pat_3 = u"评审编号为([\d\-Vv\s]+)[,，]?以资双方"
    #         field_list = ["sheng", "xiangmuming", "hetongpingshenbianhao"]
    #         pat_list = [pat_1, pat_2, pat_3]
    #         for index, each in enumerate(field_list):
    #             each_result = re.findall(pat_list[index], content)
    #             if len(each_result) > 0:
    #                 each_value = each_result[0].strip()
    #                 logger.info(u"{0}：{1}".format(guonei[each][0], each_value))
    #                 each_index = content.find(each_value)
    #                 extract_result[guonei[each][0]] = [[each_value, 1, each_index + i]]
    #             else:
    #                 extract_result[guonei[each][0]] = []
    # except:
    #     logger.info("审核模块对一段话的抽取出现问题{0}".format(traceback.format_exc()))

    try:
        extract_result[guonei["jiaohuodidiansheng"][0]] = []
        extract_result[guonei["fahuoxuqiushijian"][0]] = []
        extract_result[guonei["shouhuoren"][0]] = []
        extract_result[guonei["shouhuolianxidianhua"][0]] = []
        extract_result[guonei["yunshufangshi"][0]] = []
        if len(extract_result.get(guonei["jiaohuofangshi"][0], list())) > 0:
            content = extract_result[guonei["jiaohuofangshi"][0]][0][0]
            i =extract_result[guonei["jiaohuofangshi"][0]][0][2]
            content = re.sub("\d\)", "  ", content)
            content = re.sub("[\s_\(\)）（:]", " ", content)
            # 开始识别
            pat_all = u"发货需求时间(.+)交货地点(.+)收货人(.+)收货联系电话([\d\s或、\-]+)运输方式(.+)"
            find_result = re.findall(pat_all, content)
            if len(find_result) > 0:
                field_list = ["fahuoxuqiushijian", "jiaohuodidiansheng", #"jiaohuodidianshi", "jiaohuodidianqu", "jiaohuodidianxiangqing",
                              "shouhuoren", "shouhuolianxidianhua", "yunshufangshi", ]
                for index, each_field in enumerate(field_list):
                    each_value = find_result[0][index].strip()
                    each_index = content.find(each_value)
                    # each_mapper = target_paragraph_jiaohuofangshi.mapper[each_index: each_index + len(each_value)]
                    extract_result[guonei[each_field][0]] = [[each_value, 1, each_index + i]]
            else:
                # 否则独立抽取
                field_list = ["fahuoxuqiushijian", "jiaohuodidiansheng", #"jiaohuodidianshi", "jiaohuodidianqu",
                              # "jiaohuodidianxiangqing",
                              "shouhuoren", "shouhuolianxidianhua", "yunshufangshi", ]
                pat_list = [u"发货需求时间(.+)交货", u"交货地点(.+)收货人",# u"省(.+)市", u"市(.+)区\s县",
                            #u"区\s县(.+)收货人",
                            u"收货人(.+)收货联系", u"收货联系电话([\d\s或、\-]+)运输", u"运输方式(.+)"]
                for index, each_field in enumerate(field_list):
                    each_find = re.findall(pat_list[index], content)
                    if len(each_find) > 0:
                        each_value = each_find[0]
                        each_index = content.find(each_value)
                        # each_mapper = target_paragraph_jiaohuofangshi.mapper[each_index: each_index + len(each_value)]
                        extract_result[guonei[each_field][0]] = [[each_value, 1, each_index + i]]
    except:
        logger.info("审核模块对交货情况的抽取出现问题{0}".format(traceback.format_exc()))




    '''
    ===============审核参数=============
    tag_type_name:<type 'unicode'>
    rich_content:<type 'dict'>
    text:<type 'unicode'>
    extra_conf:<type 'dict'>
    check_points:<type 'list'>
    entities:<type 'list'>
    library:<type 'list'>
    audit_items:<type 'list'>
    format_text:<type 'dict'>
    =============================
    '''
    # 至此，抽取工作已经全部完成，并且整合了规则抽取和模型抽取两部分
    # 根据check部分的抽取结果来看，rich_content的index和抽取结果中的index是同一类不需要额外进行转换
    # 也就是说我们可以在这里进行页眉页脚的抽取工作
    # 干他妈的！
    try:
        logger.info("=======================尝试进行页眉页脚的去除工作==========================")
        # logger.info("初始抽取结果:")
        # logger.info(json.dumps(extract_result, ensure_ascii=False))
        def delete_yemeiyejiao(content, prob, index, delete_mapper_dict):
            """

            :param content:  文本
            :param index:  起始位置
            :param delete_mapper_list:  需要删除的部分
            :return:
            """
            def index_merge(mapper_sort):
                """

                :param mapper_sort:
                :return:
                """
                if len(mapper_sort) ==0:
                    return []
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
                return merge_result

            index_list = [each for each in range(index, index + len(content))]
            new_index_list = []
            for each_index in index_list:
                if each_index not in delete_mapper_dict:
                    new_index_list.append(each_index)
            index_merget_result = index_merge(new_index_list)
            result = []
            for each in index_merget_result:
                start_index = each[0] - index
                end_index = start_index + each[1]
                result.append([content[start_index: end_index], prob, each[0]])
            return result


        # logger.info(extract_result)
        rich_content = data["rich_content"]
        pdf2txt_decoder = Pdf2TxtDecoder(rich_content)
        for each in pdf2txt_decoder.get_meta_data_list():
            logger.info(each)
        delete_mapper_list = get_paragraph_delete(pdf2txt_decoder.get_meta_data_list())
        # 把处理页眉页脚之间距离小于4的也纳入页眉页脚
        delete_mapper_list.sort()
        new_delete_mapper_list = [delete_mapper_list[-1]]
        for i, e in enumerate(delete_mapper_list[:len(delete_mapper_list) - 1]):
            if delete_mapper_list[i + 1] - e <= 4:
                for n in range(1, delete_mapper_list[i + 1] - e):
                    new_delete_mapper_list.append(n + e)
            new_delete_mapper_list.append(e)


        # logger.info("待删除疑似页眉页脚:")
        # logger.info(json.dumps(delete_mapper_list, ensure_ascii=False))
        delete_mapper_dict = {}
        for each in new_delete_mapper_list:
            delete_mapper_dict[each] = 1
        for each_id in extract_result:
            each_extract_result = extract_result[each_id]
            new_each_extract_result = []
            for each_result in each_extract_result:
                new_each_extract_result += delete_yemeiyejiao(each_result[0], each_result[1], each_result[2], delete_mapper_dict)
            extract_result[each_id] = new_each_extract_result
        # logger.info("去除页眉页脚后抽取结果:")
        # logger.info(json.dumps(extract_result, ensure_ascii=False))

        logger.info("================================页眉页脚去除完成==========================")
    except:
        logger.info("================================页眉页脚去除出错==========================")
        logger.info(traceback.format_exc())


    # write_out_file(rich_content)
    extra_conf = data.get('extra_conf',None)


    logger.info("extra_conf:{0}".format(json.dumps(extra_conf,ensure_ascii=False)))
    if extra_conf == None:
        # 假定传入参数
        extra_conf = {
          "zhanghumingcheng1": "11",
          "zhanghumingcheng2": "浙江大华科技有限公司",
          "chuanzhen2": "",
          "chengduizhanghao": "571907415710301",
          "chuanzhen1": "",
          "lianxidizhi1": "吉林省长春市朝阳区待确认",
          "dizhidianhua2": "杭州市滨江区长河街道滨安路1199号F座1层0571- 28058299",
          "jiaohuodidianxiangqing": "11",
          "lianxidizhi2": "杭州市滨江区长河街道滨安路1199号F座1层",
          "fapiaokaijushijian": 4,
          "shouhuoren": "1",
          "dianhuikaihuhang": "建行杭州高新支行",
          "hetongqiandingriqi1": "2019-12-11",
          "hetongqiandingriqi2": "2019-12-11",
          "daxiejine": "",
          "kaihuyinhang1": "11",
          "lianxirengongfang": "龙梅 .",
          "xiangmuming": "中国银行股份有限公司吉林省分行",
          "shuihao2": "91330000062045693L",
          "shuihao1": "11",
          "dianhuihanghao": "105331008004",
          "fahuoxuqiushijian": "",
          "chengduikaihuhang": "招行杭州滨江支行",
          "lianxiren3": "孙洪亮",
          "lianxiren1": "孙洪亮",
          "gongfang": "浙江大华科技有限公司",
          "jkrqjjsfs": "",
          "sheng": "北京市",
          "tiaokuan": {
            "jiejuejiufen1": "解决合同纠纷的方式：执行本合同发生争议，由当事人双方协商解决。协商不成，双方同意向供方所在地人民法院提起诉讼。",
            "jiejuejiufen3": "因载明的地址有误或未及时告知变更后的地址或指定收件人拒收，导致诉讼文书未能实际被接收的，邮寄送达的诉讼文书退回之日即视为送达之日。",
            "name": "国内标准合同模板",
            "gongfangfahuo": "供方发货时间：供方备货完成后3日内发货。",
            "tebieyueding": "20、特别约定需方理解，遵守适用的法律法规，包括美国出口管制法律的规定，是供方基本的公司政策。需方承诺，针对从供方及其关联人处购买的货物，需方将遵守相关的进口、出口、再出口的法律法规，具体要求包括但不限于： 1）需方承诺，这些货物不会被用于被任何适用法律禁止的最终用途，包括化学武器、生物武器、核武器、导弹以及其他军用项目的设计、开发、生产、存储或使用； 2）需方理解，如果货物含有源自美国的物品（U.S. Origin Items）,该等货物（“管制货物”）可能受到美国出口管制条例（Export Administration Regulation，或EAR）的管辖。需方承诺，在管制货物的出口和再出口时，遵守相关的法律要求，包括，按照EAR或其他适用法律的要求，例如向美国政府申请获得出口许可； 3）需方承诺，不会把管制货物转售给被美国或欧盟制裁的国家、实体或个人，包括但不限于美国财政部外国资产控制办公室管理的“特别指定国民及受封锁人士”清单（Specially Designated Nationals and Blocked Persons List）和美国商务部工业和安全局管理的“拒绝交易对象”（Denied Persons List）与“实体清单”（ Entity List）以及受到欧盟金融制裁的欧盟人士、集团和实体综合清单上的个人或实体； 4）需方承诺，对管制货物的使用和处理不会违反适用的法律法规。",
            "daohuoqianshou": "需方须在货物到达时按厂商出厂装箱标准进行验收并签收。需方无合理原因即拒绝签收的，视为违约，供方有权自行处理该批货物，并就所受损失包括但不限于返程物流费用、仓储费用等向需方索赔。",
            "weiyuezeren": "15、违约责任：1)任何一方不履行本合同义务或履行本合同义务不符合约定的，均属于违约行为。违约方应向守约方支付合同总金额20%作为违约金，并应对守约方因此造成的损失承担赔偿责任。本合同另有规定的除外。2)由于供方原因，未能按合同约定向需方交货，供方应向需方支付迟延履行违约金。每迟延1日，供方应向需方支付相当于迟延交付货物货款的1‰作为迟延履行违约金，但迟延履行违约金总额不超过合同总金额的20%。3)由于需方原因，未能按合同约定付款，需方应向供方支付违约金。每迟延1日，需方应向供方支付相当于迟延支付货款总额的1‰作为迟延履行违约金，但迟延履行违约金总额不超过合同总金额的20%。同时，交货期相应顺延。需方迟延付款超过30个自然日，供方有权解除合同。4)货款必须汇到供方书面指定的银行帐号，否则，视为需方未按合同约定履行付款义务，供方有权要求需方继续履行付款义务，并追究需方逾期付款的违约责任。本合同约定交货方式、收货地点有误或变更，须需方提供盖章书面文件通知供方，由此产生的费用由需方承担。因需方通知有误或通知不及时，致使本合同交货出现的问题，供方不承担任何责任；",
            "tuihuoyueding": "退货约定：非质量原因供方原则上不接受退货，供方同意退货的，需方按照供方要求支付退货费用后，双方签订退货协议；否则，需方不得以退货为由，拒绝履行付款义务。对于已开发票的退货，需方必须退回发票或提供红字开票通知单。",
            "chanpinyanshou": "供方保证交付的货物为全新品，产品的功能验收以产品随机配备的说明书功能描述为准。需方收货后七天内未书面提出异议，视为合格产品。",
            "yunshufeiyong": "运输费用承担方:供方指定的运输方式由供方承担，如需方指定物流运输方式，应在供方发货之日前提出，且运输费用由需方承担；",
            "zhiliangbaozheng": "质量保证：供方在提供的产品发生质量问题依法提供退换、保修，各产品免费质保年限详见供方官方网站“服务与下载-服务政策”http://www.dahuatech.com,双方另有约定除外(须在备注处注明)。",
            "anzhuangfuwu": "本合同下甲方负责安装的，甲方（包括甲方委托或指定的第三方）应严格按照以下要求安装：1）产品随机配备的说明书（若乙方培训另有要求的，以乙方培训内容为准）； 2）工程项目施工质量手册，请参见乙方官方网：“http://www.dahuatech.com/ ”服务支持；3）如仍存在安装疑义的，请联系乙方代表。如甲方未按照上述要求，擅自更改安装方案，造成质量、安全事故的，全部损失由甲方自行承担。",
            "hetongfenshu": "本合同一式肆份，自双方盖章之日起生效，双方各执贰份，具有同等法律效力。",
            "bukekangli": "当事人一方因不可抗力而不能履行合同时，应当及时通知对方，并在合理期限内提供有关机构出具的证明，可以全部或部分免除该方当事人的责任。",
            "baozhuangfangshi": "包装方式：原厂纸箱包装。",
            "hetongxiuding": "合同执行期间，如因故不能履行或需要修改，必须经双方同意，并签订补充协议或另订合同，方为有效。"
          },
          "xufang": "中国银行股份有限公司吉林省分行",
          "zhifufangshi": "",
          "lianxiren2": "龙梅 .",
          "yinhangzhanghu1": "11",
          "shouhuolianxidianhua": "1",
          "dizhidianhua1": "1111",
          "dianhuizhanghao": "33001616727059988881",
          "yunshufangshi": "供方自行选择合适的货物运输方式。",
          "xufanggaizhang": "中国银行股份有限公司吉林省分行",
          "yinhangzhanghu2": "33001616727059988881",
          "goods": [
            {
              "xinghao": "ST4000VM000",
              "mingcheng": "机械硬盘",
              "danjia": "322",
              "xiaojijine": "3220",
              "shuliang": "10",
              "xuhao": "0"
            }
          ],
          "dianhua2": "111",
          "jiaohuodidianshi": "11",
          "dianhua1": "13900000000",
          "hetongpingshenbianhao": "1-2631194151",
          "jiaohuodidianqu": "11",
          "chengduihanghao": "308331012280",
          "fapiaoleixing": "",
          "zongji": 3220,
          "gongfanggaizhang": "浙江大华科技有限公司",
          "jiaohuodidiansheng": "11",
          "gongfangshoukuanzhanghaoxinxi": "",
          "xiaoxiejine": "",
          "kaihuyinhang2": "建行杭州高新支行"
        }


    tiaokuan = extra_conf.get("tiaokuan",{})



    # 进行抽取
    # pdf2txt_decoder = Pdf2TxtDecoder(rich_content)
    # result = extract({"pdf2txt_decoder": pdf2txt_decoder, "result": {}})
    result = extract_result
    #logger.info(json.dumps(result,ensure_ascii=False,indent=2))
    # ----------------------------
    # id-name匹配
    # name_dict = {}
    # for each in guonei:
    #     name_dict[each[1]] = each[0]
    # 抽取结果进行审核
    audit_items = []
    # 需方和供方
    try:
        audit_result = audit_utils.audit_1(result,extra_conf[u"xufang"],extra_conf[u"gongfang"])
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("需方和供方",traceback.format_exc()))
    # 两个电话
    # try:
    #     audit_result = audit_utils.audit_2(result,extra_conf[u"dianhua1"],extra_conf[u"dianhua2"])
    #     audit_items += audit_result
    # except:
    #     logger.info("{0}审核失败:{1}".format("两个电话",traceback.format_exc()))
    # 两个传真
    # try:
    #     audit_result = audit_utils.audit_3(result)
    #     audit_items += audit_result
    # except:
    #     logger.info("{0}审核失败:{1}".format("两个传真",traceback.format_exc()))
    # 两个联系人
    try:
        audit_result = audit_utils.audit_4(result,extra_conf[u"lianxiren1"],extra_conf[u"lianxiren2"])
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("两个联系人",traceback.format_exc()))
    # 两个联系地址
    try:
        audit_result = audit_utils.audit_5(result,extra_conf[u"lianxidizhi1"],extra_conf[u"lianxidizhi2"])
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("两个联系地址",traceback.format_exc()))
    # 一段话
    try:
        audit_result = audit_utils.audit_6(result,extra_conf[u"sheng"],extra_conf[u"xiangmuming"],extra_conf[u"hetongpingshenbianhao"])
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("一段话",traceback.format_exc()))
    # 表格
    try:
        audit_result = audit_utils.audit_7(result,extra_conf["goods"],str(extra_conf["zongji"]))
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("表格1",traceback.format_exc()))
    # 产品验收条款
    try:
        content_8 = u"供方保证交付的货物为全新品，产品的功能验收以产品随机配备的说明书功能描述为准。需方收货后七天内未书面提出异议，视为合格产品。"
        audit_result = audit_utils.audit_8(result, tiaokuan)
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("产品验收条款",traceback.format_exc()))
    # 包装方式条款
    try:
        content_9 = u"包装方式：原厂纸箱包装。"
        audit_result = audit_utils.audit_9(result, tiaokuan)
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("包装方式条款",traceback.format_exc()))
    # 到货签收条款
    try:
        content_10 = u"需方须在货物到达时按厂商出厂装箱标准进行验收并签收。需方无合理原因即拒绝签收的，视为违约，供方有权自行处理该批货物，并就所受损失包括但不限于返程物流费用、仓储费用等向需方索赔。"
        audit_result = audit_utils.audit_10(result, tiaokuan)
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("到货签收条款",traceback.format_exc()))
    # =================================
    # 交货方式条款  11
    try:
        audit_result = audit_utils.audit_11(result, extra_conf)
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("交货方式条款",traceback.format_exc()))
    # 供方发货时间条款
    try:
        audit_result = audit_utils.audit_12(result, tiaokuan)
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("供方发货时间条款",traceback.format_exc()))
    # 运输费用承担方条款
    try:
        audit_result = audit_utils.audit_13(result, tiaokuan)
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("运输费用承担方条款",traceback.format_exc()))
    # 质量保证条款
    try:
        audit_result = audit_utils.audit_14(result, tiaokuan)
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("质量保证条款",traceback.format_exc()))
    # 安装与服务支持条款
    try:
        audit_result = audit_utils.audit_15(result, tiaokuan)
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("安装与服务支持条款",traceback.format_exc()))
    # 发票开具时间
    try:
        audit_result = audit_utils.audit_16(result)
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("发票开具时间",traceback.format_exc()))
    # 发票类型
    try:
        audit_result = audit_utils.audit_17(result)
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("发票类型",traceback.format_exc()))
    # 结款日期与结算方式
    try:
        audit_result = audit_utils.audit_18(result,extra_conf)
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("结款日期与结算方式",traceback.format_exc()))
    # 支付方式
    try:
        audit_result = audit_utils.audit_19(result)
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("支付方式",traceback.format_exc()))
    # 退货约定
    try:
        audit_result = audit_utils.audit_20(result, tiaokuan)
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("退货约定",traceback.format_exc()))
    # 违约责任
    try:
        audit_result = audit_utils.audit_21(result, tiaokuan)
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("违约责任",traceback.format_exc()))
    # 不可抗力
    try:
        audit_result = audit_utils.audit_22(result, tiaokuan)
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("不可抗力",traceback.format_exc()))
    # 解决合同纠纷
    try:
        audit_result = audit_utils.audit_23(result,tiaokuan)
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("解决合同纠纷",traceback.format_exc()))
    # 合同修订
    try:
        audit_result = audit_utils.audit_24(result,tiaokuan)
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("合同修订",traceback.format_exc()))
    # 合同份数
    try:
        audit_result = audit_utils.audit_25(result,tiaokuan)
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("合同份数",traceback.format_exc()))
    # 特别约定
    try:
        audit_result = audit_utils.audit_26(result,tiaokuan)
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("特别约定",traceback.format_exc()))
    # 表格2
    try:
        audit_result = audit_utils.audit_27(result,extra_conf)
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("表格2",traceback.format_exc()))
    # 供方收款账号信息
    try:
        audit_result = audit_utils.audit_28(result,extra_conf)
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("供方收款账号信息",traceback.format_exc()))
    # 金额大小写
    try:
        audit_result = audit_utils.audit_29(data["text"])
        audit_items += audit_result
    except:
        logger.info("{0}审核失败:{1}".format("金额大小写", traceback.format_exc()))

    audit_items.sort(key=lambda each: len(each["audit_rule"]) * (-1))




    data.update({"audit_items": audit_items})








    # entities = data["entities"]
    # for each in entities:
    #     logger.info(type(each)g)











if __name__ == "__main__":
    data = ""
    with open("files/c84931eb6f944a088ac0a4c1c5af1e1a.json","r",encoding="utf8") as f:
        data=json.loads(f.read())
    # print(data)




    rich_content = data#["rich_content"]
    # pd = Pdf2TxtDecoder(rich_content)
    # meta_data_list = pd.get_meta_data_list()
    # for each in meta_data_list:
    #     print(each)
    a = {"rich_content":rich_content,"tag_type_name":u"国内销售合同"}
    run(a)
    audit_items = a["audit_items"]
    # print(a["audit_items"])
    print(json.dumps(audit_items,ensure_ascii=False))

    # for each in audit_items:
    #     print(each["audit_rule"])
