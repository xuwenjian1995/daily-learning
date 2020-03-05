#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-05-16 18:00
# @Author  : zhangyicheng@datagrand.com
from __future__ import unicode_literals

relative_path_to_processor = '..processors'

processor_conf_list = [
    {
        'name': 'assertion_merge',
        'module': 'assertion_merge',
        'comment': 'merge results of "assertion" type check, e.g. boundary consistency check',
        'args': {}
    },
    {
        'name': 'boundary_consistency_check',
        'module': 'boundary_consistency_check',
        'comment': '',
        'args': {
            'error_threshold': .2
        }
    },
    {
        'name': 'model_results_compare',
        'module': 'model_results_compare',
        'comment': 'compare merged predict results with the manually labeled data',
        'args': {}
    },
    {
        'name': 'model_train',
        'module': 'model_train',
        'comment': '',
        'args': {
            'model_train_url': 'http://extract_admin_api:10001/train/model_do',
            'login_url': 'http://extract_admin_api:10001/login'
        }
    },
    {
        'name': 'model_evaluate',
        'module': 'model_evaluate',
        'comment': 'evaluate trained model for label quality check',
        'args': {}
    },
    {
        'name': 'final_merge',
        'module': 'final_merge',
        'comment': 'write reports and merge assertion results with the compared results(we should be attentive that '
                   'predict results and assertion results are not on the same level.)',
        'args': {
            'context_length': 200
        }
    },
    {
        'name': 'postprocess',
        'module': 'postprocess',
        'comment': 'post process final merged results and generate a report',
        'args': {}
    },
    {
        'name': 'preprocess',
        'module': 'preprocess',
        'comment': '',
        'args': {
            'use_rich_content': True
        }
    },
]

workflow_conf_dict = {
    'label_quality_check':
        [
            'preprocess',
            'model_train',
            'model_evaluate',
            'model_results_compare',
            'boundary_consistency_check',
            'assertion_merge',
            'final_merge',
            'postprocess'
        ],
}
