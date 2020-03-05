# coding=utf-8
# email:  yuexiaolong@datagrand.com
# create: 2019/05/06

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

relative_path_to_processor = '..app.processors'

processor_conf_list = [{
    "name": "load_data",
    "module": "load_data",
    "args": {},
    "comment": "required",
}, {
    "name": "value_analysis",
    "module": "value_analysis",
    "args": {},
    "comment": "optional",
}, {
    "name": "density_analysis",
    "module": "density_analysis",
    "args": {},
    "comment": "optional",
}, {
    "name": "start_index_analysis",
    "module": "start_index_analysis",
    "args": {},
    "comment": "optional",
}, {
    "name": "rich_content_analysis",
    "module": "rich_content_analysis",
    "args": {},
    "comment": "optional",
}, {
    "name": "save_model",
    "module": "save_model",
    "args": {},
    "comment": "required",
}, {
    "name": "load_model",
    "module": "load_model",
    "args": {},
    "comment": "required",
}, {
    "name": "generate_sample_table",
    "module": "generate_sample_table",
    "args": {},
    "comment": "required",
}, {
    "name": "load_raw_data",
    "module": "load_raw_data",
    "args": {
        'rich_content_enable': 0,
        'light_content_mode': 1,
    },
}, {
    "name": "samples_table",
    "module": "samples_table",
    "args": {},
}, {
    "name": "fields_table",
    "module": "fields_table",
    "args": {},
}, {
    "name": "save_train_data",
    "module": "save_train_data",
    "args": {},
}]

workflow_conf_dict = {
    'train': [
        'load_data',
        'generate_sample_table',
        'density_analysis',
        'value_analysis',
        'start_index_analysis',
        'rich_content_analysis',
        'save_model',
    ],
    'train_by_doc_type': ['load_raw_data', 'samples_table', 'fields_table', 'save_train_data',],
    'predict': [
        'load_model',
    ]
}
