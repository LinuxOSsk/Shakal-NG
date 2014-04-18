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
			'perex': RichEditorWidget,
			'annotation': RichEditorWidget,
			'content': RichEditorWidget,
		}
