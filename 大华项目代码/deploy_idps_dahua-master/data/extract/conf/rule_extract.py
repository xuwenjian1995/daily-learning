# coding: utf-8
from __future__ import unicode_literals
import json
from uuid import uuid4 as uuid
def get_uuid():
    return str(uuid()).replace("-","")

def extract(content, params, fields, pipline_result, logger):
    """
    规则抽取
    content: 文本内容
    fields: list of field_id (某个类型下的所有字段)
    pipline_result: pipline_result
    """
    # TODO
    logger.info("输出rich_content================================")
    rich_content = params["rich_content"]
    file_name = get_uuid()
    with open("/extract/data/{0}.json".format(file_name), "a") as f:
        logger.info(file_name)
        # logger.info(rich_content)
        f.write(json.dumps(rich_content))
    return {}

