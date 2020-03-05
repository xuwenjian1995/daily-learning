# coding: utf-8
from __future__ import unicode_literals


def custom_postprocess(pipline_result, params, logger):
    """
    :param pipline_result: 
    :param params: 当前文本的各种参数，包括doctype, rich_content等
    :param logger: 
    :return: 
    """
    # 在结果里加一个后处理value，默认是None
    processor_result = {}
    if 'postprocess' in pipline_result:
        for field in pipline_result['postprocess']:
            processor_result[field] = []
            if pipline_result['postprocess'][field]:
                for value, prob, index in pipline_result['postprocess'][field]:
                    processor_result[field].append([value, prob, index, None])
    # TODO 填充后处理值
    return processor_result

