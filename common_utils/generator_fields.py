# -*- coding: utf-8 -*-
from django_sample_generator import functions
from django_sample_generator.fields import FunctionFieldGenerator


def gen_long_html(paragraph_count=None, max_length=None):
	sample = functions.gen_text_long(paragraph_count, max_length)
	return ''.join('<p>' + r + '</p>' for r in sample.split('\n'))


class NameFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_text_name


class SentenceFieldGenerator(FunctionFieldGenerator):
	function = functions.gen_text_sentence


class LongHtmlFieldGenerator(FunctionFieldGenerator):
	function = gen_long_html
