#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Yang Huiyu
# @Date  : 2019/2/18

import math
import copy
from functools import partial
import numpy as np
from ...beans.line import Line
from ...common import util
from ...common.driver import server_logger as logger

IS_TABLE = True
BLANK_RATIO = 0.3
MIN_BLANK_WIDTH = 5


def find_lines(page):
    tmp_tables = page.get_tables()
    wrong_tables = []
    for i, table in enumerate(tmp_tables):
        # debug for table area detection
        table_location = {
            'left': int(math.floor(table.x)),
            'top': int(math.floor(table.y)),
            'right': int(math.ceil(table.x + table.width)),
            'bottom': int(math.ceil(table.y + table.height))
        }
        # line_top = Line(table_left, table_top, table_right, table_top)
        # line_bottom = Line(table_left, table_bottom, table_right, table_bottom)
        # line_left = Line(table_left, table_top, table_left, table_bottom)
        # line_right = Line(table_right, table_top, table_right, table_bottom)
        # scale = page.get_page_info().pic_scale
        # map(partial(util.anti_scale_line, scale=scale), [line_top, line_bottom])
        # util.draw_lines([line_top, line_bottom, line_left, line_right], original_image, 'debug_table_area.jpg')
        ######################
        fill_lines(table, table_location)
        if not IS_TABLE:
            wrong_tables.append(table)
        for t in wrong_tables:
            tmp_tables.remove(t)


def fill_internal_lines(table, table_location, blanks_x, blanks_y):
    if len(blanks_x) > 2 and len(blanks_y) > 2:
        _find_internal_vertical_lines(table, blanks_x, table_location)
        _find_internal_horizontal_lines(table, blanks_y, table_location)
    else:
        logger.warning('Detect too few blanks. Probably not a table')
        IS_TABLE = False

def fill_border_lines(table, table_location, blanks_x, blanks_y):
    _find_left_vertical_border(table, blanks_x, table_location)
    _find_right_vertical_border(table, blanks_x, table_location)
    _find_top_horizontal_border(table, blanks_y, table_location)
    _find_bottom_horizontal_border(table, blanks_y, table_location)


def fill_lines(table, table_location):
    filtered_chars = _filter_empty_chars(table.get_chunks())
    histogram_y_axis = _histogram_chars_y(filtered_chars, table_location['top'], table_location['bottom'])
    histogram_x_axis = _histogram_chars_x(filtered_chars, table_location['left'], table_location['right'])
    blanks_y = _find_blanks(histogram_y_axis, table_location['top'])
    blanks_x = _find_blanks(histogram_x_axis, table_location['left'])
    if blanks_x and blanks_y:
        fill_border_lines(table, table_location, blanks_x, blanks_y)
        fill_internal_lines(table, table_location, blanks_x, blanks_y)


def _filter_empty_chars(chars):
    """
    This function is used to filter chars with none text
    :param chars:
    :return: without_blank
    """
    return [char for char in chars if char.str != u" "]


def _histogram_chars_x(chars, table_left, table_right):
    """
    统计chars在x轴的直方图
    :param chars:
    :return:
    """
    histogram_x = np.zeros(table_right - table_left)
    for c in chars:
        # node坐标修改后要同步修改
        x1 = int(math.ceil(c.x))
        x2 = int(math.floor(x1 + c.width))
        projections = np.zeros(table_right - table_left)
        try:
            projections = np.concatenate(
                (np.zeros(x1 - table_left), np.ones(x2 - x1), np.zeros(table_right - x2)), axis=None)
        except ValueError:
            logger.error('char {} out of table'.format(c.str))
        histogram_x = histogram_x + projections
    return histogram_x


def _histogram_chars_y(chars, table_top, table_bottom):
    """
    统计chars在y轴的直方图
    :param chars:
    :return:
    """
    histogram_y = np.zeros(table_bottom - table_top)
    for c in chars:
        # node坐标修改后要同步修改
        y2 = int(math.ceil(c.y))
        y1 = int(y2 - math.floor(c.height))
        projections = np.zeros(table_bottom - table_top)
        try:
            projections = np.concatenate(
                (np.zeros(y1 - table_top), np.ones(y2 - y1), np.zeros(table_bottom - y2)), axis=None)
        except ValueError:
            logger.error('char {} out of table'.format(c.str))
        histogram_y = histogram_y + projections
    return histogram_y


def _find_blanks(histogram, start):
    """
    找到表格内疑似表格线的区域
    :param histogram:
    :param start: 表格的最左边或最上边
    :return:
    """
    max_chars_value = np.max(histogram)
    if max_chars_value == 0:
        logger.warning('no chars in the table! Probably not a table')
        IS_TABLE = False
        return None
    # filtered_histogram = np.where(histogram < BLANK_RATIO * max_chars_value, 0, histogram)
    histogram_lst = histogram.tolist()
    blanks = []
    blank = []
    for index, histogram_value in enumerate(histogram_lst):
        if index >= 0 and histogram_value == 0:
            blank.append(index + start)
        elif histogram_value > 0 and index > 0 and histogram_lst[index - 1] == 0:
            blanks.append(blank)
            blank = []
        if index == len(histogram_lst)-1 and histogram_value == 0:
            blanks.append(blank)
    return [b for b in blanks if len(b) >= MIN_BLANK_WIDTH]


def _find_internal_vertical_lines(table, blanks_x, table_location):
    internal_vertical_lines = []
    for blank in blanks_x[1: -1]:
        existing_vil = check_existing_lines(table, blank[0], blank[-1], direction='vertical')
        if len(existing_vil) >= 1:
            logger.info('internal lines existing')
        else:
            il_x = blank[len(blank)/2]
            internal_line = Line(il_x, table_location['top'], il_x, table_location['bottom'], direction='vertical')
            logger.info('adding internal vertical line')
            internal_vertical_lines.append(internal_line)
    table.set_lines(table.get_lines().extend(internal_vertical_lines))


def _find_internal_horizontal_lines(table, blanks_y, table_location):
    internal_horizontal_lines = []
    for blank in blanks_y[1: -1]:
        existing_vil = check_existing_lines(table, blank[0], blank[-1], direction='horizontal')
        if len(existing_vil) >= 1:
            logger.info('internal lines existing')
        else:
            il_y = blank[len(blank) / 2]
            internal_line = Line(table_location['left'], il_y, table_location['right'], il_y, direction='horizontal')
            logger.info('adding internal horizontal line')
            internal_horizontal_lines.append(internal_line)
    table.set_lines(table.get_lines().extend(internal_horizontal_lines))


def _find_left_vertical_border(table, blanks, table_location):
    left_blank = blanks[0]
    existing_lvb_lines = check_existing_lines(table, left_blank[0], left_blank[-1], direction='vertical')
    if len(existing_lvb_lines) >= 1:
        logger.info('left vertical border existing')
    else:
        lvb_x = table_location['left']
        lvb = Line(lvb_x, table_location['top'], lvb_x, table_location['bottom'], direction='vertical')
        logger.info('adding left vertical border')
        table.set_lines(table.get_lines().append(lvb))


def _find_right_vertical_border(table, blanks, table_location):
    right_blank = blanks[-1]
    existing_lvb_lines = check_existing_lines(table, right_blank[0], right_blank[-1], direction='vertical')
    if len(existing_lvb_lines) >= 1:
        logger.info('right vertical border existing')
    else:
        rvb_x = table_location['right']
        rvb = Line(rvb_x, table_location['top'], rvb_x, table_location['bottom'], direction='vertical')
        logger.info('adding right vertical border')
        table.set_lines(table.get_lines().append(rvb))


def _find_top_horizontal_border(table, blanks, table_location):
    top_blank = blanks[0]
    existing_thb_lines = check_existing_lines(table, top_blank[0], top_blank[-1], direction='horizontal')
    if len(existing_thb_lines) >= 1:
        logger.info('top horizontal border existing')
    else:
        thb_y = table_location['top']
        thb = Line(table_location['left'], thb_y, table_location['right'], thb_y, direction='horizontal')
        logger.info('add top horizontal border')
        table.set_lines(table.get_lines().append(thb))


def _find_bottom_horizontal_border(table, blanks, table_location):
    bottom_blank = blanks[-1]
    existing_bhb_lines = check_existing_lines(table, bottom_blank[0], bottom_blank[-1], direction='horizontal')
    if len(existing_bhb_lines) >= 1:
        logger.info('bottom horizontal border existing')
    else:
        bhb_y = table_location['bottom']
        bhb = Line(table_location['left'], bhb_y, table_location['right'], bhb_y, direction='horizontal')
        logger.info('add bottom horizontal border')
        table.set_lines(table.get_lines().append(bhb))


def check_existing_lines(table, start, end, direction='horizontal'):
    if direction == 'horizontal':
        table_hozizontal_lines = table.get_horizontal_lines()
        range_lines = [l for l in table_hozizontal_lines if start <= l.y1 <= end]
        return range_lines
    if direction == 'vertical':
        table_vertical_lines = table.get_vertical_lines()
        range_lines = [l for l in table_vertical_lines if start <= l.x1 <= end]
        return range_lines
    logger.warning('line direction is must be horizontal or vertical')
    return []


# if __name__ == "__main__":
#     from src.beans.char import Char
#     from src.beans.line import Line
#     from src.common.driver import server_logger as logger
#     page_num = 1
#     index_in_page = 5
#     offset = 78
#     config1 = {'x': 10, 'y': 28, 'width': 4, 'height': 4}
#     config2 = {'x': 25, 'y': 28, 'width': 4, 'height': 4}
#     c1 = Char(config1, page_num, index_in_page, offset)
#     c2 = Char(config2, page_num, index_in_page, offset)
#     table_left = 2
#     table_right = 50
#     histogram_x = _histogram_chars_x([c1, c2], table_left, table_right)
#     print(histogram_x)
#     blanks = _find_blanks(histogram_x, table_left)
#     print(blanks)
