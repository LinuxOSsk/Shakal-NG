# -*- coding: utf-8 -*-
from django import forms

from .models import Article
from common_utils.admin_widgets import DateTimeInput, RichEditorWidget, EnclosedInput


class ArticleForm(forms.ModelForm):
	class Meta:
		model = Article
		widgets = {
			'pub_time':  DateTimeInput,
			'authors_name': EnclosedInput(append='icon-user'),
			'original_perex': RichEditorWidget(formats=()),
			'original_annotation': RichEditorWidget(formats=()),
			'original_content': RichEditorWidget(formats=()),
		}
		fields = '__all__'
