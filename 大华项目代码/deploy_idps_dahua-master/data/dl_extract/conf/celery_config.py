# coding=utf-8
# email: gujiasheng@datagrand.com

import os

MQ_USER_NAME = os.environ.get('MQ_USER_NAME', 'guest')
MQ_USER_PASSWORD = os.environ.get('MQ_USER_PASSWORD', 'guest')
MQ_HOST = os.environ.get('MQ_HOST', 'rabbitmq')
MQ_PORT = os.environ.get('MQ_PORT', 5672)
MQ_VHOST = os.environ.get('MQ_VHOST', '/')
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
EXTRACT_QUEUE = os.environ.get('EXTRACT_QUEUE', 'predict_queue')


# Actual Celery Settings
# http://docs.celeryproject.org/en/latest/userguide/configuration.html
broker_url = 'amqp://{}:{}@{}:{}/{}'.format(MQ_USER_NAME, MQ_USER_PASSWORD, MQ_HOST, MQ_PORT, MQ_VHOST)
result_backend = 'redis://{}:{}/1'.format(REDIS_HOST, REDIS_PORT)

# imports = ('demo.tasks.demo_task',
#            'demo.tasks.another_demo_task')
task_protocol = 1
task_routes = {
    'predict_task': {'queue': EXTRACT_QUEUE},
    # 'predict_1_91': {'queue': 'predict_1_91_queue'}
}
task_queues = {
    EXTRACT_QUEUE: {
        'exchange': 'default',
        'routing_key': EXTRACT_QUEUE
    }
}
# result_backend = 'redis://localhost:6379/0'
# task_create_missing_queues = 'Disabled'
task_serializer = 'json'
result_serializer = 'json'
result_expires = 60 * 60 * 24
accept_content = ['json', 'msgpack']
worker_prefetch_multiplier = 1
worker_concurrency = 1
