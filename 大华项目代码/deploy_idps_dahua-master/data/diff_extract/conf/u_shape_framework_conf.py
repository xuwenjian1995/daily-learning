# coding: utf-8
from __future__ import unicode_literals

relative_path_to_processor = 'diff_extract.app.processors'

processor_conf_list = [
    {
        "name": "common_offline_preprocess",
        "module": "common_offline_preprocess",
        "comment": "通用的离线预处理流程，包括保存field_config，清理老的model field_config、data数据，拷贝\3\4数据等",
        "args": {}
    },
    {
        "name": "extract_offline_preprocess",
        "module": "extract_offline_preprocess",
        "comment": "离线预处理流程，包括去除\3\4，生成模型数据等",
        "args": {
            "is_ignore_colon": True,
            "is_enable_table_clean": True
        }
    },
    {
        "name": "extract_offline_train",
        "module": "extract_offline_train",
        "comment": "比对抽取离线训练",
        "args": {}
    },
    {
        "name": "extract_online_preprocess",
        "module": "extract_online_preprocess",
        "comment": "比对抽取在线预处理",
        "args": {}
    },
    {
        "name": "extract_online_predict",
        "module": "extract_online_predict",
        "comment": "比对抽取在线预测",
        "args": {
            "similarity_threshold": 0.7,
            "is_enable_diff_table_extract": True,
            "is_ignore_colon": True,
            "is_filter_empty_result": True,
            "is_complete_match": True,
            "is_debug_out_to_file": True,
            "is_compress_to_speedup": True
        }
    },
    {
        "name": "save_models",
        "module": "save_models",
        "comment": "通用的模型存储",
        "args": {
        }
    },
    {
        "name": "load_models",
        "module": "load_models",
        "comment": "通用的模型读取",
        "args": {
        }
    },
]

workflow_conf_dict = {
    "offline":
        [
            "common_offline_preprocess",
            "extract_offline_preprocess",
            "extract_offline_train",
            "save_models"
        ],
    "online":
        [
            "load_models",
            "extract_online_preprocess",
            "extract_online_predict"
        ]
}
