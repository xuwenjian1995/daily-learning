# coding: utf-8
import fields_conf


class DoctypeDemoExtractor(object):

    """
    demo文档类型的所有规则
    """

    def __init__(self, content, logger):
        self.content = content
        self.fields = fields_conf.all_fields['demo']
        self.logger = logger

    def extract(self):
        pass

