# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.conf import settings

from .models import News
from antispam.forms import AntispamFormMixin
from common_utils import get_meta
from common_utils.forms import AuthorsNameFormMixin
from rich_editor.forms import RichOriginalField


NEWS_MAX_LENGTH = getattr(settings, 'NEWS_MAX_LENGTH', 3000)


class NewsForm(AntispamFormMixin, AuthorsNameFormMixin, forms.ModelForm):
	original_short_text = RichOriginalField(get_meta(News).get_field('original_short_text').parsers, label= u'Krátky text', max_length= NEWS_MAX_LENGTH)
	original_long_text = RichOriginalField(get_meta(News).get_field('original_long_text').parsers, label= u'Dlhý text')

	class Meta:
		model = News
		exclude = ('author', 'created', 'approved', )
		fields = ('title', 'authors_name', 'original_short_text', 'original_long_text', )
