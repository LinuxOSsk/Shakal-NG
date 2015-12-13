# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from .models import News
from antispam.forms import AntispamFormMixin
from common_utils.forms import AuthorsNameFormMixin


class NewsForm(AntispamFormMixin, AuthorsNameFormMixin, forms.ModelForm):
	class Meta:
		model = News
		fields = (
			'title',
			'authors_name',
			'source',
			'source_url',
			'original_short_text',
			'original_long_text',
		)
