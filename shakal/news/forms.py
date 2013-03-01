# -*- coding: utf-8 -*-

from django import forms
from django.contrib.comments.forms import COMMENT_MAX_LENGTH
from antispam.forms import AntispamModelFormMixin
from html_editor.fields import HtmlField
from models import News

class NewsForm(AntispamModelFormMixin, forms.ModelForm):
	short_text = HtmlField(label = u'Krátky text', max_length = COMMENT_MAX_LENGTH)
	long_text = HtmlField(label = u'Dlhý text', max_length = COMMENT_MAX_LENGTH)

	def __init__(self, *args, **kwargs):
		logged = kwargs.pop('logged', False)
		request = kwargs.pop('request')
		super(NewsForm, self).__init__(*args, **kwargs)
		if logged:
			del(self.fields['authors_name'])
			del(self.fields['captcha'])
		self.process_antispam(request)

	class Meta:
		model = News
		exclude = ('author', 'created', 'approved', )
		fields = ('title', 'authors_name', 'short_text', 'long_text', )
