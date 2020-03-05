# coding=utf-8
# @email   : zhuyaobang@datagrand.com
# @create  : 2018/12/12 下午5:40
# @Author  : zhuyaobang
# @Software: PyCharm
uniform = {
    'enable': True,
    'rules': [
        [ur'，', ur','],
        [ur'。', ur'.'],
        [ur'·', ur'.'],
        [ur'．', ur'.'],
        [ur'（', ur'('],
        [ur'）', ur')'],
        [ur'：', ur':'],
        [ur'；', ur';'],
        [ur'／', ur'/'],
    ],
}

ocr_uniform = {
    'enable': False,
    'rules': [
        [ur'，', ur','],
        [ur'。', ur'.'],
        [ur'·', ur'.'],
        [ur'．', ur'.'],
        [ur'（', ur'('],
        [ur'）', ur')'],
        [ur'：', ur':'],
        [ur'；', ur';'],
        [ur'／', ur'/'],
    ],
}

detect_document = {
    'enable': False,
}

detect_header_footer = {
    'header_y': 0.095,
    'footer_y': 0.903
}
page_number_check = {
    'enable': False,
}

paragraph_detect_fast = {
    'enable': False,
    'min_para_len': 10,
}

find_swapped_paragraph = {
    'enable': False,
    'similar_threshold': 0.85
}
swap_paragraph = {
    'enable': False,
}

ocr_multi_source_merge = {
    'enable': False,
}

delete_chars = {
    'enable': True,
    'remove_list': [
        u'\t',
        u'\n',
        u' ',
        u'　',
        u'%',
        u'％',
        u'：',
        u':',
        u';',
        u'；',
        u'_'
    ]
}

fine_diff = {
    'enable': False,
}

post_process_difference = {
    'enable': True,
    'remove_chars': [
        u'_',
        u'-',
        u'.',
        u',',
        u'/',
        u'。',
        u'o',
        u'‰',
        u'】'
    ]
}

ocr_similar_post_process = {
    'enable': True,
    'extend_similar_words_file': u'extend_simi_word.txt',
    'remove_similar_words_file': u'disable_simi_word.txt'
}
