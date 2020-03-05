#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Yang Huiyu
# @Date  : 2019/6/24
relative_path_to_processor = 'auto_rule_extract.processors'

processor_conf_list = [
    {
        "name": "config_offline",
        "module": "config_offline",
        "args": {}
    },
    {
        "name": "gen_train_data",
        "module": "gen_train_data",
        "args": {
            "context_before_len": 10,
            "context_after_len": 5
        }
    },
    {
        "name": "get_inside_feature",
        "module": "get_inside_feature",
        "args": {
            "ngram_df_threshold": 0.6,
            "prefix_suffix_max_len": 4,
            "prefix_suffix_df_threshold": 0.5
        }
    },
    {
        "name": "get_outside_feature",
        "module": "get_outside_feature",
        "args": {}
    },
    {
        "name": "clean_outside_rules",
        "module": "clean_outside_rules",
        "args": {}
    },
    {
        "name": "clean_inside_rules",
        "module": "clean_inside_rules",
        "args": {}
    },
    {
        "name": "evaluate_outside_rules",
        "module": "evaluate_outside_rules",
        "args": {
            "extract_len_coefficient": 1.5
        }
    },
    {
        "name": "evaluate_inside_rules",
        "module": "evaluate_inside_rules",
        "args": {}
    },
    {
        "name": "build_inverted_index",
        "module": "build_inverted_index",
        "args": {}
    },
    {
        "name": "dump_model",
        "module": "dump_model",
        "args": {}
    },
    {
        "name": "rule_extract",
        "module": "rule_extract",
        "args": {}
    },
    {
        "name": 'merge_raw_result',
        "module": 'merge_raw_result',
        "args": {}
    },
    {
        "name": 'rank_by_result',
        "module": 'rank_by_result',
        "args": {
            "inside_feature_weight": 0.4
        }
    },
    {
        "name": 'rank_by_context',
        "module": 'rank_by_context',
        "args": {
            "context_before_len": 10,
            "context_after_len": 5
        }
    },
    {
        "name": 'clean_result',
        "module": 'clean_result',
        "args": {
            "outside_confidence": 0.3,
            "inside_confidence": 0.4
        }
    },
    {
        "name": 'merge_final',
        "module": 'merge_final',
        "args": {}
    }
]

workflow_conf_dict = {
    "train": [
        'config_offline',
        'gen_train_data',
        'get_inside_feature',
        'get_outside_feature',
        'clean_outside_rules',
        'clean_inside_rules',
        'evaluate_outside_rules',
        'evaluate_inside_rules',
        'build_inverted_index',
        'dump_model'
    ],
    "predict": [
        'rule_extract',
        'merge_raw_result',
        'rank_by_result',
        'rank_by_context',
        'clean_result',
        'merge_final'
    ]
}
