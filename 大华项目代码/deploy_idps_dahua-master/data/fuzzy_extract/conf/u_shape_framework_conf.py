# coding=utf-8
# email:  yuexiaolong@datagrand.com
# create: 2019/04/19

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

relative_path_to_processor = '..app.processors'

processor_conf_list = [
    {
        "name": "train_data_preprocess",
        "module": "train_data_preprocess",
        "args": {},
        "comment": "required",
    },
    {
        "name": "predict_data_preprocess",
        "module": "predict_data_preprocess",
        "args": {},
        "comment": "required",
    },
    {
        "name": "train_search",
        "module": "train_search",
        "args": {},
        "comment": "optional",
    },
    {
        "name": "predict_search",
        "module": "predict_search",
        "args": {},
        "comment": "optional",
    },
    {
        "name": "train_stat",
        "module": "train_stat",
        "args": {},
        "comment": "optional",
    },
    {
        "name": "predict_stat",
        "module": "predict_stat",
        "args": {},
        "comment": "optional",
    },
    {
        "name": "train_classifier",
        "module": "train_classifier",
        "args": {},
        "comment": "optional",
    },
    {
        "name": "predict_classifier",
        "module": "predict_classifier",
        "args": {},
        "comment": "optional",
    },
    {
        "name": "save_model",
        "module": "save_model",
        "args": {},
        "comment": "required",
    },
    {
        "name": "merge_results",
        "module": "merge_results",
        "args": {},
        "comment": "required",
    },
]

workflow_conf_dict = {
    'train': [
        'train_data_preprocess',
        'train_search',
#        'train_classifier',
        'train_stat',
        'save_model',
    ],
    'predict': [
        'predict_data_preprocess',
        'predict_search',
#        'predict_classifier',
        'predict_stat',
        'merge_results',
    ],
    'train_classifier': [
        'train_data_preprocess',
        'train_classifier',
    ],
    'predict_classifier': [
        'predict_data_preprocess',
        'predict_classifier',
    ]
}
