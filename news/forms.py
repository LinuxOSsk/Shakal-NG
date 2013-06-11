# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings

from antispam.forms import AntispamModelFormMixin
from models import News
from rich_editor.forms import RichOriginalField


COMMENT_MAX_LENGTH = getattr(settings, 'COMMENT_MAX_LENGTH', 3000)


class NewsForm(AntispamModelFormMixin, forms.ModelForm):
	original_short_text = RichOriginalField(News._meta.get_field('original_short_text').parsers, label = u'Krátky text', max_length = COMMENT_MAX_LENGTH, js = True)
	original_long_text = RichOriginalField(News._meta.get_field('original_long_text').parsers, label = u'Dlhý text', max_length = COMMENT_MAX_LENGTH, js = True)

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
		fields = ('title', 'authors_name', 'original_short_text', 'original_long_text', )
