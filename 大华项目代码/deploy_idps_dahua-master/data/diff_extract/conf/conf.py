# coding=utf-8


# online参数
RECV_PORT = 8000
PREDICT_ROUTER = '/extract'
PREDICT_PATH_ROUTER = '/extract_with_path'
RELOAD_ROUTER = '/reload'
PREDICT_FIELDS_ROUTER = '/extract_by_fields'

# offline config
REDIS_HOST = 'redis'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PWD = ''

# field workflow config 针对每个字段配置不同的workflow
field_workflow_online_config = {
    # 1: 'online',
    # 2: 'online',
}
field_workflow_offline_config = {

}
