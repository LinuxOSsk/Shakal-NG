# -*- coding: utf-8 -*-
from django.utils.encoding import force_str
from django.utils.termcolors import colorize


class AbstractTablePrinter(object):
	def __init__(self, data, *args, **kwargs):
		super(AbstractTablePrinter, self).__init__(*args, **kwargs)
		self.data = data

	CHARS = {
		'top': '═',
		'top-mid': '╤',
		'top-left': '╔',
		'top-right': '╗',
		'bottom': '═',
		'bottom-mid': '╧',
		'bottom-left': '╚',
		'bottom-right': '╝',
		'left': '║',
		'left-mid': '╟',
		'mid': '─',
		'mid-mid': '┼',
		'right': '║',
		'right-mid': '╢',
		'middle': '│'
	}

	def get_row_lengths(self, header, data):
		if header is None:
			if data:
				row_lengths = [0] * len(data[0])
			else:
				row_lengths = None
		else:
			row_lengths = [0] * len(header)
			for i, col in enumerate(header):
				row_lengths[i] = max(len(col), row_lengths[i])
		for row in data:
			for i, col in enumerate(row):
				row_lengths[i] = max(len(force_str(col)), row_lengths[i])
		return row_lengths

	def fill(self, row_lengths, padchar, left, mid, right): #pylint: disable=too-many-arguments
		if row_lengths is None:
			return ''
		txt = [padchar * (l + 2) for l in row_lengths]
		return ''.join([left, mid.join(txt), right])

	def render_col(self, col, maxlength):
		adjusted = col.ljust(maxlength, str(' '))[:maxlength]
		if hasattr(col, 'colorize_opts'):
			adjusted = colorize(adjusted, **col.colorize_opts)
		return adjusted

	def printrow(self, row, row_lengths, left, mid, right): #pylint: disable=too-many-arguments
		txt = [' ' + self.render_col(force_str(c), row_lengths[i]) + ' ' for i, c in enumerate(row)]
		return ''.join([left, mid.join(txt), right])

	def render(self):
		header = self.get_header()
		data = self.get_data()
		row_lengths = self.get_row_lengths(header, data)

		rows = []
		rows.append(self.fill(row_lengths, self.CHARS['top'], self.CHARS['top-left'], self.CHARS['top-mid'], self.CHARS['top-right']))
		if header is not None:
			rows.append(self.printrow(header, row_lengths, self.CHARS['left'], self.CHARS['middle'], self.CHARS['right']))
			rows.append(self.fill(row_lengths, self.CHARS['mid'], self.CHARS['left-mid'], self.CHARS['mid-mid'], self.CHARS['right-mid']))

		for row in data:
			rows.append(self.printrow(row, row_lengths, self.CHARS['left'], self.CHARS['middle'], self.CHARS['right']))
		rows.append(self.fill(row_lengths, self.CHARS['bottom'], self.CHARS['bottom-left'], self.CHARS['bottom-mid'], self.CHARS['bottom-right']))

		return '\n'.join(rows)

	def get_header(self):
		raise NotImplementedError

	def get_data(self):
		raise NotImplementedError

	def __str__(self):
		return self.render().encode('utf-8')


class NamedtupleTablePrinter(AbstractTablePrinter):
	def __init__(self, data, namedtuple_instance, columns=None, *args, **kwargs):
		super(NamedtupleTablePrinter, self).__init__(data, *args, **kwargs)
		self.namedtuple_instance = namedtuple_instance
		self.columns = columns

	def get_header(self):
		if self.columns is None:
			return self.namedtuple_instance._fields
		else:
			return self.columns

	def get_data(self):
		if self.columns is None:
			return [list(r) for r in self.data]
		else:
			return [[getattr(r, c) for c in self.columns] for r in self.data]


class DictTablePrinter(AbstractTablePrinter):
	def get_header(self):
		return None

	def get_data(self):
		return list(self.data.items())


class colored_unicode(str):
	def __init__(self, value, **kwargs):
		super(colored_unicode, self).__init__(value)
		self.colorize_opts = kwargs

	def __new__(cls, value, **kwargs):
		return super(colored_unicode, cls).__new__(cls, value)
