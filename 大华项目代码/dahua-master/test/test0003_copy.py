#!/usr/bin/env python
# coding=utf-8
# author: jingjian@datagrand.com
# datetime:2019-11-28 17:29
import os, sys, re, json, traceback, time
import _locale
import requests
_locale._getdefaultlocale = (lambda *args: ['en_US', 'utf8'])
host = 'http://10.1.253.53:15000/api/'
user_info = dict(token='', username='admin123', password='abcd@123!')
def login():
    """登录
    """
    login_response = requests.post(
    host + 'login',
    data={
        'username': user_info['username'],
        'password': user_info['password']
    })
    if login_response.status_code >= 400:
        print(json.loads(login_response.content))
        print(login_response)
        print('登录失败，请联系达观项⽬负责⼈')
        exit()
    user_info['token'] = login_response.json().get('access_token')
def headers_generator():
    """⽣成身份认证 headers
    """
    return {'Authorization': 'Bearer ' + user_info['token']}
def request_with_jwt(url, method, **kw):
    """使⽤jwt认证登录简单封装requests
    Arguments:
    url {[str]} -- [请求地址]
    method {[str]} -- [请求⽅法]
    Returns:
    [response] -- [requests的响应]
    """
    # 检测是否有token, 没有则登录获取
    if not user_info['token']:
        login()
        print(user_info["token"])
    if method == 'GET':
        response = requests.get(url, headers=headers_generator(), **kw)
    else:
        response = {
            'PUT': requests.put,
            'POST': requests.post,
            'DELETE': requests.delete,
        }[method](
            url, headers=headers_generator(), **kw)
    # 检测token是否合法，不合法则登录获取token，再发送相同请求
    print(response)
    if response.status_code == 401:
        login()

        return request_with_jwt(url=url, method=method, **kw)
    else:
        return response

# 进行电子稿审核
def send_request_check(file_path,doc_form=1):
    '''
    doc_form  1电子件    2扫描件    3图片
    :param file_path:
    :return:
    '''
    fileList = {'fileList': open(file_path, 'rb')}
    response = request_with_jwt(
        url=host + 'review',
        data = {"data": json.dumps({"check_point_id_list": [2], "tag_type_id": "30","doc_form":doc_form}), "async_task": False},
        files =fileList,
        method='POST')
    '''
    {
      "abstract_info": {
        "8160": [
          [
            "平安国际融资租一有限公司",
            0.99901234,
            212
          ]
        ]
      },
      "id": 140,
      "message": "提交成功",
      "text": "平安国际融资租赁有限公司2017年公开发行可续期公司债券募集说明书（面向合格投资者)第一节发行概况一、本次债券的核准情况及核准规模1、2017年7月11日，发行人董事会批准公司本次公开发行可续期公司债券，同意公司发行不超过45亿元人民币的可续期公司债券。2、本次债券于2017年【】月【】日经中国证监会“证监许可〔2017〕【】号”文核准公开发行，核准规模为不超过45亿元。二、本次债券发行的基本情况及发行条款1、发行主体：平安国际融资租一有限公司。2、债券名称：平安国际融资租赁一有限公司2017年公开发行可续期公司债券。3、债券期限及发行人续期选择权：本次债券以每3/5个计息年度为一个周期（“重新定价周期”）。在每3/5个计息年度（即每个重新定价周期）末附发行人续期选择权，发行人有权选择将本次债券期限延长3/5年（即1个重新定价周期），或选择在该重新定价周期到期全额兑付本次债券。若发行人选择延长债券期限，发行人应至少于续期选择权行权年度付息日前30个交易日，在相关媒体上刊登续期选择权行使公告。选择延长债券期限后，从第2个重新定价周期开始，每个重新定价周期适用的票面利率调整为当期基准利率加上基本利差再加上300个基点（1个基点为0.01%），由发行人确定，并于续期选择权行权年度付息日后【】个交易日内，在相关媒体上刊登票面利率调升公告。4、发行规模：本次债券发行总规模不超过人民币45亿元，分期发行，首期发行规模不超过人民币45亿元。具体发行规模由公司董事长根据公司资金需求情况和发行时市场情况在上述范围内确定。5、债券利率及其确定方式：本次债券采用固定利率形式，单利按年计息。在本次债券存续的首个重新定价周期（第1个计息年度至第3/5个计息年度）内，票面年利率由基准利率加上基本利差确定。基准利率在每个重新定价周期确定一次。首次基准利率为簿记建档日前5个交易日中国债券信息网（www.chinabond.com.cn）（或中央国债登记结算有限责任公司认可的其他网站）公布的中债银行12平安国际融资租赁有限公司2017年公开发行可续期公司债券募集说明书（面向合格投资者)间固定利率国债收益率曲线中，待偿期为3/5年的国债收益率的算术平均数（四舍五入保留两位小数），其后每个重新定价周期的当期基准利率为在该重新定价周期起息日前5个交易日中国债券信息网（www.chinabond.com.cn）（或中央国债登记结算有限责任公司认可的其他网站）公布的中债银行间固定利率国债收益率曲线中，待偿期为3/5年的国债收益率的算术平均数（四舍五入保留两位小数）。如果发行人选择延长本次债券期限，则从第2个重新定价周期开始，每个重新定价周期适用的票面利率调整为当期基准利率加上基本利差再加上300个基点（1个基点为0.01%）。6、递延支付利息权：本次债券附设发行人延期支付利息权，除非发生强制付息事件，本次债券的每个付息日，发行人可自行选择将当期利息以及按照本条款已经递延的所有利息及其孳息推迟至下一个付息日支付，且不受到任何递延支付利息次数的限制；前述利息递延不属于发行人未能按照约定足额支付利息的行为。每笔递延利息在递延期间应按当期票面利率累计计息。如发行人决定递延支付利息的，发行人应在付息日前5个交易日披露《递延支付利息公告》。7、强制付息事件：付息日前12个月内，发生以下事件的，发行人不得递延当期利息以及按照约定已经递延的所有利息及其孳息：（1）向普通股股东分红；（2）减少注册资本。8、利息递延下的限制事项：若发行人选择行使延期支付利息权，则在延期支付利息及其孳息未偿付完毕之前，发行人不得有下列行为：（1）向普通股股东分红；（2）减少注册资本。9、发行人赎回选择权（1）发行人因税务政策变更进行赎回发行人由于法律法规的改变或修正，相关法律法规司法解释的改变或修正而不得不为本次债券的存续支付额外税费，且发行人在采取合理的审计方式后仍然不能避免该税款缴纳或补缴责任的时候，发行人有权对本次债券进行赎回。发行人若因上述原因进行赎回，则在发布赎回公告时需要同时提供以下文件：序号姓名性别年龄1张一女182张二女183张三女184张四女185张五女186张柳女187张琪女188张吧女189张就女1810张氏女18①由发行人总经理及财务负责人签字的说明，该说明需阐明上述发行人不可避免的税款缴纳或补缴条例；13平安国际融资租赁有限公司2017年公开发行可续期公司债券募集说明书（面向合格投资者)的资产中剩余权益的合同，通过发行条款的设计，发行的可续期公司债券将作为权益工具进行会计核算。若后续会计政策、标准发生变化，可能使得已发行的可续期公司债券重分类为金融负债，从而导致发行人资产负债率上升的风险。（六）信用评级变化的风险本次债券评级机构中诚信证评评定发行人的主体长期信用等级为AAA，评定本次债券的信用等级为AAA。虽然发行人目前资信状况良好，但在本次债券存续期内，发行人无法保证主体信用评级和本次债券的信用评级不会发生负面变化。若资信评级机构调低发行人的主体信用评级或本次债券的信用评级，则可能对债券持有人的利益造成不利影响。二、发行人的相关风险（一）财务风险1、负债水平较高的风险发行人近年来由于业务经营的不断扩张，资产规模和负债规模也随之上升。2014-2016年及2017年3月末，发行人资产负债率分别为84.52%、86.39%、88.24%和87.25%，其中，非流动负债占总负债比重分别为67.37%、57.70%、56.87%和64.06%。由于行业性质，近年来发行人资产负债比率维持在相对高位，公司目前处于业务扩张期，资金需求量较大，有息债务规模总体增长较快，非流动负债比例相对较高，发行人未来可能面临一定的偿债压力。大写金额:壹亿贰仟叁佰肆拾伍万陆仟柒佰捌拾玖；小写金额:123，456，789.00元2、长期应收款无法按期收回的风险发行人应收融资租赁款规模较大，2014-2016年及2017年3月末，发行人长期应收款分别为1,033,553.31万元、4,290,498.10万元、6,434,066.65万元和5,657,320.39万元；一年内到期的非流动资产分别为1,301,810.56万元、2,256,008.46万元、3,466,093.28万元和3,798,166.58万元；两者合计占总资产比重分别为86.54%、86.46%、86.97%和75.98%。发行人的长期应收款多为超一年期的应收融资租赁款，归因于发行人的租赁业务期限一般为3-8年期，一年内到期的非流动资产主要为一年内应收回的融资租赁款。受宏观经济形势、行业政策以及技术更新的影响，如融资租赁承租人不能按期支付租赁款，发行人存在应收款无法按期收回的可能性。24平安国际融资租赁有限公司2017年公开发行可续期公司债券募集说明书（面向合格投资者)3、期间费用上升的风险发行人期间费用主要为业务及管理费，2014-2016年及2017年3月末分别为57,843.15万元、81,396.00万元、116,207.82万元和29,835.35万元，占营业收入的比例分别为22.04%、17.61%、18.56%和15.22%。发行人近年来期间费用金额呈现稳步上升的态势，主要是由于发行人开拓业务和人员扩张导致业务及管理费用出现增长所致。然而，由于发行人业务发展较快，成本得到进一步控制，期间费用占收入的比例有所下降。随着公司业务规模的扩大，未来期间费用可能会随营业收入的增加而增长，对发行人的盈利水平产生一定影响。4、流动性风险流动性风险指的是企业由于资金筹措不力、现金流动不畅或发生停滞、断流等不能偿还到期债务形成的风险。2014-2016年及2017年3月末，发行人流动比率分别为1.33、1.03、0.99及1.30，速动比率分别为1.33、1.03、0.99及1.30，略呈下降的趋势，短期偿债能力有所减弱。2014-2016年及2017年3月末，发行人经营活动产生的现金流净额分别为-243,691.93万元、-319,783.12万元、-610,063.63万元和-570,679.69万元，发行人经营活动现金流量净额持续为负，主要是因为发行人处于资产快速增长阶段，购买租赁资产用于租赁业务的资金投入大于由租赁业务形成的租金回笼速度。融资租赁行业作为资金密集型行业，需要投入大量资金进行经营，随着发行人近年来融资租赁业务规模逐年的增长，发行人经营性活动现金流可能继续保持流出且流出幅度逐年增大，进而导致发行人出现一定的流动性风险。5、受限资产较大的风险发行人为保证融资租赁业务的正常进行，在董事会授权下以其应收租赁款和租赁资产等作为质押品和抵押品向银行提供增信措施，相应的应收租赁款和资产成为受限资产。截至2017年3月末，公司受限资产账面价值总额为3,770,340.62万元，占总资产比例为30.30%，未来随着公司规模的逐步扩大，公司为保证顺利融资，受限资产将逐渐增加，若未来公司的经营情况发生变化，无法偿还到期负债，相关的受限资产将面临所有权被转移的风险，可能对公司的生产经营造成较大影响。在抵、质押融资期间，相关的受限资产的处置也将受到限制。6、有息负债规模扩张较快的风险25"
    }
    '''
    # url = "http://idps2-preview.test.datagrand.cn/api/review"
    #
    # data = {"data": json.dumps({"check_point_id_list": [21], "tag_type_id": "2278"}), "async_task": False}
    #
    # send_review_request = requests.post(url, data=data, files=fileList,
    #                                     headers={
    #                                         'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2NsYWltcyI6eyJ1c2VybmFtZSI6InN1cGVyYWRtaW5wcm8iLCJzdGF0dXMiOjEsInJvbGVfaWRzIjpbMV0sInVzZXJfaWQiOi0xLCJyb2xlX25hbWVfbGlzdCI6WyJcdTdiYTFcdTc0MDZcdTU0NTgiLCJzdXBlcmFkbWlucHJvIl0sIm5pY2tuYW1lIjoiSSBjYW4gYW55dGhpbmchIn0sImp0aSI6IjNkMzhlYTE0LTYyODItNGQ1YS05YTFmLTgwZTJiMjQwMDkxYSIsImV4cCI6MTU3NDk5NTA3MSwiZnJlc2giOmZhbHNlLCJpYXQiOjE1NzQ5MDg2NzEsInR5cGUiOiJhY2Nlc3MiLCJuYmYiOjE1NzQ5MDg2NzEsImlkZW50aXR5Ijoic3VwZXJhZG1pbnBybyJ9.ro1ybK9sAlB101obuQ_3Ks9k2e6FAR2Y0DtTC325OE8',
    #                                         })
    print(json.dumps(json.loads(response.content),ensure_ascii=False,indent=2))

# 获取电子件审核结果
def send_request_check_info(doc_id):
    '''
    结果页面形如   http://idps2-preview.test.datagrand.cn/#/review/reviewDetail/147?doc_form=3
    :param doc_id:
    :return:
    '''
    # fileList = {'fileList': open(file_path, 'rb')}
    response = request_with_jwt(
        url=host + 'review/{0}'.format(doc_id),
        method='GET')
    # url = "http://idps2-preview.test.datagrand.cn/api/review/120"
    # send_review_request = requests.get(url,
    #                                    headers={
    #                                        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2NsYWltcyI6eyJ1c2VybmFtZSI6InN1cGVyYWRtaW5wcm8iLCJzdGF0dXMiOjEsInJvbGVfaWRzIjpbMV0sInVzZXJfaWQiOi0xLCJyb2xlX25hbWVfbGlzdCI6WyJcdTdiYTFcdTc0MDZcdTU0NTgiLCJzdXBlcmFkbWlucHJvIl0sIm5pY2tuYW1lIjoiSSBjYW4gYW55dGhpbmchIn0sImp0aSI6IjNkMzhlYTE0LTYyODItNGQ1YS05YTFmLTgwZTJiMjQwMDkxYSIsImV4cCI6MTU3NDk5NTA3MSwiZnJlc2giOmZhbHNlLCJpYXQiOjE1NzQ5MDg2NzEsInR5cGUiOiJhY2Nlc3MiLCJuYmYiOjE1NzQ5MDg2NzEsImlkZW50aXR5Ijoic3VwZXJhZG1pbnBybyJ9.ro1ybK9sAlB101obuQ_3Ks9k2e6FAR2Y0DtTC325OE8',
    #                                        })
    a= json.loads(response.content)
    b = a["items"]
    print(json.dumps(a,ensure_ascii=False,indent=2))
    # print(json.dumps(json.loads(response.content),ensure_ascii=False,indent=2))

# 进行扫描件表格抽取
def send_request_table_extract(file_path):
    # url = "http://idps2-preview.test.datagrand.cn/api/extracting/new/table"
    # fileList = {
    #     'file': open(file_path,
    #                  'rb')}
    # data = {"ocr": 0, "async_task": False,"feature_type_id": 133}
    # response = requests.post(url, data=data, files=fileList,
    #                                     headers={
    #                                         'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2NsYWltcyI6eyJ1c2VybmFtZSI6ImFkbWluIiwic3RhdHVzIjoxLCJyb2xlX2lkcyI6WzFdLCJ1c2VyX2lkIjoxLCJyb2xlX25hbWVfbGlzdCI6WyJcdTdiYTFcdTc0MDZcdTU0NTgiXSwibmlja25hbWUiOiJcdTdiYTFcdTc0MDZcdTU0NTgifSwianRpIjoiYzJjMmE0NWEtMTI2OC00MDcxLTlkMGMtMGRiOTQyYzliN2NlIiwiZXhwIjoxNTc1MzM2MTkzLCJmcmVzaCI6ZmFsc2UsImlhdCI6MTU3NTI0OTc5MywidHlwZSI6ImFjY2VzcyIsIm5iZiI6MTU3NTI0OTc5MywiaWRlbnRpdHkiOiJhZG1pbiJ9.HWJuyEPTw5F2400Pjm1Pz_RHp6Dwf8OqvWn3mH9fucI',
    #                                         })

    fileList = {'file': open(file_path, 'rb')}
    response = request_with_jwt(
        url=host + 'extracting/new/table',
        data={"ocr": 0, "async_task": False,"feature_type_id": 133},
        files=fileList,
        method='POST')


    # fileList = {
    #     'file': open('/Users/wangtingting/extract_admin_backend/api/upload/0d74b10f-020d-11ea-bac2-d20091b04101.pdf',
    #                  'rb')}
    # data = {"ocr": 0, "async_task": False}
    # send_review_request = requests.post(url, data=data, files=fileList,
    #                                     headers={
    #                                         'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2NsYWltcyI6eyJ1c2VybmFtZSI6InN1cGVyYWRtaW5wcm8iLCJzdGF0dXMiOjEsInJvbGVfaWRzIjpbMV0sInVzZXJfaWQiOi0xLCJyb2xlX25hbWVfbGlzdCI6WyJcdTdiYTFcdTc0MDZcdTU0NTgiLCJzdXBlcmFkbWlucHJvIl0sIm5pY2tuYW1lIjoiSSBjYW4gYW55dGhpbmchIn0sImp0aSI6IjNkMzhlYTE0LTYyODItNGQ1YS05YTFmLTgwZTJiMjQwMDkxYSIsImV4cCI6MTU3NDk5NTA3MSwiZnJlc2giOmZhbHNlLCJpYXQiOjE1NzQ5MDg2NzEsInR5cGUiOiJhY2Nlc3MiLCJuYmYiOjE1NzQ5MDg2NzEsImlkZW50aXR5Ijoic3VwZXJhZG1pbnBybyJ9.ro1ybK9sAlB101obuQ_3Ks9k2e6FAR2Y0DtTC325OE8',
    #                                         })
    print(json.dumps(json.loads(response.content),ensure_ascii=False,indent=2))


# 查看扫描件表格抽取结果
def send_request_table_info(table_id):
    response = request_with_jwt(
        url=host + 'extracting/table/{0}'.format(table_id),
       method='GET')

    # url = "http://idps2-preview.test.datagrand.cn/api/extracting/table/349"
    # send_review_request = requests.get(url,
    #                                    headers={
    #                                        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2NsYWltcyI6eyJ1c2VybmFtZSI6InN1cGVyYWRtaW5wcm8iLCJzdGF0dXMiOjEsInJvbGVfaWRzIjpbMV0sInVzZXJfaWQiOi0xLCJyb2xlX25hbWVfbGlzdCI6WyJcdTdiYTFcdTc0MDZcdTU0NTgiLCJzdXBlcmFkbWlucHJvIl0sIm5pY2tuYW1lIjoiSSBjYW4gYW55dGhpbmchIn0sImp0aSI6IjNkMzhlYTE0LTYyODItNGQ1YS05YTFmLTgwZTJiMjQwMDkxYSIsImV4cCI6MTU3NDk5NTA3MSwiZnJlc2giOmZhbHNlLCJpYXQiOjE1NzQ5MDg2NzEsInR5cGUiOiJhY2Nlc3MiLCJuYmYiOjE1NzQ5MDg2NzEsImlkZW50aXR5Ijoic3VwZXJhZG1pbnBybyJ9.ro1ybK9sAlB101obuQ_3Ks9k2e6FAR2Y0DtTC325OE8',
    #                                        })
    print(json.dumps(json.loads(response.content),ensure_ascii=False,indent=2))


# 1.pdf 平安电子件     2.pdf 大华扫描件     3.pdf  平安扫描件
send_request_check("/tmp/deploy_idps_dahua/data/check/scripts/table_extract_script/test/10.pdf",doc_form=2)
# send_request_check_info(83)
# send_request_table_extract("F:\\2.pdf")
# send_request_table_info(355)