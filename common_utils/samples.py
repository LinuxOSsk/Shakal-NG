# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_sample_generator import samples


class LongHtmlGenerator(samples.LongTextSample):
	def get_sample(self):
		sample = super(LongHtmlGenerator, self).get_sample()
		return ''.join('<p>' + r + '</p>' for r in sample.split('\n'))
