money_dict = {
    u"壹":1,
    u"贰":2,
    u"叁":3,
    u"肆":4,
    u"伍":5,
    u"陆":6,
    u"柒":7,
    u"捌":8,
    u"玖":9,
    u"零":0
}

def transform(money):
    # print(money)
    if u"亿" in money:
        moneys = money.split(u"亿")
        if len(moneys)==2:
            return transform(moneys[0])*100000000+transform(moneys[1])
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
        if len(money)==1:
            return money_dict[money]
        elif len(money)==0:
            return 0
        else:
            return money_dict[money[len(money)-1]]






    text_2 = text
    pat_2_1 = "[壹贰叁肆伍陆柒捌玖拾佰仟万亿零元角分]{2,}"
    result_2_1 = re.finditer(pat_2_1, text_2)
    return_2 = []
    # 找到所有的大写 默认为金额
    for each in result_2_1:
        each_value = each.group()
        if each_value[0] not in "壹贰叁肆伍陆柒捌玖拾":
            continue
        logger.info(each_value)
        # 转小写数字
        # print(type(each_value))
        if type(each_value) == str:
            num = transform(each_value.decode("utf-8"))
        else:
            num = transform(each_value)
        start_index = each.span()[0]
        end_index = each.span()[1]
        target_str = text_2[max(start_index-25,0):min(len(text_2),end_index+25)]
        pat_2_2 = "((\d{1,3}(,\d{3})+(\.\d{1,2})?)|(\d{2,}(\.\d{1,2})?))"
        result_2_2 = re.finditer(pat_2_2, target_str)
        result_2_2_list = []
        find_flag = False
        for each2 in result_2_2:
            each2_value = float(each2.group().replace(",",""))
            result_2_2_list.append([each2.group(), each2.span()[0]])
            if int(num*100) == int(each2_value*100):
                find_flag = True
        if len(result_2_2_list)>0 and find_flag==False:
            result_2_2_list.sort(key=lambda e: len(e[0])*(-1))
            return_2.append([{"text": each_value, "offset": start_index}, {"text": str(result_2_2_list[0][0]), "offset": result_2_2_list[0][1]+max(start_index-25,0)}])
    for each in return_2:
        audit_item = {
            "audit_suggestion": '请核实',
            "audit_desc": '大小写不一致',
            "audit_tips": "大小写不一致",
            "audit_rule_type": "必改问题",
            "context": each
        }
        audit_items.append(audit_item)
    data.update({"audit_items": audit_items})
