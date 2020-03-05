# -*- coding: utf-8 -*-
# email: zhoubingcheng@datagrand.com
# create  : 2018/11/16
import re

ch_pattern = re.compile(ur'[\u4e00-\u9fa5、。？！，（）：“”；《》]')


class LineText(object):

	def __init__(self, text_chunks):
		assert len(text_chunks) > 0
		self._text_chunks = text_chunks

	@property
	def page(self):
		return self._text_chunks[0].page

	@property
	def y(self):
		return self._text_chunks[0].y

	@property
	def height(self):
		ch_heights = [text_chunk.height for text_chunk in self._text_chunks if ch_pattern.search(text_chunk.str)]
		if len(ch_heights) > 0:
			return max(ch_heights)
		else:
			return max(map(lambda t:t.height, self._text_chunks))

	@property
	def text(self):
		return u''.join(map(lambda t:t.str, self._text_chunks))

	def is_same_line(self, other):
		if self.page == other.page and self.y == other.y and self.height == other.height:
			return True
		return False
