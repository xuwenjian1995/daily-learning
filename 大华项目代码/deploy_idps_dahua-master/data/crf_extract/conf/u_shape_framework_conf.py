# -*- coding: utf-8 -*-
# email: qianyixin@datagrand.com
# date: 2019-05-11 16:47
from __future__ import unicode_literals

relative_path_to_processor = '..app.processors'

processor_conf_list = [
    {
        "name": "common_offline_preprocess",
        "module": "common_offline_preprocess",
        "args": {}
    },
    {
        "name": "init_rpc_client",
        "module": "init_rpc_client",
        "args": {
            "WORDSEG_HOST": "wordseg_rpc",
            "WORDSEG_PORT": 8000,
            "NER_HOST": "ner_rpc",
            "NER_PORT": 8000
        }
    },
    {
        "name": "gen_train_data",
        "module": "gen_train_data",
        "args": {
            "context_len": 3000,
            "step": 50,
            "max_len": 1e10
        }
    },
    {
        "name": "train_model",
        "module": "train_model",
        "args": {}
    },
    {
        "name": "preprocess_feature",
        "module": "preprocess_feature",
        "args": {}
    },
    {
        "name": "predict_nbest",
        "module": "predict_nbest",
        "args": {
            "nbest": 5,
            "norm_prob": True
        }
    },
    {
        "name": "merge_result",
        "module": "merge_result",
        "args": {}
    },
]
workflow_conf_dict = {
    "train": [
        "common_offline_preprocess",
        "init_rpc_client",
        "gen_train_data",
        "train_model"
    ],
    "predict": [
        "preprocess_feature",
        "predict_nbest",
        "merge_result"
    ]
}
