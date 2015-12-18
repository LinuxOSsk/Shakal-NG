# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from .models import News
from antispam.forms import AntispamFormMixin
from common_utils.forms import AuthorsNameFormMixin, SetRequiredFieldsMixin
from common_utils.widgets import DescriptionRadioSelect


class NewsChangeForm(SetRequiredFieldsMixin, forms.ModelForm):
	required_fields = {
		'original_long_text': False
	}

	class Meta:
		model = News
		fields = (
			'title',
			'category',
			'source',
			'source_url',
			'original_short_text',
			'original_long_text',
		)
		widgets = {'category': DescriptionRadioSelect()}

	def clean(self):
		cleaned_data = super(NewsChangeForm, self).clean()
		long_text = cleaned_data.get('original_long_text')
		if long_text is None or long_text.field_text == '':
			if 'original_short_text' in cleaned_data:
				cleaned_data['original_long_text'] = cleaned_data['original_short_text']
		return cleaned_data


class NewsForm(AntispamFormMixin, AuthorsNameFormMixin, NewsChangeForm):
	class Meta:
		model = News
		fields = (
			'title',
			'authors_name',
			'category',
			'source',
			'source_url',
			'original_short_text',
			'original_long_text',
		)
		widgets = {'category': DescriptionRadioSelect()}
