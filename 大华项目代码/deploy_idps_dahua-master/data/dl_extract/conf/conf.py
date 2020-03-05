# coding:utf-8
# @Author: Zeng Yanneng
# @Date  : 2018/8/20

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division

import os
from multiprocessing import cpu_count

# TODO: Make sure to Disable it here for online environment
# DEBUG for multiprocessing purpose
DEBUG = False

# online config
FETCH_WORKER_CONNECTION_TIMEOUT = 20 * 60
FETCH_WORKER_REQUEST_TIMEOUT = 20 * 60

# offline config
REDIS_HOST = 'redis'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PWD = ''

# model types: "base",  "pos"
model_types = ['base', ]

# cut off config
CONTEXT_LEN = 2500
STEP = 50
MAX_LEN = 6000

DO_TABLE_NORMALIZE = True

DL_ONLINE_SERVICE_NAME = "127.0.0.1"
DL_ONLINE_SERVICE_NAME_GPU = "dl_extract_online_gpu"
DL_ONLINE_SERVICE_PORT = 8000
DL_ONLINE_SERVICE_TIMEOUT = 60 * 60
DL_ONLINE_PREDICT_CUT = 7000    # 分段predict切分长度
DL_ONLINE_PREDICT_CUT_OVERLAP = 1000  # 分段predict重叠部分
DL_ONLINE_PREDICT_CUT_LARGE = 30000 # 分段predict切分长度
DL_ONLINE_PREDICT_CUT_OVERLAP_LARGE = 1000  # 分段predict重叠部分
DL_ONLINE_PREDICT_BATCH_SIZE = 8
TEST_DL_ONLINE_PREDICT_REPEAT = 1
CRF_VITERBI_NBEST = 5 # Viterbi NBEST result

ELMO_SERVICE_URL = "100.100.22.2"
ELMO_SERVICE_PORT = 12272
ELMO_SERVICE_TIMEOUT = 60 * 60

BERT_SERVER_HOST = os.getenv("BERT_SERVER_HOST", "dl-online.datagrand.cn")
BERT_SERVER_PORT = int(os.getenv("BERT_SERVER_PORT", 6766))

BERT_PREDICT_TIMEOUT = 5 * 60 * 1000
BERT_TRAIN_TIMEOUT = 5 * 60 * 1000

# DL Extract Server Conf
PREPROCESS_CPU_COUNT = 16

# Field_config allowed fields
DL_FIELD_CONFIG_ALLOWED_FIELDS = ['bert_en', 'char_emb_en', 'pre_emb', 'word_emb_en', 'title_emb_en',
                                  'batch_size', 'loss_layer_type', 'max_epoch']

# 定义至少要evaluate_during_train多少次
# 总Step数除以这个数得出每多少次Step evaluate一次。所以实际evaluate次数可能略多于这个次数
DL_TRAIN_EVALUATE_COUNT = 20

# F1 value between 0 and 1
STOP_TRAIN_WHEN_F1_REACH = 1

# Bert server timeout. Including initializing and extracting time. In milliseconds
BERT_SERVER_TIMEOUT = 10 * 60 * 1000

# bert client config
MAX_SEQ_LEN = 124
