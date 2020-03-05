# coding: utf-8
from __future__ import unicode_literals

relative_path_to_processor = '..app.processors'

processor_conf_list = [
    {
        "name": "common_offline_preprocess",
        "module": "common_offline_preprocess",
        "comment": "通用的离线预处理流程，包括保存field_config，清理老的model field_config、data数据，拷贝\3\4数据等",
        "args": {}
    },
    {
        "name": "train_data_preprocess",
        "module": "train_data_preprocess",
        "comment": "离线模块数据预处理",
        "args": {
        }
    },
    {
        "name": "train_recognize_similarity_estimator",
        "module": "train_recognize_similarity_estimator",
        "comment": "基于相似度表格识别模型离线训练",
        "args": {}
    },
    {
        "name": "train_extract_search_estimator",
        "module": "train_extract_search_estimator",
        "comment": "search抽取离线训练",
        "args": {}
    },
    {
        "name": "train_extract_svm_estimator",
        "module": "train_extract_svm_estimator",
        "comment": "svm抽取离线训练",
        "args": {}
    },
    {
        "name": "predict_data_preprocess",
        "module": "predict_data_preprocess",
        "comment": "在线预测模块数据预处理",
        "args": {
        }
    },
    {
        "name": "predict_recognize_similarity_estimator",
        "module": "predict_recognize_similarity_estimator",
        "comment": "基于相似度的表格识别在线预测",
        "args": {
            "estimator": {"min_confidence": 0.6}
        }
    },
    {
        "name": "predict_extract_search_estimator",
        "module": "predict_extract_search_estimator",
        "comment": "基于search模型抽取的在线预测",
        "args": {
            "estimator": {"min_confidence": 0.6}
        }
    },
    {
        "name": "predict_extract_svm_estimator",
        "module": "predict_extract_svm_estimator",
        "comment": "基于svm模型抽取的在线预测",
        "args": {
            "estimator": {"min_confidence": 0.15}
        }
    },
    {
        "name": "save_models",
        "module": "save_models",
        "comment": "通用的模型存储",
        "args": {}
    },
    {
        "name": "model_result_merge",
        "module": "model_result_merge",
        "comment": "合并各类estimator的抽取结果",
        "args": {}
    },
    {
        "name": "model_extract",
        "module": "model_extract",
        "comment": "表格模型抽取",
        "args": {}
    },
    {
        "name": "script",
        "module": "script",
        "comment": "表格脚本抽取",
        "args": {
            "script_package": "table_extract.app.scripts"
        }
    },
    {
        "name": "model_script_result_merge",
        "module": "model_script_result_merge",
        "comment": "合并模型和表格抽取结果",
        "args": {}
    },
    {
        "name": "merge_field_config",
        "module": "merge_field_config",
        "comment": "获取字段训练参数",
        "args": {}
    }
]

workflow_conf_dict = {
    "offline":  # 先表格判别，再表格抽取离线训练workflow
        [
            "merge_field_config",
            "common_offline_preprocess",
            "train_data_preprocess",
            "train_recognize_similarity_estimator",
            "train_extract_search_estimator",
            "train_extract_svm_estimator",
            "save_models"
        ],
    "model_online":  # 先表格判别，再表格抽取在线抽取workflow
        [
            "predict_data_preprocess",
            "predict_recognize_similarity_estimator",
            # "predict_extract_search_estimator",
            "predict_extract_svm_estimator",
            "model_result_merge"
        ],
    "online":  # 综合模型抽取和脚本抽取结果
        [
            "model_extract",
            "script",
            "model_script_result_merge"
        ]
}
