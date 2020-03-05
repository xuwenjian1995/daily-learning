# coding=utf-8


# online参数
RECV_PORT = 8080
PREDICT_ROUTER = '/extract'
PREDICT_PATH_ROUTER = '/extract_with_path'
RELOAD_ROUTER = '/reload'
PREDICT_BY_FIELDS = '/extract_by_fields'

# offline config
REDIS_HOST = 'redis'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PWD = ''

# field workflow config 针对每个字段配置不同的workflow
field_workflow_online_config = {
    'default': 'model_online'
}
field_workflow_offline_config = {
    'default': 'offline'
}

field_config = {
    "default_field": {
        "recognize_similarity": {
            "estimator": {
                'similarity': 'simple_similarity', 'feature_type': 'ngram', 'gram': 2
            },
            "features": [
                "pre_table_lines",
                "label_table_indices",
                "avg_tagged_cell_count",
                "table_row_titles",
                "table_column_titles",
                "tagged_cells"
            ]
        },
        "extract_svm": {
            "estimator": {
                "class_weight": {1: 10}
            },
            "features": [
                "table_all_cells",
                "table_row_titles",
                "table_column_titles"
            ]
        },
        "extract_search": {
            "estimator": {
                "similarity": "simple_similarity",
                "feature_type": "ngram",
                "gram": 2,
                "stop_words": set()
            },
            "features": ["tagged_cells"]
        }
    }
}
