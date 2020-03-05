# coding: utf-8
from __future__ import unicode_literals

configs = {
    'redis': {
        'redis_host': 'redis',
        'redis_port': 6379,
        'redis_db': 0,
        'redis_pwd': ''
    },
    'search_estimator': {
        'part_type': 'paragraph',
        'similarity': 'simple_similarity',
        'feature_type': 'ngram',
        'gram': 2,
        'stop_words': set()
    },
    'svm_estimator': {
        'part_type': 'paragraph',
        'stop_words': set(),
        'gram_range': (2, 2),
        'feature_num': 100,
    },
    'topn': 3
}
