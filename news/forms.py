# -*- coding: utf-8 -*-
from django import forms

from .models import News
from antispam.forms import AntispamFormMixin
from attachment.forms import AttachmentFormMixin
from common_utils.forms import AuthorsNameFormMixin, SetRequiredFieldsMixin
from common_utils.widgets import DescriptionRadioSelect


EDITABLE_FIELDS = (
	'title',
	'category',
	'source',
	'source_url',
	'original_short_text',
	'original_long_text',
	'event_date',
)


class NewsChangeForm(SetRequiredFieldsMixin, AttachmentFormMixin, forms.ModelForm):
	required_fields = {
		'original_long_text': False
	}

	def get_model(self):
		return News

	def clean(self):
		cleaned_data = super(NewsChangeForm, self).clean()
		long_text = cleaned_data.get('original_long_text')
		if long_text is None or long_text.field_text == '':
			if 'original_short_text' in cleaned_data:
				cleaned_data['original_long_text'] = cleaned_data['original_short_text']
		return cleaned_data

	class Meta:
		model = News
		fields = EDITABLE_FIELDS
		widgets = {'category': DescriptionRadioSelect()}


class NewsForm(AntispamFormMixin, AuthorsNameFormMixin, NewsChangeForm):
	class Meta:
		model = News
		fields = ('authors_name',) + EDITABLE_FIELDS
		widgets = {'category': DescriptionRadioSelect()}
