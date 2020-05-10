# -*- coding: utf-8 -*-
from django import forms

from .models import Article
from common_utils.admin_widgets import RichEditorWidget, EnclosedInput


class ArticleForm(forms.ModelForm):
	class Meta:
		model = Article
		widgets = {
			'authors_name': EnclosedInput(append='fa-user'),
			'original_perex': RichEditorWidget(formats=()),
			'original_annotation': RichEditorWidget(formats=()),
			'original_content': RichEditorWidget(formats=()),
		}
		fields = '__all__'
