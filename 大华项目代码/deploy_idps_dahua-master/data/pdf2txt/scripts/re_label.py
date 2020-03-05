# coding=utf-8
# email:  lihanqing@datagrand.com
# create: 2018/11/13-2:17 PM
from line import LineText


def run(data, thre=1.0):
	line_combined_text_chunks = data.get('line_combined_text_chunks', [])
	predict_label = data.get('predict_label', [])
	pre_line = None
	for i, text_chunks in enumerate(line_combined_text_chunks):
		label = predict_label[i]
		line = LineText(text_chunks)
		if pre_line is not None and 1 <= i < len(predict_label) - 1:
			assert isinstance(pre_line, LineText)
			p_label = predict_label[i - 1]
			n_label = predict_label[i + 1]
			if label in 'ME' and abs(line.height - pre_line.height) > thre:
				if p_label == 'M':
					predict_label[i - 1] = u'E'
				else:
					predict_label[i - 1] = u'S'
				if n_label in 'BS':
					predict_label[i] = u'S'
				else:
					predict_label[i] = u'B'
			elif label in 'BS' and line.is_same_line(pre_line):
				assert label in 'BS'
				if p_label == 'S':
					predict_label[i - 1] = u'B'
				else:
					predict_label[i - 1] = u'M'
				if n_label in 'BS':
					predict_label[i] = u'E'
				else:
					predict_label[i] = u'M'
		pre_line = line
	return predict_label
