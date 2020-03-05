# coding=utf-8
# email:  younixiao@qq.com
# create: 2018年11月16日星期五 16:00


from os import path as os_path
import sys
reload(sys)
sys.path.append(os_path.join(os_path.dirname(__file__), os_path.pardir, 'api'))
from app import session
from shared_orm.models.tags_model import TagsModel


def marge_tag(tag_type_id):
    tags = TagsModel.query.all()
    for tag in tags:
        new_tag = TagsModel(
            tag_type_id=tag_type_id,
            name=tag.name,
            index=tag.index,
            color=tag.color,
            desc=tag.desc,
            data_type=tag.data_type,
            extended=tag.extended,
            status=tag.status,
        )
        new_tag.id = int(tag.id) + 10000
        session.add(new_tag)
    session.commit()


if __name__ == "__main__":
    new_type_id = sys.argv[1]
    print new_type_id
    if not new_type_id:
        'new_type_id is required'
        exit()
    marge_tag(new_type_id)

