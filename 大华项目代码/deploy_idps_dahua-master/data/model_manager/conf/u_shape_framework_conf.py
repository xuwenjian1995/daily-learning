# coding=utf-8
from __future__ import unicode_literals

processor_conf_list = [
    {
        "name": "merge_group_field_config",
        "module": "merge_group_field_config",
        "args": {},
    },
    {
        "name": "dirs_generator",
        "module": "dirs_generator",
        "args": {},
    },
    {
        "name": "standard_data_generator",
        "module": "standard_data_generator",
        "args": {},
    },
    {
        "name": "normalize",
        "module": "pre_process.normalize",
        "args": {
            'is_english': False,
            'norm_arabic_num': True,
            'norm_chinese_num': True,
            'norm_money_num': True,
        }
    },
    {
        "name": "normalize_english",
        "module": "pre_process.normalize",
        "args": {
            'is_english': True,
            'norm_arabic_num': True,
            'norm_chinese_num': True,
            'norm_money_num': True,
        }
    },
    {
        "name": "rich_content_input",
        "module": "pre_process.rich_content_input",
        "args": {
            "merge_table": True
        },
    },
    {
        "name": "remove_space",
        "module": "pre_process.remove_space",
        "args": {
            'is_tagged_content': True
        }
    },
    {
        "name": "stem",
        "module": "pre_process.stem",
        "args": {
            'stemmer': "porter",
            'is_tagged_content': True,
        }
    },
    {
        "name": "use_fields_analysis",
        "module": "use_fields_analysis",
        "args": {},
    },
    {
        "name": "write_message_b",
        "module": "write_message_b",
        "args": {},
    },
    {
        "name": "check_result",
        "module": "check_result",
        "args": {},
    },
    {
        "name": "model_evaluate",
        "module": "model_evaluate",
        "args": {
            'use_rich_content': True,
            'extract_with_path': False,
            'extract_by_fields_with_path_url': 'http://evaluate_extract:8000/extract_by_fields_with_path',
            'extract_by_fields_url': 'http://evaluate_extract:8000/extract_by_fields',
            'timeout': 1800,
        }
    },
    {
        "name": "write_train_evaluate",
        "module": "write_train_evaluate",
        "args": {},
    },
    {
        "name": "model_delete",
        "module": "model_delete",
        "args": {},
    },
    {
        "name": "model_reload",
        "module": "model_reload",
        "args": {
            'subservice_urls': {
                'dl_extract': 'http://dl_extract_online:8000/reload',
                'crf_extract': 'http://crf_extract_online:8000/reload',
                'auto_rule_extract': 'http://auto_rule_extract_online:8000/reload',
                'fields_analysis': 'http://fields_analysis_online:8000/reload',
                'fuzzy_extract': 'http://fuzzy_extract_online:8000/reload',
                'diff_extract': 'http://diff_extract_online:8000/reload',
                'table_extract': 'http://table_extract_online:8080/reload',
                'predefined_rule_extract': 'http://predefined_rule_extract:8000/reload'
            },
            'enable_predefined_rule_reload': False,
            'default_reload_services': ['crf_extract', 'dl_extract', 'auto_rule_extract', 'fields_analysis']
        }
    },
    {
        "name": "evaluate_model_reload",
        "module": "model_reload",
        "args": {
            'subservice_urls': {
                'dl_extract': 'http://evaluate_dl_extract_online:8000/reload',
                'crf_extract': 'http://evaluate_crf_extract_online:8000/reload',
                'auto_rule_extract': 'http://evaluate_auto_rule_extract_online:8000/reload',
                'fields_analysis': 'http://evaluate_fields_analysis_online:8000/reload',
                'fuzzy_extract': 'http://evaluate_fuzzy_extract_online:8000/reload',
                'diff_extract': 'http://evaluate_diff_extract_online:8000/reload',
                'table_extract': 'http://evaluate_table_extract_online:8080/reload',
                'predefined_rule_extract': 'http://predefined_rule_extract:8000/evaluate_reload'
            },
            'enable_predefined_rule_reload': True,
            'default_reload_services': ['crf_extract', 'dl_extract', 'auto_rule_extract', 'fields_analysis']
        }
    },
]

workflow_conf_dict = {
    # 检查结果，更新数据库的状态；
    'check_result': [
        'check_result',
    ],

    # 模型加载
    'model_reload': [
        'model_reload',
    ],

    # evaluate模型加载
    'evaluate_model_reload': [
        'evaluate_model_reload',
    ],

    # 模型评估
    'model_evaluate': [
        'evaluate_model_reload',
        'dirs_generator',
        'model_evaluate',
        'write_train_evaluate',
    ],

    # 模型删除
    'model_delete': [
        'model_delete',
    ],

    # 生成数据，并写message_b到fields_analysis中；
    'data_process': [
        'dirs_generator',
        'merge_group_field_config',
        'standard_data_generator',
        'use_fields_analysis',
        'write_message_b',
    ],

    # 预处理数据（归一化，使用富文本信息等）;
    'standard_data_with_rich_content_normalize': [
        'rich_content_input',
        'normalize',
    ],
    'en_standard_data_with_rich_content_normalize': [
        'rich_content_input',
        'normalize_english',
        'remove_space',
        'stem',
    ],
    'standard_data_with_normalize': [
        'normalize',
    ],
    'en_standard_data_with_normalize': [
        'normalize_english',
        'remove_space',
        'stem',
    ]
}
