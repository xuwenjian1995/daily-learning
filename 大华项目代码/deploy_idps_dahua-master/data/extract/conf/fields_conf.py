# coding : utf-8
from collections import namedtuple


"""
存放人工配规则的字段（特定文档类型下的）
"""
Field = namedtuple('Field', ['id', 'name'])

demo_field1 = Field('1', 'demo字段1')
demo_field2 = Field('2', 'demo字段2')

# TODO

all_fields = {
    "demo": [demo_field1, demo_field2]  # 文档类型为demo的所有字段
}
