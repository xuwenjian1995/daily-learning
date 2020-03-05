# coding=utf-8
# email:  lihanqing@datagrand.com
# create: 2019/2/21-9:33 PM
import sys
from math import ceil, floor

import requests

reload(sys)
sys.setdefaultencoding('utf-8')

from ...beans.rectangle import Rectangle
from ...beans.line import Line
from ...common.driver import processor_logger as logger
from ...common.util import scale_rectangle


def detect(page, **kwargs):
    params = kwargs.get('algo_params', {})
    average_row_height = kwargs.get('average_row_height', 20)
    img_file = kwargs.get('img_file', '')
    detector = AreaDetector(page, average_row_height, img_file, params)
    return detector.detect()


class AreaDetector(object):

    def __init__(self, page, average_row_height, img_file, params):
        self._page = page
        self._params = params
        self._img_file = img_file
        self._page_width = int(self._page.get_page_info().width)
        self._page_height = int(self._page.get_page_info().height)
        self._min_blank_width = params.get('min_blank_width', 0.5) * average_row_height
        self._min_table_width = params.get('_min_table_width', 0.1) * self._page_width
        self._min_table_height = params.get('_min_table_height', 0.1) * self._page_height
        self._min_table_top = params.get('_min_table_top', 0.1) * self._page_height
        self._max_table_bottom = params.get('_max_table_bottom', 0.9) * self._page_height
        self._max_x_blank_of_table_content = params.get('_max_x_blank_of_table_content', 0.5)
        self._max_y_blank_of_table_content = params.get('_max_y_blank_of_table_content', 0.5)
        self._get_overlap = lambda interval1, interval2: max(0, min(interval1[1], interval2[1]) - max(interval1[0],
                                                                                                      interval2[0]))

    def _post(self, img_file, ip, port, timeout):
        try:
            logger.info('start to use od to detect {}'.format(img_file))
            url = 'http://{}:{}/detect_by_file'.format(ip, port)
            files = {'img': open(img_file, 'rb')}
            response = requests.post(url, files=files, timeout=timeout)
            status_code = response.status_code
            assert status_code == 200, '{} failure, status code: {}'.format(img_file, status_code)
            return response.json()
        except Exception, e:
            logger.error('{} error'.format(img_file))
            logger.error(e.message)

    def detect(self):
        page_chunks =  self._page.get_chunks()
        od_areas = self._find_table_areas()
        valid_areas = self._filter_invalid_areas(od_areas, page_chunks)
        tuned_areas = []
        for v_area in valid_areas:
            area = v_area['rectangle']
            tuned_area = self._tune_area(area, page_chunks)
            v_area['rectangle'] = tuned_area
            tuned_areas.append(v_area)
        return tuned_areas

    def _find_table_areas(self):
        ip = self._params['ip']
        port = self._params['port']
        timeout = self._params['timeout']
        scale = self._params['scale']
        result = self._post(self._img_file, ip, port, timeout)
        areas = []
        for obj in result['obj']:
            type = obj['type']
            xmin, ymin, xmax, ymax = obj['area']
            rectangle = Rectangle(xmin, ymin, xmax - xmin, ymax - ymin)
            scale_rectangle(rectangle, scale)
            areas.append({'rectangle': rectangle, 'type': type})
        return areas

    def _filter_invalid_areas(self, od_areas, chunks):
        # 过滤掉无效表格区域，根据最小上边界，最大上边界，最小高度，最小宽度，--内部文本区域边界，--文本分布均匀度
        # 水平方向投影必须要有blank(即不止一列)，水平方向最宽的blank不能大于阈值，垂直方向最高的blank不能大于阈值
        refined_areas = []
        for od_area in od_areas:
            area = od_area['rectangle']
            if area.width < self._min_table_width or area.height < self._min_table_height:
                continue
            if area.y < self._min_table_top or area.y + area.height > self._max_table_bottom:
                continue
            x_blank_num, max_x_blank_width, y_blank_num, max_y_blank_height = self._get_x_y_blank_info_of_area(chunks,
                                                                                                               area)
            if x_blank_num > 0 and max_x_blank_width < self._max_x_blank_of_table_content * area.width:
                if y_blank_num > 0 and max_y_blank_height > self._max_y_blank_of_table_content * area.height:
                    continue
                refined_areas.append(od_area)
        return refined_areas

    def _tune_area(self, area, chunks):
        # 上下边框若压到文本，则判断是外扩还是收缩，根据所压文本的水平blanks数, blanks数据为0认为是压到了非表格区的文字
        # 调节上边框
        top_border_blank_num = self._get_blank_num_of_line_h(chunks, Line(area.x, area.y, area.x + area.width, area.y,
                                                                          'horizontal'))
        top_y = int(area.y)
        y_projections_of_chunks = []
        if top_border_blank_num >= 0:
            y_projections_of_chunks = self._get_sorted_y_projections_of_chunks(chunks, area.x, area.x + area.width)
            top_y = self._tune_top_border(top_y, top_border_blank_num, y_projections_of_chunks)

        # 调节下边框
        bottom_border_blank_num = self._get_blank_num_of_line_h(chunks,
                                                                Line(area.x, area.y + area.height, area.x + area.width,
                                                                     area.y + area.height,
                                                                     'horizontal'))
        bottom_y = int(area.y + area.height)
        if bottom_border_blank_num >= 0:
            if not y_projections_of_chunks:
                y_projections_of_chunks = self._get_sorted_y_projections_of_chunks(chunks, area.x, area.x + area.width)
            bottom_y = self._tune_bottom_border(bottom_y, bottom_border_blank_num, y_projections_of_chunks)

        # 左右边框若压到文本，则外扩
        # 调节左边框
        left_border_blank_num = self._get_blank_num_of_line_v(chunks,
                                                              Line(area.x, area.y, area.x, area.y + area.height,
                                                                   'vertical'))
        left_x = int(area.x)
        x_projections_of_chunks = []
        if left_border_blank_num >= 0:
            x_projections_of_chunks = self._get_sorted_x_projections_of_chunks(chunks, area.y, area.y + area.height)
            left_x = self._tune_left_border(left_x, x_projections_of_chunks)

        # 调节右边框
        right_border_blank_num = self._get_blank_num_of_line_v(chunks,
                                                               Line(area.x + area.width, area.y, area.x + area.width,
                                                                    area.y + area.height,
                                                                    'vertical'))
        right_x = int(area.x + area.width)
        if right_border_blank_num >= 0:
            if not x_projections_of_chunks:
                x_projections_of_chunks = self._get_sorted_x_projections_of_chunks(chunks, area.y, area.y + area.height)
            right_x = self._tune_right_border(right_x, x_projections_of_chunks)
        return Rectangle(left_x, top_y, right_x - left_x, bottom_y - top_y)

    def _projection_chunks_x_of_line_h(self, chunks, line_h):
        """
        将与水平线line_h重叠的chunks投影到x轴
        :param chunks, line_h:
        :return:
        """
        projections = set()
        for chunk in chunks:
            if chunk.y - chunk.height <= line_h.y1 <= chunk.y and self._get_overlap((chunk.x, chunk.x + chunk.width),
                                                                                    (line_h.x1, line_h.x2)):
                x1 = int(ceil(chunk.x))
                x2 = int(floor(chunk.x + chunk.width))
                projections = projections | set(range(x1, x2))  # 理论上应该是x2+1
        return projections

    def _projections_chunks_x_y_of_area(self, chunks, area):
        x_projections, y_projections = set(), set()
        for chunk in chunks:
            if area.x < chunk.x and chunk.x + chunk.width < area.x + area.width and area.y < chunk.y - chunk.height \
                    and chunk.y < area.y + area.height:
                x1 = int(ceil(chunk.x))
                x2 = int(floor(chunk.x + chunk.width))
                x_projections = x_projections | set(range(x1, x2))  # 理论上应该是x2+1
                y1 = int(ceil(chunk.y - chunk.height))
                y2 = int(floor(chunk.y))
                y_projections = y_projections | set(range(y1, y2))  # 理论上应该是x2+1
        return x_projections, y_projections

    def _projection_chunks_y_of_line_v(self, chunks, line_v):
        """
        将与垂直线line_v重叠的chunks投影到y轴
        :param chunks, line_v:
        :return:
        """
        projections = set()
        for chunk in chunks:
            if chunk.x <= line_v.x1 <= chunk.x + chunk.width and self._get_overlap((chunk.y - chunk.height, chunk.y),
                                                                                   (line_v.y1, line_v.y2)):
                y1 = int(ceil(chunk.y - chunk.height))
                y2 = int(floor(chunk.y))
                projections = projections | set(range(y1, y2))  # 理论上应该是x2+1
        return projections

    def _get_sorted_y_projections_of_chunks(self, chunks, x1, x2):
        projections = set()
        for chunk in chunks:
            if self._get_overlap((x1, x2), (chunk.x, chunk.x + chunk.width)):
                y1 = int(ceil(chunk.y - chunk.height))
                y2 = int(floor(chunk.y))
                projections = projections | set(range(y1, y2))  # 理论上应该是x2+1
        return sorted(list(projections))

    def _get_sorted_x_projections_of_chunks(self, chunks, y1, y2):
        projections = set()
        for chunk in chunks:
            if self._get_overlap((y1, y2), (chunk.y - chunk.height, chunk.y)):
                x1 = int(ceil(chunk.x))
                x2 = int(floor(chunk.x + chunk.width))
                projections = projections | set(range(x1, x2))  # 理论上应该是x2+1
        return sorted(list(projections))

    def _get_blank_num_of_line_h(self, chunks, line_h):
        projections = self._projection_chunks_x_of_line_h(chunks, line_h)
        if not projections:
            return -1
        blank_num, _ = self._get_blank_info_of_projections(projections)
        return blank_num

    def _get_blank_num_of_line_v(self, chunks, line_v):
        projections = self._projection_chunks_y_of_line_v(chunks, line_v)
        if not projections:
            return -1
        blank_num, _ = self._get_blank_info_of_projections(projections)
        return blank_num

    def _get_x_y_blank_info_of_area(self, chunks, area):
        x_projections, y_projections = self._projections_chunks_x_y_of_area(chunks, area)
        if not x_projections:
            x_blank_num, max_x_blank_width = -1, -1
        else:
            x_blank_num, max_x_blank_width = self._get_blank_info_of_projections(x_projections)
        if not y_projections:
            y_blank_num, max_y_blank_height = -1, -1
        else:
            y_blank_num, max_y_blank_height = self._get_blank_info_of_projections(y_projections)
        return x_blank_num, max_x_blank_width, y_blank_num, max_y_blank_height

    def _get_blank_info_of_projections(self, projections):
        low, high = min(projections), max(projections)
        blanks = set(range(low, high + 1)) - projections
        if not blanks:
            return 0, 0
        sorted_blanks = sorted(list(blanks))
        blank_num = 0
        begin, last = sorted_blanks[0], sorted_blanks[0]
        max_blank_width = 0
        for pixel in sorted_blanks[1:]:
            if pixel - last == 1:
                last = pixel
            else:
                if last - begin > self._min_blank_width:  # 空白大于最小宽度
                    max_blank_width = max(max_blank_width, last - begin)
                    blank_num += 1
                begin, last = pixel, pixel
        if last - begin > self._min_blank_width:  # 空白大于最小宽度
            max_blank_width = max(max_blank_width, last - begin)
            blank_num += 1
        return blank_num, max_blank_width

    def _tune_top_border(self, top_y, top_border_blank_num, y_projections_of_chunks):
        hit = False
        last_y = 0
        new_top_y = top_y
        if top_border_blank_num > 0:
            for y in y_projections_of_chunks[::-1]:
                if hit:
                    if y == last_y - 1:
                        last_y = y
                    else:
                        new_top_y = y
                        break
                else:
                    if y == top_y:
                        hit = True
                        last_y = y
        else:
            for y in y_projections_of_chunks:
                if hit:
                    if y == last_y + 1:
                        last_y = y
                    else:
                        new_top_y = y
                        break
                else:
                    if y == top_y:
                        hit = True
                        last_y = y
        return new_top_y

    def _tune_bottom_border(self, bottom_y, bottom_border_blank_num, y_projections_of_chunks):
        hit = False
        last_y = 0
        new_bottom_y = bottom_y
        if bottom_border_blank_num > 0:
            for y in y_projections_of_chunks:
                if hit:
                    if y == last_y + 1:
                        last_y = y
                    else:
                        new_bottom_y = y
                        break
                else:
                    if y == bottom_y:
                        hit = True
                        last_y = y
        else:
            for y in y_projections_of_chunks[::-1]:
                if hit:
                    if y == last_y - 1:
                        last_y = y
                    else:
                        new_bottom_y = y
                        break
                else:
                    if y == bottom_y:
                        hit = True
                        last_y = y
        return new_bottom_y

    def _tune_left_border(self, left_x, x_projections_of_chunks):
        hit = False
        last_x = 0
        new_left_x = left_x
        for x in x_projections_of_chunks[::-1]:
            if hit:
                if x == last_x - 1:
                    last_x = x
                else:
                    new_left_x = x
                    break
            else:
                if x == left_x:
                    hit = True
                    last_x = x
        return new_left_x

    def _tune_right_border(self, right_x, x_projections_of_chunks):
        hit = False
        last_x = 0
        new_right_x = right_x
        for x in x_projections_of_chunks:
            if hit:
                if x == last_x + 1:
                    last_x = x
                else:
                    new_right_x = x
                    break
            else:
                if x == right_x:
                    hit = True
                    last_x = x
        return new_right_x
