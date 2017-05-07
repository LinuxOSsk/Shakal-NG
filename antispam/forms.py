# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import operator

import random

from antispam.fields import AntispamField
from web.middlewares.threadlocal import get_current_request


class AntispamFormMixin(object):
	def __init__(self, *args, **kwargs):
		super(AntispamFormMixin, self).__init__(*args, **kwargs)
		request = get_current_request()
		if not request.user.is_authenticated():
			self.fields['captcha'] = AntispamField(required=True)
			self.process_antispam(get_current_request())

	def generate_antispam(self):
		operators = (
			('+', operator.add, operator.sub, False),
			('-', operator.sub, operator.add, True),
			('/', operator.div, operator.mul, True),
			('*', operator.mul, operator.div, False),
		)

		sign, operation, inverse_operation, answer_first = random.choice(operators)

		answer = random.randrange(1, 10)
		num_2 = random.randrange(1, 10)
		num_1 = inverse_operation(num_2, answer) if answer_first else random.randrange(1, 10)
		answer = operation(num_1, num_2)
		return ("{0} {1} {2} plus tisíc (číslom) ".format(num_1, sign, num_2), unicode(answer + 1000))

	def process_antispam(self, request):
		if request.method == 'GET' or not 'antispam' in request.session:
			request.session['antispam'] = self.generate_antispam()
		self.set_antispam_widget_attributes(request.session['antispam'])

	def set_antispam_widget_attributes(self, antispam):
		if 'captcha' in self.fields:
			self.fields['captcha'].widget.attrs['question'] = antispam[0]
			self.fields['captcha'].widget.attrs['answer'] = antispam[1]
