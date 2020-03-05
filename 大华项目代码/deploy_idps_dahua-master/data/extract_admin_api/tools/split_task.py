# coding=utf-8
# email:  younixiao@qq.com
# create: 2018年11月22日星期四 20:14
from os import path as os_path
from app import session
from shared_orm.models.labeling_model import LabelingModel
from shared_orm.models.docs_model import DocsModel
from shared_orm.models.tasks_model import TasksModel
from shared_orm.models.labeling_item_model import LabelingItemModel


tag_type_id = 1
train_list = [1]

doc_count = 0
task_count = 0

task_models = []

for train_id in train_list:
    if doc_count > 200:
        doc_count = 0
    if doc_count == 0:
        task_count = task_count + 1
        new_task = TasksModel(
            tag_type_id=tag_type_id,
            task_name='train_{}'.format(task_count),
            creator_id=1,
            task_type=5,
            extended='',
            desc='',
            status=1,
            project_id=1)
        session.add(new_task)
        session.commit()
        task_models.append(new_task)

    task_id = task_models[-1].id
    old_doc =  DocsModel.query.filter(DocsModel.id == train_id).first()
    if not old_doc:
        continue
    new_doc = DocsModel(
        task_id=task_id,
        unique_name=old_doc.unique_name,
        content=old_doc.content,
        content_wrap=old_doc.content_wrap,
        pre_tag=old_doc.pre_tag,
        name=old_doc.name,
        extended=train_id, 
        status=5
    )

    session.add(new_doc)
    session.commit()

    new_label = LabelingModel(
        doc_id=new_doc.id,
        task_id=task_id,
        operator_id=1,
        assessor_id=0,
        status=1,
        extended='',
    )
    session.add(new_label)
    session.commit()
    print 'new_label_id: {}'.format(new_label.id)

    old_label = LabelingModel.query.filter(
        LabelingModel.doc_id == train_id).first()

    if not old_label:
        continue

    old_labeling_items = LabelingItemModel.query.filter(
        LabelingItemModel.labeling_id == old_label.id).all()
    for old_label_item in old_labeling_items:
        session.add(
            LabelingItemModel(
                labeling_id=new_label.id,
                tag_id=old_label_item.tag_id,
                word=old_label_item.word,
                index=old_label_item.index,
            ))
    session.commit()