#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Yang Huiyu
# @Date  : 2018/12/5

OFFLINE_WORKFLOW_PARAMS = [
    {
        "cmd": "config_offline",
        "args": {}
    },
    {
        "cmd": "gen_train_data",
        "args": {
            "context_before_len": 10,
            "context_after_len": 5
        }
    },
    {
        "cmd": "get_inside_feature",
        "args": {
            "ngram_df_threshold": 0.6,
            "prefix_suffix_max_len": 4,
            "prefix_suffix_df_threshold": 0.5
        }
    },
    {
        "cmd": "get_outside_feature",
        "args": {}
    },
    {
        "cmd": "clean_outside_rules",
        "args": {}
    },
    {
        "cmd": "clean_inside_rules",
        "args": {}
    },
    {
        "cmd": "evaluate_outside_rules",
        "args": {
            "extract_len_coefficient": 1.5
        }
    },
    {
        "cmd": "evaluate_inside_rules",
        "args": {}
    },
    {
        "cmd": "build_inverted_index",
        "args": {}
    },
    {
        "cmd": "dump_model",
        "args": {}
    }
]