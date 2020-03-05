# coding: utf-8
from __future__ import unicode_literals

document_process = {
    'host': 'document_process',
    'port': 8000,
    'timeout': 1800,
}

ocr = {
    'timeout': 1800,
    'use': 'ys',
    'ys': {
        'host': 'http://10.1.40.13:51401/ysocr/ocr',
        'download': 'http://10.1.40.13:51401/file'
    },
    'ali': {
        'pdf_host': 'http://10.1.40.13:51401/uploadapi/imgpdf2textpdf',  # pdf文件调用路由
        'image_host': 'http://10.1.40.13:51401/uploadapi/img2dtextpdf_ali_service',  # 图片调用的路由
        'file_key': 'files',  # 'ALI': 'files', 'TAIBI': 'file',
    }
}

extract = {
    'host': 'extract',
    'port': 8000,
    'timeout': 1800,
}

diff = {
    'url': 'http://contract_diff/diff/',
    'timeout': 1800,
    'use_path': True,
}

review = {
    'host': 'contract_check',
    'port': 10110,
    'timeout': 1800,
    'use_path': False,
}

# file_type:[url, recognition_category, detect_category] (路由, 文字识别模型, 文字检测模型)
ocr_extract = {
    'business_license': ['http://10.1.40.13:51401/bizlicense/extract', 'business_license',
                         'business_license'],  # 营业执照,
    'invoice': ['http://10.1.40.13:51401/invoice_extract', 'invoice', 'invoice'],  # 发票
    'idcard': ['http://10.1.40.13:51401/idcard/extract', 'idcard', 'idcard'],  # 身份证
    'document': ['http://10.1.40.13:51401/ysocr/ocr', 'document', 'document'],  # 通用文档
    'jiushi': ['http://10.1.40.13:51401/document/extract', 'document', 'document'],  #jiushi 红头文件
    'timeout': 1800,
}

gtja_extract = {
    'url': 'http://gtja:17165/extract',
    'timeout': 1800,
}

table = {}
prepare_diff = {}
write_diff_result = {}
prepare_dp = {}
write_dp_status = {}
prepare_extract = {}
write_extract_result = {}
prepare_review = {}
write_review = {}
prepare_table = {}
write_table = {}
prepare_ocr_extract = {}
write_ocr_extract_result = {}
prepare_gtja_extract = {}
write_gtja_extract_result = {}
