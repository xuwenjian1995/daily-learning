#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/12/5 18:00
import os, sys, re, json, traceback, time

guonei = {
    "yiduanhua": ["157", u"一段话"],

    "xufang":["183", u"需方"],  #需方
    "gongfang":["184", u"供方"],  #供方
    "sheng":["212", u"省"],   #省
    "jkrqjjsfs":["168", u"12结款日期"],   #结款日期及结算方式
    "xufanggaizhang":["196", u"需方(盖章)"],   # 需方(盖章)
    "gongfanggaizhang":["197", u"供方(盖章)"],   # 供方(盖章)
    "lianxirengongfang":["199", u"供方联系人"],  # 联系人 供方
    "zongji":["195", u"总计"],   # 总计
    # "daxiejine":["55","大写金额"],   # 大写金额
    # "xiaoxiejine":["56","小写金额"],    #  小写金额

    "xuhao":["189", u"序号"],    # 序号
    "mingcheng":["190", u"产品名称"],    # 名称
    "xinghao":["191", u"产品型号"],    # 型号
    "shuliang":["192", u"数量"],    # 数量
    "danjia":["193", u"单价"],     # 单价
    "xiaojijine":["194", u"总金额"],   # 小计金额

    "chanpinyanshou":["158", u"2产品验收"],   # 产品验收
    "baozhuangfangshi":["159", u"3包装方式"],    # 包装方式
    "daohuoyanshou":["160", u"4货物验收"],    # 到货签收

    "fahuoshijian": ["161", u"5交货方式"],

    "gongfangfahuoshijian":["162", u"6发货时间"],    # 供方发货时间
    "yunshufeiyongchegndanfang":["163", u"7费用承担"],   # 运输费用承担方
    "zhiliangbaozheng":["164", u"8质量保证"],    # 质量保证
    "anzhuangyufuwuzhichi":["165", u"9安装服务"],  # 安装与服务支持
    "tuihuoyueding":["170", u"14退货约定"],     # 退货约定
    "weiyuezeren":["171", u"15违约责任"],       # 违约责任
    "bukekangli":["172", u"16不可抗力"],    # 不可抗力
    "hetongjiufen1":["173", u"17解决纠纷1"],     # 解决合同纠纷1
    "hetongjiufen2":["174", u"17解决纠纷2"],     # 解决合同纠纷2
    "hetongjiufen3":["175", u"17解决纠纷3"],     # 解决合同纠纷3
    "hetongxiuding":["176", u"18合同修订"],     # 合同修订
    "hetongfenshu":["177", u"19合同份数"],      # 合同份数
    "tebieyueding":["178", u"20特别约定"],      # 特别约定

    # "dianhua1":["75","电话1"],      # 电话1
    # "dianhua2":["76","电话2"],      # 电话2
    "lianxiren1":["185", u"联系人1"],       # 联系人1
    "lianxiren2":["186", u"联系人2"],        # 联系人2
    "lianxidizhi1":["187", u"联系地址1"],      # 联系地址1
    "lianxidizhi2":["188", u"联系地址2"],      # 联系地址2
    "xiangmuming":["213", u"项目名"],       # 项目名
    "hetongpingshenbianhao":["214", u"项目编号"],     # 合同评审编号
    "fahuoxuqiushijian":["215", u"交货方式-发货需求时间"],     # 交货方式-发货需求时间
    "jiaohuodidiansheng":["216", u"交货方式-发货地点"],    # 交货方式-发货地点省
    # "jiaohuodidianshi":["84","交货方式-发货地点市"],      # 交货方式-发货地点市
    # "jiaohuodidianqu":["85","交货方式-发货地点区"],       # 交货方式-发货地点区
    # "jiaohuodidianxiangqing":["86","交货方式-发货地点详情"],# 交货方式-发货地点详情
    "shouhuoren":["217", u"交货方式-收货人"],            # 交货方式-收货人
    "shouhuolianxidianhua":["218", u"交货方式-收货联系电话"],  # 交货方式-收货联系电话
    "yunshufangshi":["219", u"运输方式"],         # 运输方式
    "fapiaokaijushijian":["166", u"10发票开具"],    # 发票开具时间
    "fapiaoleixing":["167", u"11发票类型"],         # 发票类型
    "zhifufangshi":["169", u"13支付方式"],          # 支付方式

    "lianxiren3":["198", u"需方联系人"],            # 联系人3
    "hetongqiandingriqi1":["200", u"合同签订日期1"],   # 合同签订日期1
    "hetongqiandingriqi2":["201", u"合同签订日期2"],   # 合同签订日期2
    "zhanghumingcheng1":["202", u"需方账户名称"],     # 账户名称1
    "zhanghumingcheng2":["203", u"供方账户名称"],     # 账号名称2
    "kaihuyinhang1":["204", u"需方开户银行"],         # 开户银行1
    "kaihuyinhang2":["205", u"供方开户银行"],         # 开户银行2
    "yinhangzhanghu1":["206", u"需方银行账户"],       # 银行账户1
    "yinhangzhanghu2":["207", u"供方银行账户"],       # 银行账户2
    "shuihao1":["208", u"需方税号"],              # 税号1
    "shuihao2":["209", u"供方税号"],              # 税号2
    "dizhidianhua1":["210", u"需方地址电话"],         # 地址电话1
    "dizhidianhua2":["211", u"供方地址电话"],         # 地址电话2
    # "gongfangshoukuanzhanghaoxinxi":["100","供方收款账号信息"],  # 供方收款账号信息

    "dianhuikaihuhang":["179", u"电汇开户行账号"],      # 电汇开户行
    # "dianhuizhanghao":["23", "电汇账号"],       # 电汇账号
    "dianhuihanghao":["180", u"电汇行号"],        # 电汇行号
    "chengduikaihuhang":["181", u"承兑开户行账号"],     # 承兑开户行
    # "chengduizhanghao":["26", "承兑账号"],      # 承兑账号
    "chengduihanghao":["182", u"承兑行号"],       # 承兑行号


    # "chuanzhen1":["111","传真1"],
    # "chuanzhen2":["112","传真2"]

}


# aboard_hk01 = dict(  # todo idps中建立相应的tag字段
#     entityName=(1, "entityName"),
#     entityAddress=(2, "entityAddress"),
#     customerName=(3, "customerName"),
#     agreementNum=(4, "agreementNum"),
#     customerRegAddr=(5, "customerRegAddr"),
#     purchaserPO=(6, "purchaserPO"),
#     signDate=(7, "signDate"),
#     masterAgreement=(58, "masterAgreement"),
#     agreementRemarks=(59, "agreementRemarks"),
#     discount=(8, "discount"),
#     voucherDiscount=(9, "voucherDiscount"),
#     totalAmount=(10, "totalAmount"),
#     amountExclTax=(11, "amountExclTax"),
#     vat=(12, "vat"),
#     amountInclTax=(13, "amountInclTax"),
#     tradeMethod=(14, "tradeMethod"),
#     paymentTerms=(15, "paymentTerms"),
#     consignee=(16, "consignee"),
#     shippingAddress=(17, "shippingAddress"),
#     Tax=(18, "Tax"),
#     Warranty=(19, "Warranty"),
#     Claim=(20, "Claim"),
#     Export_Compliance=(21, "Export_Compliance"),
#     Force_Majeure=(22, "Force_Majeure"),
#     Applicable_Laws_And_Arbitration=(23, "Applicable_Laws_And_Arbitration"),
#     Special_Conditions=(24, "Special_Conditions"),
#     Counterparts=(25, "Counterparts"),
#     Export_Clearance=(26, "Export_Clearance"),
#     buyerLTD=(27, "buyerLTD"),
#     sellerLTD=(28, "sellerLTD"),
#     unitPriceKey=(29, "unitPriceKey"),
#     unitPriceDiscountExclKey=(29, "unitPriceDiscountExclKey"),
#     amountKey=(29, "amountKey"),
#     item_lineNumber=(60, "item_lineNumber"),
#     item_enuPingName=(61, "item_enuPingName"),
#     item_innerModel=(62, "item_innerModel"),
#     item_outerModel=(63, "item_outerModel"),
#     item_quantity=(64, "item_quantity"),
#     item_unitPrice=(65, "item_unitPrice"),
#     item_unitPriceDiscountExclKey=(65, "item_unitPriceExclTaxDiscount"),
#     item_amountExclTax=(68, "item_amountExclTax"),
#     item_promotionFlag=(69, "item_promotionFlag"),
# )


aboard_hk01 = dict(  # todo idps中建立相应的tag字段
    entityName=(113, "entityName"),
    entityAddress=(114, "entityAddress"),
    customerName=(115, "customerName"),
    agreementNum=(116, "agreementNum"),
    customerRegAddr=(117, "customerRegAddr"),
    purchaserPO=(118, "purchaserPO"),
    signDate=(119, "signDate"),
    masterAgreement=(120, "masterAgreement"),
    agreementRemarks=(121, "agreementRemarks"),
    discount=(122, "discount"),
    voucherDiscount=(123, "voucherDiscount"),
    totalAmount=(124, "totalAmount"),
    amountExclTax=(125, "amountExclTax"),
    vat=(154, "vat"), # todo
    amountInclTax=(13, "amountInclTax"), # todo
    tradeMethod=(126, "tradeMethod"),
    paymentTerms=(127, "paymentTerms"),
    consignee=(128, "consignee"),
    shippingAddress=(129, "shippingAddress"),
    Tax=(130, "Tax"),
    Warranty=(131, "Warranty"),
    Claim=(132, "Claim"),
    Export_Compliance=(133, "Export_Compliance"),
    Force_Majeure=(134, "Force_Majeure"),
    Applicable_Laws_And_Arbitration=(135, "Applicable_Laws_And_Arbitration"),
    Special_Conditions=(136, "Special_Conditions"),
    Counterparts=(137, "Counterparts"),
    Export_Clearance=(138, "Export_Clearance"),
    buyerLTD=(139, "buyerLTD"),
    sellerLTD=(140, "sellerLTD"),
    unitPriceKey=(141, "unitPriceKey"),
    unitPriceDiscountExclKey=(142, "unitPriceDiscountExclKey"),
    amountKey=(143, "amountKey"),
    item_lineNumber=(144, "item_lineNumber"),
    item_enuPingName=(145, "item_enuPingName"),
    item_innerModel=(146, "item_innerModel"),
    item_outerModel=(147, "item_outerModel"),
    item_quantity=(148, "item_quantity"),
    item_unitPrice=(149, "item_unitPriceExclTax"),
    item_unitPriceDiscountExclKey=(150, "item_unitPriceExclTaxDicount"),
    item_amountExclTax=(151, "item_amountExclTax"),
    item_promotionFlag=(152, "item_promotionFlag"),
)

if __name__ == "__main__":
    pass
