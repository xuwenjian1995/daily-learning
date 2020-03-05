# coding=utf-8
# email:  lihanqing@datagrand.com
# create: 2018/7/18-下午4:30
import sys,json

from ..common.util import dump_data
from ..driver import logger_processor as logger
reload(sys)
sys.setdefaultencoding('utf-8')
from ..driver import logger_processor as logger
from uuid import uuid4 as uuid
def get_uuid():
    return str(uuid()).replace("-","")

def write_out_file(rich_content, file_uuid):
    # 输出成文档供测试
    folder_path = "/root/contract_check_online/check/app/scripts/files/"
    # rich_content = data["rich_content"]
    # ------------------------
    # file_name = get_uuid()
    with open("{0}/{1}.json".format(folder_path, file_uuid), "w") as f:
        f.write(json.dumps(rich_content))
    logger.info("输出成文件:{0}".format(file_uuid))


def run(data):
    # save_file_name = 'file_1_data'
    # logger.info('start to dump data to file: {}'.format(save_file_name))
    # dump_data(data, save_file_name)
    rich_content = data["rich_content"]
    extra_conf = data.get('extra_conf', dict())
    file_uuid = extra_conf.get("file_uuid", get_uuid())
    write_out_file(rich_content, file_uuid)

    # entities = data["entities"]
    # for each in entities:
    #     logger.info(each)
    #     logger.info(each.get_id())
    #     logger.info(each.get_name())
    #     logger.info(each.get_value())
    #     logger.info(each.get_offset())
