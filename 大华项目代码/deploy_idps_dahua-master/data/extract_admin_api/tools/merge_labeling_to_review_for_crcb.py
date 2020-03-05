# coding=utf-8
# email:  younixiao@qq.com
# create: 2018年11月28日星期三 18:24

from os import path as os_path
import sys
import json

reload(sys)
sys.path.append(os_path.join(os_path.dirname(__file__), os_path.pardir, 'api'))
from app import session
from shared_orm.models.review_abstract_model import ReviewAbstractModel
from shared_orm.models.labeling_item_model import LabelingItemModel
from app.resources.reviewsenior.review_common import TagsModelUtil

tags_query_list = TagsModelUtil.all_enable_tags()
tag_id_to_name_dict = {
    int(tags_query.id): tags_query.name
    for tags_query in tags_query_list
}

tag_id_to_type_dict = {
    int(tags_query.id): tags_query.data_type
    for tags_query in tags_query_list
    if tags_query not in ('', None)
}


def get_label_items(ids):
    return LabelingItemModel.query.filter(
        LabelingItemModel.labeling_id.in_(ids)
    ).all()


def get_review(review_id):
    return ReviewAbstractModel.query.filter(ReviewAbstractModel.review_id == review_id).first()


def handle_(result):
    abstract_info_more = []
    for result_key in result:
        for index, tag in enumerate(result[result_key]):
            abstract_info_more.append(
                dict(
                    processing_result=tag[3],
                    tag_id=int(result_key) + 10000,
                    value=tag[0],
                    offset=tag[2],
                    tag_name=tag_id_to_name_dict.get(int(result_key)),
                    type=tag_id_to_type_dict.get(int(result_key), 'string')))
    return abstract_info_more


def merge_tags_from_label_item_models(label_item_models):
    extract_json = {}
    repeat_json = {}
    for label_item_model in label_item_models:
        if not label_item_model.status:
            continue
        word = label_item_model.word
        tag_id = str(label_item_model.tag_id)
        index = label_item_model.index
        if tag_id in repeat_json:
            if index not in repeat_json[tag_id]:
                repeat_json[tag_id][index] = [word]
            else:
                if word in repeat_json[tag_id][index]:
                    if 'word' == '张峰':
                        print repeat_json[tag_id][index]
                    continue
                else:
                    repeat_json[tag_id][index].append(word)
        else:
            repeat_json[tag_id] = {
                index: [word]
            }
        processing_result = None
        if label_item_model.extended:
            processing_result = label_item_model.extended
        extract_list = [word, 1, index, processing_result]
        if tag_id in extract_json:
            extract_json[tag_id].append(extract_list)
        else:
            extract_json[tag_id] = [extract_list]
    result = handle_(extract_json)
    return result


def migrate(item):
    review_id = item[0]
    labels = item[1]
    review_model = get_review(review_id)
    label_item_models = get_label_items(labels)
    tags = merge_tags_from_label_item_models(label_item_models)
    review_model.abstract_info_more = json.dumps(tags)
    try:
        session.commit()
        print 'review_id: {}'.format(review_id)
        # print 'data: {}'.format(json.dumps(tags, ensure_ascii=False))
        print 'success'
    except Exception as e:
        session.rollback()
        print '{} failed'.format(review_id)
        print e


if __name__ == "__main__":
    migrate_list = [
        [3, [647, 648, 646, 649]],
        [4, [642, 643, 644, 645]],
        [5, [663, 668, 658, 703]],
        [6, [696, 699, 701, 706]],
        [7, [736, 1284, 702, 1454]]
    ]
    for migrate_item in migrate_list:
        migrate(migrate_item)
