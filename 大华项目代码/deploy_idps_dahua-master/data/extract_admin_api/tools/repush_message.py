# coding=utf-8
# email:  younixiao@qq.com
# create: 2018年11月16日星期五 16:00
import json
import sys
from os import path as os_path

reload(sys)
sys.path.append(os_path.join(os_path.dirname(__file__), os_path.pardir, 'api'))
from app import flask_app, logger
from shared_orm.models.docs_model import DocsModel
from shared_orm.models.tasks_model import TasksModel
from app.common.get_file_redis import get_file_redis, FILE_KEY


def push_file_message(doc_list, tag_type_id, pre_tag=False):
    """ 推数据到消息队列
        """
    success = True
    try:
        redis = get_file_redis()
        cmd = ['2txt2json']
        cmd.append('extract') if pre_tag else ''
        document_format = flask_app.config.get('DOCUMENT_FORMAT')
        if document_format and document_format == 'True':
            cmd.append('format')
        logger.info('repush message')
        logger.info(cmd)
        message_dict = dict(
            cmd=cmd,
            tag_type=tag_type_id,
        )
        for doc in doc_list:
            message_dict['id'] = int(doc.id)
            message_dict['local_path'] = doc.unique_name
            print message_dict
            redis.rpush(FILE_KEY, json.dumps(message_dict))
            redis.rpush("test", json.dumps(message_dict))
    except Exception as e:
        logger.error('repush message failed')
        logger.error(e)
        success = False
    return success


if __name__ == "__main__":
    tasks = sys.argv[1:]
    print tasks
    if not tasks:
        'tasks id is required'
        exit()

    for task in tasks:
        task_id = int(task)
        docs = DocsModel.query.filter(DocsModel.task_id == task_id).all()
        print docs
        tag_type_id = TasksModel.query.filter(
            TasksModel.id == task_id).first().tag_type_id
        push_file_message(doc_list=docs, tag_type_id=tag_type_id, pre_tag=False)
        print 'repush task {} successed'.format(task_id)
