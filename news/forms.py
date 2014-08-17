# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings

from antispam.forms import AntispamFormMixin
from common_utils import get_meta
from models import News
from rich_editor.forms import RichOriginalField


COMMENT_MAX_LENGTH = getattr(settings, 'COMMENT_MAX_LENGTH', 3000)


class NewsForm(AntispamFormMixin, forms.ModelForm):
	original_short_text = RichOriginalField(get_meta(News).get_field('original_short_text').parsers, label = u'Krátky text', max_length = COMMENT_MAX_LENGTH)
	original_long_text = RichOriginalField(get_meta(News).get_field('original_long_text').parsers, label = u'Dlhý text', max_length = COMMENT_MAX_LENGTH)

	def __init__(self, *args, **kwargs):
		logged = kwargs.pop('logged', False)
		super(NewsForm, self).__init__(*args, **kwargs)
		if logged:
			del(self.fields['authors_name'])
			del(self.fields['captcha'])

	class Meta:
		model = News
		exclude = ('author', 'created', 'approved', )
		fields = ('title', 'authors_name', 'original_short_text', 'original_long_text', )
