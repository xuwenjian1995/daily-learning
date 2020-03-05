#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-06-24 11:57
# @Author  : zhangyicheng@datagrand.com
from __future__ import unicode_literals

relative_path_to_processor = '..processors'

processor_conf_list = [
    {
        'name': 'dump_rules',
        'module': 'dump_rules',
        'comment': '',
        'args': {}
    },
    {
        'name': 'evaluate',
        'module': 'evaluate',
        'comment': '',
        'args': {
            'evaluate_predefined_rule_extract_url': 'http://evaluate_extract:8000/predefined_rule_extract',
            'evaluate_predefined_rule_extract_with_path_url':
                'http://evaluate_extract:8000/predefined_rule_extract_with_path',
            'evaluate_extract_normalize_url': 'http://evaluate_extract:8000/normalize',
            'extract_with_path': True,
            'use_rich_content': True,
        }
    },
    {
        'name': 'reload_extract',
        'module': 'reload_extract',
        'comment': '',
        'args': {'extract_reload_url': 'http://extract:8000/reload'}
    },
    {
        'name': 'evaluate_reload_extract',
        'module': 'reload_extract',
        'comment': '',
        'args': {'extract_reload_url': 'http://evaluate_extract:8000/reload'}
    },
    {
        'name': 'validate_rule',
        'module': 'validate_rule',
        'comment': '',
        'args': {}
    },
]

workflow_conf_dict = {
    'evaluate':
        [
            'dump_rules',
            'evaluate_reload_extract',
            'evaluate',
        ],
    'reload':
        [
            'dump_rules',
            'reload_extract',
        ],
    'evaluate_reload':
        [
            'dump_rules',
            'evaluate_reload_extract',
        ],
    'validate_rule':
        [
            'validate_rule',
        ],
}
