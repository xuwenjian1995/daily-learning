# coding=utf-8
from __future__ import unicode_literals

processor_conf_list = [
    {
        "name": "area_text",
        "module": "area_text",
        "args": {},
    },
    {
        "name": "prepare_file",
        "module": "prepare_file",
        "args": {},
    },
    {
        "name": "cache",
        "module": "cache",
        "args": {
            'enable': True,
            'redis_host': 'redis',
            'redis_port': 6379,
            'redis_db': 10,
            'redis_pwd': '',
        }
    },
    {
        "name": "node",
        "module": "node",
        "args": {
            'node_host': 'node_server_master',
            'node_port': '3001',
            'timeout': 600,
        }
    },
    {
        "name": "pdf2txt",
        "module": "pdf2txt",
        "args": {
            'public_server': False,
            'public_args': {
                'file_server_user_name': 'pdf2txt',
                'file_server_user_password': '2XNdL5eN9E8XXpMf',
                'mq_host': '42.159.9.163',
                'mq_port': 15688
            },
            'mq_host': 'rabbitmq',
            'mq_port': '5672',
            'detect_table': True,
            'detect_header_footer': True,
            'detect_title': False,
            'file_type': 'normal',
        }
    },
    {
        "name": "word_to_pdf",
        "module": "word_to_pdf",
        "args": {
            'unoconv_host': 'unoconv',
            'unoconv_port': '3000',
            'timeout': 600,
        }
    },
    {
        "name": "txt_to_docx",
        "module": "txt_to_docx",
        "args": {}
    },
    {
        "name": "extract_audit_tables",
        "module": "extract_audit_tables",
        "args": {},
    },
    {
        "name": "save_audit_tables",
        "module": "save_audit_tables",
        "args": {},
    },
    {
        "name": "content_correct",
        "module": "content_correct",
        "args": {},
    },
]

workflow_conf_dict = {
    'node': [
        'prepare_file',
        'cache',
        'txt_to_docx',
        'word_to_pdf',
        'node',
    ],
    'pdf2txt': [
        'prepare_file',
        'cache',
        'txt_to_docx',
        'word_to_pdf',
        'pdf2txt',
        # 'content_correct',
    ],
    'area_text': [
        'prepare_file',
        'area_text',
    ],
    'audittable': [
        'prepare_file',
        'cache',
        'word_to_pdf',
        'pdf2txt',
        'content_correct',
        'extract_audit_tables',
        'save_audit_tables',
    ]
}
