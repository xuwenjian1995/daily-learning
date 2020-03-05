# coding=utf-8
# email:  younixiao@qq.com
# create: 2018年12月11日星期二 14:39

import json
import os
from os import path as os_path
import sys
import datetime
from sqlalchemy.ext.declarative import DeclarativeMeta

reload(sys)
sys.path.append(os_path.join(os_path.dirname(__file__), os_path.pardir, 'api'))

SAVE_DIR = 'backup'


class AlchemyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [
                x for x in dir(obj)
                if not x.startswith('_') and x != 'metadata'
            ]:
                data = obj.__getattribute__(field)
                if isinstance(data, datetime.datetime):
                    fields[field] = str(data)
                else:
                    try:
                        # this will fail on non-encodable values, like other classes
                        json.dumps(
                            data
                        )
                        fields[field] = data
                    except TypeError:
                        fields[field] = None
            return fields

        return json.JSONEncoder.default(self, obj)


def get_model_dicts(models):
    table = models[0].__tablename__
    model_dicts = []
    for model in models:
        model_dicts.append(
            json.dumps(model, cls=AlchemyEncoder, ensure_ascii=False))
    with open(os.path.join(SAVE_DIR, table), 'w') as save_file:
        save_file.write(json.dumps(model_dicts, ensure_ascii=False))
    print '{} data saved'.format(table)


if __name__ == '__main__':
    from app import flask_app, logger
    from shared_orm.models.tag_type_model import TagTypeModel
    from shared_orm.models.tags_model import TagsModel
    from shared_orm.models.tasks_model import TasksModel
    from shared_orm.models.docs_model import DocsModel
    from shared_orm.models.labeling_item_model import LabelingItemModel
    from shared_orm.models.labeling_model import LabelingModel

    for orm in (DocsModel, LabelingModel, TagsModel, TagTypeModel, TasksModel, LabelingItemModel):
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)

        get_model_dicts(orm.query.all())
