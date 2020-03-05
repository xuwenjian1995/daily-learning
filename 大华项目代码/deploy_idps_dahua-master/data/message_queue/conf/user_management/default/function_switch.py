# coding: utf-8
from __future__ import unicode_literals

function_switch = {
    'label': {
        'pre_label': {
            'enable': True,
            'use_rich_content': True,
            'extract_with_path': True,
        },
    },
    'extract': {
        'use_rich_content': True,
        'extract_with_path': True,
    },
    'diff': {
        'dp_args': {
            'detect_table': True,  # 如果速度慢，则将该配置设置为False即可；
            'detect_header_footer': True,
            'detect_title': False,
        }
    },
    'review': {
        'extract': {
            'enable': True,
            'use_rich_content': True,
            'extract_with_path': True,
        },
    },
    'dp': {
        'use_rich_content': True,
    },
}
