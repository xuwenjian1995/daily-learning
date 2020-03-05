#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Yang Huiyu
# @Date  : 2018/12/5

ONLINE_WORKFLOW_PARAMS = [
    {
        "cmd": "rule_extract",
        "args": {}
    },
    {
        "cmd": 'merge_raw_result',
        "args": {}
    },
    {
        "cmd": 'rank_by_result',
        "args": {
            "internal_feature_weight": 0.4
        }
    },
    {
        "cmd": 'rank_by_context',
        "args": {
            "context_before_len": 10,
            "context_after_len": 5
        }
    },
    {
        "cmd": 'clean_result',
        "args": {
            "outside_confidence": 0.3,
            "inside_confidence": 0.4
        }
    },
    {
        "cmd": 'merge_final',
        "args": {}
    }
]