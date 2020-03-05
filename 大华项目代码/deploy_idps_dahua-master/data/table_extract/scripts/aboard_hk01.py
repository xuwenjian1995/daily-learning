#!/usr/bin/env python
# coding=utf-8
# author:chenxianglong@datagrand.com
# datetime:2019/12/16 19:07
# 抽取HK01模板内容
from pdf2txt_decoder.pdf2txt_decoder import Pdf2TxtDecoder
from .field_conf import aboard_hk01
from document_beans.table import Table
import json

is_debug = 1
is_from_check = False


def debug_save_file(context):
    if is_debug:
        file_path = r"./tmp.json"
        with open(file_path, "w") as fw:
            fw.write(json.dumps(context))


def debug_load_file():
    if is_debug:
        file_path = "/tmp/3.json"
        with open(file_path, "r") as fr:
            return json.loads(fr.read())


def get_debug_logger():
    import logging
    logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    return logger


try:
    from ..driver import logger_online as logger
except:
    logger = get_debug_logger()


# 更新cell中context内容（前端显示问题修复）
def get_cell_context_list(cell):
    context_list = list()
    if not cell or not cell.mapper:
        return context_list
    last_idx, last_offset = 0, cell.mapper[0]

    for idx, offset in enumerate(cell.mapper):
        # last one
        if idx == len(cell.mapper) - 1:
            context_list.append([
                cell.text[last_idx:],
                1,
                cell.mapper[last_idx]
            ])
        elif idx == 0:
            continue

        if offset != last_offset + 1:
            context_list.append([
                cell.text[last_idx:idx],
                1,
                cell.mapper[last_idx]
            ])
            last_idx, last_offset = idx, offset
        else:
            last_offset = offset

    return context_list


# 更新抽取内容
def update_extractor_result(result, key, cell, group_key=-1):
    if not cell or not cell.mapper:
        return
    tag_info = aboard_hk01.get(key)
    # {"entityName":(1,"entityName")}
    assert (tag_info != None)
    tagid = tag_info[0]
    tag_name = tag_info[1]
    if tagid not in result:
        result[tagid] = list()

    if is_from_check:
        result[tagid].append([
            cell.text,
            1,
            get_cell_context_list(cell),  # 用于审核显示（修复前端显示问题）替换原有offset
            tag_name,
            group_key,  # 分组group_key
        ])
    else:
        # result[tagid].append([
        #     cell.text,
        #     1,
        #     cell.mapper[0]
        # ])
        result[tagid].extend(get_cell_context_list(cell))


def text_in_cell(comp_text, cell_text):
    """
    判断传入的文字是不是在表格中的text中
    :param comp_text: 待检测的
    :param cell_text: 表格的文本
    :return:
    """
    return comp_text in cell_text


def text_with_colon_in_cell(comp_text, cell_text):
    return comp_text in cell_text.split(':')[0]


def cell_text_not_empty(comp_text, cell_text):
    """
    直接返回表格的文本数据
    :param comp_text:
    :param cell_text:
    :return:
    """
    return cell_text


def text_with_full_text(comp_text, cell_text):
    return comp_text.strip().replace(" ", "") in cell_text.strip().replace(" ", "")


def text_all_match(comp_text, cell_text):
    return comp_text == cell_text


def text_all_match_ingore_case(comp_text, cell_text):
    return comp_text.lower() == cell_text.lower()


def text_first_word_in(comp_text, cell_text):
    first_word = comp_text.split(' ')[0]
    return first_word in cell_text


def get_next_cell(table, comp_text="", row_idx=None, col_idx=None, next_type="right",
                  cmp_func=text_in_cell, satisfy_idx=0, right_nonempty_max_idx=None):
    '''
    :param row_idx: 行idx 如果只传row_idx的话，则选择该行
    :param col_idx: 列lix 如果只传col_idx的话，则选择该列
    :param comp_text: 需要与单元格中文本比对的方法
    :param next_type: 返回下一格cell的类型，right：右一，down：下一，self：当前单元格
    :param cmp_func: 比较comp_text与cell_text函数
    :param satisfy_idx: 满足情况的第x个
    :param right_nonempty_max_idx: 如果next_type为right，则返回右方第1到第right_nonempty_max_idx个非空的值
    :return: 下一个cell
    '''

    if row_idx is None and col_idx is None:
        for row_id, row_list in enumerate(table.cells):
            for col_id, cell in enumerate(row_list):
                if cell and cmp_func(comp_text, cell.text):
                    satisfy_idx -= 1
                    if satisfy_idx < 0:
                        row_idx = row_id
                        col_idx = col_id
                        break

    elif col_idx is None:
        """
        如果列号为空的时候，长处理行
        """
        row_list = table.cells[row_idx] if row_idx < len(table.cells) else list()
        for col_id, cell in enumerate(row_list):
            if cell and cmp_func(comp_text, cell.text):
                satisfy_idx -= 1
                if satisfy_idx < 0:
                    col_idx = col_id
                    break

    elif row_idx is None:
        col_list = [each[col_idx] for each in table.cells if col_idx < len(each)]
        for row_id, cell in enumerate(col_list):
            if cell and cmp_func(comp_text, cell.text):
                satisfy_idx -= 1
                if satisfy_idx < 0:
                    row_idx = row_id
                    break

    if row_idx is None or col_idx is None or row_idx >= len(table.cells) or col_idx >= len(table.cells[row_idx]):
        logger.warning("search failed, comp_text: {}".format(comp_text))
        return (None, None, None)

    if next_type == "right":
        # 如果next_type为right，则返回右方第1到第right_nonempty_max_idx个非空的值
        # 为了解决居中对齐，左对齐，右对齐等生成表格格式不一致的情况
        col_idx += 1
        if right_nonempty_max_idx:
            for idx, cell in enumerate(table.cells[row_idx][col_idx:right_nonempty_max_idx + 1]):
                if cell and cell.text:
                    col_idx += idx
                    break

    elif next_type == "left":
        col_idx -= 1

    elif next_type == "down":
        row_idx += 1

    elif next_type == "up":
        row_idx -= 1

    else:
        pass

    if row_idx >= len(table.cells) or col_idx >= len(table.cells[row_idx]):
        logger.warning("search failed, index_out_of_range, comp_text: {}".format(comp_text))
        return (None, None, None)

    logger.info("search succ, comp_text: {0}, cell_text: {1}".format(comp_text, table.cells[row_idx][col_idx].text))

    return (table.cells[row_idx][col_idx], row_idx, col_idx)


def extract_all_tag(table):
    extract_result = dict()
    # entityName
    cell, _, _ = get_next_cell(table, row_idx=0, cmp_func=cell_text_not_empty, next_type="self")
    if cell:
        update_extractor_result(extract_result, "entityName", cell)
    # entityAddress
    cell, _, _ = get_next_cell(table, row_idx=1, cmp_func=cell_text_not_empty, next_type="self")
    if cell:
        update_extractor_result(extract_result, "entityAddress", cell)

    # 从To:行计算为起始行，针对ocr识别表格不把前3行内容当做表格时的处理
    cell, table_start_row, _ = get_next_cell(table, comp_text="To", col_idx=0, cmp_func=text_with_colon_in_cell)
    if not cell:
        table_start_row = 0

    # customerName
    cell, _, _ = get_next_cell(table, comp_text="Buyer Name", row_idx=table_start_row, cmp_func=text_with_colon_in_cell,
                               right_nonempty_max_idx=3)
    if cell:
        update_extractor_result(extract_result, "customerName", cell)
    else:
        cell, _, _ = get_next_cell(table, comp_text="To", row_idx=table_start_row, cmp_func=text_with_colon_in_cell,
                                   right_nonempty_max_idx=3)
        if cell:
            update_extractor_result(extract_result, "customerName", cell)
    # agreementNum
    cell, _, _ = get_next_cell(table, comp_text="No", row_idx=table_start_row, cmp_func=text_with_colon_in_cell,
                               right_nonempty_max_idx=100)
    if cell:
        update_extractor_result(extract_result, "agreementNum", cell)
    # customerRegAddr
    cell, _, _ = get_next_cell(table, comp_text="Buyer Address", row_idx=table_start_row + 1,
                               cmp_func=text_with_colon_in_cell,
                               right_nonempty_max_idx=3)
    if cell:
        update_extractor_result(extract_result, "customerRegAddr", cell)
    else:
        cell, _, _ = get_next_cell(table, comp_text="Add", row_idx=table_start_row + 1,
                                   cmp_func=text_with_colon_in_cell,
                                   right_nonempty_max_idx=3)
        if cell:
            update_extractor_result(extract_result, "customerRegAddr", cell)
    # purchaserPO
    cell, _, _ = get_next_cell(table, comp_text="Customer PO", row_idx=table_start_row + 1, cmp_func=text_first_word_in,
                               right_nonempty_max_idx=100)
    if cell:
        update_extractor_result(extract_result, "purchaserPO", cell)
    # signDate
    cell, _, _ = get_next_cell(table, comp_text="Date", row_idx=table_start_row + 2, cmp_func=text_with_colon_in_cell,
                               right_nonempty_max_idx=3)
    if cell:
        update_extractor_result(extract_result, "signDate", cell)
    # masterAgreement
    cell, _, _ = get_next_cell(table, comp_text="Master", row_idx=table_start_row + 2, cmp_func=text_first_word_in,
                               right_nonempty_max_idx=100)
    if cell:
        update_extractor_result(extract_result, "masterAgreement", cell)
    # agreementRemarks  #todo 去掉Remark:前缀
    cell, _, _ = get_next_cell(table, comp_text="Remark", row_idx=table_start_row + 3, cmp_func=text_with_colon_in_cell,
                               next_type="self")
    if cell:
        update_extractor_result(extract_result, "agreementRemarks", cell)
        _, _, col_idx = get_next_cell(table, comp_text="Amount", row_idx=table_start_row + 4, next_type="self")
    else:
        _, _, col_idx = get_next_cell(table, comp_text="Amount", row_idx=table_start_row + 3, next_type="self")
    # discount

    _, row_idx, _ = get_next_cell(table, comp_text="Discount", col_idx=5, next_type="self")
    if col_idx and row_idx:
        update_extractor_result(extract_result, "discount", table.cells[row_idx][col_idx])
    # voucherDiscount
    _, row_idx, _ = get_next_cell(table, comp_text="Voucher", col_idx=5, next_type="self")
    if col_idx and row_idx:
        update_extractor_result(extract_result, "voucherDiscount", table.cells[row_idx][col_idx])
    # totalAmount
    _, row_idx, _ = get_next_cell(table, comp_text="Amount", col_idx=5, next_type="self")
    if col_idx and row_idx:
        update_extractor_result(extract_result, "totalAmount", table.cells[row_idx][col_idx])
    else:
        # 使用TOTAL字段来抽取totalAmount
        cell, _, _ = get_next_cell(table, comp_text="TOTAL", cmp_func=text_all_match_ingore_case,
                                   right_nonempty_max_idx=100)
        if cell:
            update_extractor_result(extract_result, "totalAmount", cell)

    # amountExclTax
    _, row_idx, _ = get_next_cell(table, comp_text="excl. Tax", col_idx=5, next_type="self")
    if col_idx and row_idx:
        update_extractor_result(extract_result, "amountExclTax", table.cells[row_idx][col_idx])
    # vat
    _, row_idx, _ = get_next_cell(table, comp_text="VAT", col_idx=5, next_type="self")
    if col_idx and row_idx:
        update_extractor_result(extract_result, "vat", table.cells[row_idx][col_idx])
    # amountInclTax
    _, row_idx, _ = get_next_cell(table, comp_text="incl.Tax", col_idx=5, next_type="self")
    if col_idx and row_idx:
        update_extractor_result(extract_result, "amountInclTax", table.cells[row_idx][col_idx])
    # tradeMethod and ...
    decl_list = [
        ("Terms of Trade", "tradeMethod", text_first_word_in),
        ("Payment Terms", "paymentTerms", text_first_word_in),
        ("Consignee", "consignee", text_with_colon_in_cell),
        ("Shipping address", "shippingAddress", text_first_word_in),
        ("Tax", "Tax", text_in_cell),
        ("Warranty", "Warranty", text_with_colon_in_cell),
        ("Claim", "Claim", text_with_colon_in_cell),
        ("Export Comp", "Export_Compliance", text_with_full_text),
        ("Force Maj", "Force_Majeure", text_with_full_text),
        ("Applicable Laws And Arbitration", "Applicable_Laws_And_Arbitration", text_first_word_in),
        ("Special Conditions", "Special_Conditions", text_first_word_in),
        ("Counterparts", "Counterparts", text_with_full_text),
        ("Export Clear", "Export_Clearance", text_with_full_text)
    ]
    for decl in decl_list:
        cell, _, _ = get_next_cell(table, comp_text=decl[0], col_idx=1, cmp_func=decl[2], next_type="right")
        if cell:
            update_extractor_result(extract_result, decl[1], cell)

    # buyerLTD
    cell, row_idx, _ = get_next_cell(table, comp_text="The Buyer", col_idx=1, cmp_func=text_in_cell)
    if cell:
        update_extractor_result(extract_result, "buyerLTD", cell)
        # sellerLTD
        cell, _, _ = get_next_cell(table, comp_text="The Seller", row_idx=row_idx, cmp_func=text_in_cell)
        if cell:
            update_extractor_result(extract_result, "sellerLTD", cell)

    # item数据字段
    # 下面抽取remark中的数据

    item_property_list = [
        (0, "item_lineNumber"),
        (1, "item_enuPingName"),
        (2, "item_innerModel"),
        (3, "item_outerModel"),
        (4, "item_quantity"),
        # 以下数据的col_idx需要计算后更新
        # (5, "item_unitPrice"),
        # (6, "item_unitPriceDiscountExclKey"),
        # (7, "item_amountExclTax"),
        # (8, "item_promotionFlag"),
    ]
    # item和Nos抽取
    _, row_idx, _ = get_next_cell(table, comp_text="Item", col_idx=0, next_type="self")
    if not row_idx:
        _, row_idx, _ = get_next_cell(table, comp_text="ltem", col_idx=0, next_type="self")

    _, nos_row_idx, _ = get_next_cell(table, comp_text="Nos", col_idx=0, next_type="self")

    is_cross_line = False
    if nos_row_idx and row_idx and nos_row_idx == row_idx + 1:
        is_cross_line = True

    if row_idx:
        # unitPriceKey
        cell, _, col_idx = get_next_cell(table, comp_text="Unit Price", row_idx=row_idx, next_type="self")
        if cell:
            # 表格数据中对应的列
            item_property_list.append((col_idx, "item_unitPrice"))
            update_extractor_result(extract_result, "unitPriceKey", cell)
        # unitPriceDiscountExclKey
        cell, _, col_idx = get_next_cell(table, comp_text="Unit Price", row_idx=row_idx, next_type="self",
                                         satisfy_idx=1)
        if cell:
            # 表格数据中对应的列
            item_property_list.append((col_idx, "item_unitPriceDiscountExclKey"))
            update_extractor_result(extract_result, "unitPriceDiscountExclKey", cell)
            # 可能会有下一行信息
            cell, _, _ = get_next_cell(table, col_idx=col_idx, row_idx=row_idx, next_type="down")
            if cell and ("discount" in cell.text or "excl. Tax" in cell.text):
                update_extractor_result(extract_result, "unitPriceDiscountExclKey", cell)
                is_cross_line = True
        # amountKey
        cell, _, col_idx = get_next_cell(table, comp_text="Amount", row_idx=row_idx, next_type="self")
        if cell:
            # 表格数据中对应的列
            item_property_list.append((col_idx, "item_amountExclTax"))
            item_property_list.append((col_idx + 1, "item_promotionFlag"))
            update_extractor_result(extract_result, "amountKey", cell)
            # 可能会有下一行信息
            cell, _, _ = get_next_cell(table, col_idx=col_idx, row_idx=row_idx, next_type="down")
            if cell and ("discount" in cell.text or "excl. Tax" in cell.text):
                update_extractor_result(extract_result, "unitPriceDiscountExclKey", cell)
                is_cross_line = True

        # 每一行数据
        if is_cross_line:
            row_idx += 2
        else:
            row_idx += 1
        while row_idx < len(table.cells):
            cell = table.cells[row_idx][0]
            if not (cell and cell.text):
                break
            for col_idx, prop_name in item_property_list:
                if row_idx < len(table.cells) and col_idx < len(table.cells[row_idx]):
                    cell = table.cells[row_idx][col_idx]
                    if cell and cell.text:
                        update_extractor_result(extract_result, prop_name, cell, group_key=row_idx)
            row_idx += 1
    return extract_result


# 只是合并了cells
def merge_tables(table_data_list):
    assert len(table_data_list) > 0
    table = table_data_list[0]
    for idx in range(1, len(table_data_list)):
        table.cells.extend(table_data_list[idx].cells)

    # 填充空值多余的空值
    max_length = max([len(each) for each in table.cells])
    for each_row in table.cells:
        if len(each_row) < max_length:
            each_row.extend([None] * (max_length - len(each_row)))

    return table


def run(context):
    logger.info("is_from_check: %s" % is_from_check)
    if not is_from_check and context["doctype"] not in ["33"]:
        return None
    # debug_save_file(context)
    pdf2txt_decoder = context['pdf2txt_decoder']
    meta_data_list = pdf2txt_decoder.get_meta_data_list()
    table_data_list = [each for each in meta_data_list if isinstance(each, Table)]
    if len(table_data_list) == 0:
        logger.info("未识别到表格，异常退回")
        return
    total_table = merge_tables(table_data_list)
    extract_result = extract_all_tag(total_table)
    context.update({"result": extract_result})
    return extract_result


if __name__ == "__main__":
    rich_content = debug_load_file()
    pdf2txt_decoder = Pdf2TxtDecoder(rich_content)
    content = {"pdf2txt_decoder": pdf2txt_decoder, "result": {}}
    run(content)
