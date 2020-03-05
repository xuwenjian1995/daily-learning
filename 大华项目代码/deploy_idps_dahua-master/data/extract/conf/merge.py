# coding: utf-8
from __future__ import unicode_literals

priorities = {
    'priority_1': ['diff_extract', 'dl_extract', 'table_extract', 'crf_extract', 'rule_extract', 'predefined_rule_extract', 'auto_rule_extract'],
    'priority_2': ['diff_extract', 'dl_extract', 'table_extract', 'rule_extract', 'crf_extract', 'predefined_rule_extract', 'auto_rule_extract'],
    'priority_3': ['table_extract','diff_extract', 'dl_extract', 'predefined_rule_extract', 'rule_extract', 'crf_extract', 'auto_rule_extract'],
    'priority_4': ['table_extract']
}

fields_merge_config = {
    'field_default': {  # 字段默认配置
        'priority': 'priority_3',  # 组件优先级
        'forbidden_components': [],  # 禁用的组件
        'merge_components': False,  # 所有组件的结果是否应该被合并
        'components_prob': {  # 各个组件的最小置信度
            'table_extract': 0.,
            'crf_extract': 0.01,
            'rule_extract': 0.,
            'predefined_rule_extract': 0.,
            'auto_rule_extract': 0.5,
            'dl_extract': 0.2,  # 小数据测试时用0.3，正常业务数据一般取0.2
            'diff_extract': 0.
        }
    },
}


def _get_all_fields(pipeline_result):
    fields = []
    for component in ['diff_extract', 'dl_extract', 'table_extract', 'crf_extract', 'rule_extract', 'predefined_rule_extract', 'auto_rule_extract']:
        if component not in pipeline_result:
            continue
        fields.extend(pipeline_result[component].keys())
    fields = list(set(fields))
    return fields


def merge(pipeline_result, fields, logger):
    """
    merge策略
    result: pipeline result
    """
    fields = _get_all_fields(pipeline_result)
    merge_result = {}

    for field in fields:
        merge_config = fields_merge_config.get(field, fields_merge_config['field_default'])
        field_values = []
        for component in priorities[merge_config['priority']]:
            if component not in pipeline_result or field not in pipeline_result[component] \
                    or component in merge_config['forbidden_components']:
                continue
            component_field_values = [value for value in pipeline_result[component][field] if
                                      value[1] >= merge_config['components_prob'][component]]
            if component_field_values and not merge_config['merge_components']:
                field_values = component_field_values
                break
            else:
                field_values.extend(component_field_values)
        merge_result[field] = field_values
    return merge_result

