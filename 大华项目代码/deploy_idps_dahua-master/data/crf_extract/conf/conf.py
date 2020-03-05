# coding: utf-8

import os

# online config
ROLE = os.getenv('ROLE', 'slave')
ADDRESS = '0.0.0.0'
PORT = 8000
MODEL_LINKS_DIR = os.getenv('MODEL_LINKS_DIR', 'model')
CONFIG_LINKS_DIR = os.getenv('CONFIG_LINKS_DIR', 'config')
OUTPUT_DIR = 'crf_extract/output'

# offline config
REDIS_HOST = 'redis'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PWD = ''

# rpc config
WORDSEG_HOST = "wordseg_rpc",
WORDSEG_PORT = 8000,
NER_HOST = "ner_rpc",
NER_PORT = 8000
